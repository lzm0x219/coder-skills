/** 候选公开声明：AWS SDK v3 S3Client 由调用方配置并持有。 */
import type { S3Client } from "@aws-sdk/client-s3";

export type UploadErrorCode =
  | "invalid_input"
  | "part_in_flight"
  | "parts_in_flight"
  | "completion_conflict"
  | "object_exists"
  | "invalid_part"
  | "permission_denied"
  | "remote_rejected"
  | "transport_failure"
  | "outcome_unknown";

export type UploadOperation = "create" | "fromCheckpoint" | "uploadPart" | "complete" | "abort";

export declare class UploadError extends Error {
  readonly code: UploadErrorCode;
  readonly operation: UploadOperation;
  readonly requestId?: string;
}

export interface PartReceipt {
  readonly uploadId: string;
  readonly number: number;
  readonly etag: string;
  readonly sizeBytes: number;
}

export interface UploadCheckpoint {
  readonly bucket: string;
  readonly key: string;
  readonly uploadId: string;
  readonly parts: readonly PartReceipt[];
}

export interface CompletedObject {
  readonly bucket: string;
  readonly key: string;
  readonly etag: string;
}

export interface MultipartUploadSession {
  readonly uploadId: string;
  uploadPart(input: {
    readonly number: number;
    readonly bytes: Uint8Array;
    readonly signal?: AbortSignal;
  }): Promise<PartReceipt>;
  checkpoint(): UploadCheckpoint;
  complete(input: {
    readonly overwrite: "forbid" | "allow";
    readonly signal?: AbortSignal;
  }): Promise<CompletedObject>;
  abort(input?: { readonly signal?: AbortSignal }): Promise<void>;
}

export interface MultipartUploads {
  create(input: {
    readonly bucket: string;
    readonly key: string;
    readonly signal?: AbortSignal;
  }): Promise<MultipartUploadSession>;
  fromCheckpoint(checkpoint: UploadCheckpoint): MultipartUploadSession;
}

/** 本地创建包装层；不发起远端上传，也不取得 s3 的关闭权。 */
export declare function createMultipartUploads(s3: S3Client): MultipartUploads;
