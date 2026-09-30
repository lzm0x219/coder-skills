/** 编译期调用点；jobs/JobId 暂定，公共 API 只有声明、没有运行时实现。 */
import {
  FileFlowClient,
  FileFlowError,
  parseJobId,
  type FileId,
  type JobId,
} from "./fileflow-sdk.api.js";

export async function processFile(
  pdf: Uint8Array,
  token: () => Promise<string>,
  uploadKey: string,
  startKey: string,
  write: (chunk: Uint8Array) => Promise<void>,
): Promise<JobId> {
  const client = new FileFlowClient({
    endpoint: "https://api.fileflow.example",
    credential: { getToken: () => token() },
  });
  const uploaded = await client.files.upload({
    filename: "report.pdf",
    mediaType: "application/pdf",
    bytes: pdf,
    idempotencyKey: uploadKey,
  });
  const started = await client.jobs.startTextExtraction({
    sourceFileId: uploaded.data.id,
    idempotencyKey: startKey,
  });
  const finished = await client.jobs.waitForCompletion(started.data.id);
  if (finished.data.state === "failed") throw new Error(finished.data.failure.message);
  if (finished.data.state === "cancelled") throw new Error("任务已取消");

  const download = await client.files.openDownload(finished.data.outputFileId);
  let transferFailed = false;
  let transferError: unknown;
  try {
    for await (const chunk of download.data.chunks) await write(chunk);
  } catch (error) {
    transferFailed = true;
    transferError = error;
  }
  try {
    await download.data.close();
  } catch (closeError) {
    if (transferFailed) throw new AggregateError([transferError, closeError], "传输与关闭均失败");
    throw closeError;
  }
  if (transferFailed) throw transferError;
  return finished.data.id;
}

export async function resumeOrCancel(client: FileFlowClient, savedJobId: string) {
  const id = parseJobId(savedJobId);
  const current = await client.jobs.get(id);
  if (current.data.state === "running") return client.jobs.cancel(id);
  return current;
}

export async function nextFailedPage(client: FileFlowClient, cursor?: string) {
  return client.jobs.listPage({ state: "failed", pageSize: 50, cursor });
}

export async function retryStartAfterUnknown(
  client: FileFlowClient,
  sourceFileId: FileId,
  savedKey: string,
) {
  const input = { sourceFileId, idempotencyKey: savedKey };
  try {
    return await client.jobs.startTextExtraction(input);
  } catch (error) {
    if (error instanceof FileFlowError && error.code === "outcome_unknown") {
      return client.jobs.startTextExtraction(input);
    }
    throw error;
  }
}

function checkIdDistinction(client: FileFlowClient, id: JobId) {
  // @ts-expect-error 任务 ID 不可当作文件 ID 使用。
  void client.files.openDownload(id);
}
