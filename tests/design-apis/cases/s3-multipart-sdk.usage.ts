/** 候选接口的编译期调用点；不上传文件，也不创建 S3 客户端。 */
import type { S3Client } from "@aws-sdk/client-s3";
import {
  createMultipartUploads,
  UploadError,
  type CompletedObject,
  type MultipartUploads,
  type UploadCheckpoint,
} from "./s3-multipart-sdk.api.js";

export interface UploadParts {
  readonly first: Uint8Array; // 至少 5 MiB
  readonly last: Uint8Array;
}

export function bindS3Client(s3: S3Client): MultipartUploads {
  return createMultipartUploads(s3);
}

export async function uploadObject(
  uploads: MultipartUploads,
  parts: UploadParts,
  saveCheckpoint: (value: UploadCheckpoint) => Promise<void>,
  clearCheckpoint: (uploadId: string) => Promise<void>,
  flagForReconciliation: (value: UploadCheckpoint, error: UploadError) => Promise<void>,
): Promise<CompletedObject> {
  const session = await uploads.create({ bucket: "archive", key: "daily/a.bin" });
  let object: CompletedObject;
  try {
    await saveCheckpoint(session.checkpoint()); // 先持久保存 uploadId。
    const results = await Promise.allSettled([
      session.uploadPart({ number: 1, bytes: parts.first }),
      session.uploadPart({ number: 2, bytes: parts.last }),
    ]);
    const failed = results.find((result): result is PromiseRejectedResult => result.status === "rejected");
    if (failed) throw failed.reason;
    await saveCheckpoint(session.checkpoint()); // 保存最新 ETag 回执。
    object = await session.complete({ overwrite: "forbid" });
  } catch (error) {
    if (error instanceof UploadError && error.code === "outcome_unknown") {
      try {
        await flagForReconciliation(session.checkpoint(), error);
      } catch (recordError) {
        throw new AggregateError([error, recordError], "远端结果与核对记录均未确定");
      }
    } else {
      try {
        await session.abort();
      } catch (cleanupError) {
        throw new AggregateError([error, cleanupError], "上传与清理均失败");
      }
    }
    throw error;
  }
  await clearCheckpoint(session.uploadId); // 完成已确定；清理失败不触发远端 abort。
  return object;
}

export function resumeLocally(uploads: MultipartUploads, saved: UploadCheckpoint) {
  return uploads.fromCheckpoint(saved); // 仅重建句柄，不查询远端。
}

function requireExplicitOverwrite(uploads: MultipartUploads) {
  const session = uploads.fromCheckpoint({ bucket: "b", key: "k", uploadId: "u", parts: [] });
  // @ts-expect-error 覆盖策略必须在完成调用点显式给出。
  void session.complete({});
}
