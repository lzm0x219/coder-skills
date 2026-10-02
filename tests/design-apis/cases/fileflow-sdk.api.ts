/** FileFlow: 虚构服务的 TypeScript SDK 草案；jobs/JobId 暂定，命名评审未通过。 */

declare const fileIdBrand: unique symbol;
declare const jobIdBrand: unique symbol;

export type FileId = string & { readonly [fileIdBrand]: true };
export type JobId = string & { readonly [jobIdBrand]: true };

/** 从持久化值恢复 ID；格式不合法时抛出 invalid_input。 */
export declare function parseFileId(value: string): FileId;
export declare function parseJobId(value: string): JobId;

export interface CredentialProvider {
  /** 每次尝试开始时调用；signal 在调用方取消或尝试/总预算超时时触发。 */
  getToken(context: { readonly signal: AbortSignal }): Promise<string>;
}

export interface RetryOptions {
  /** 总尝试次数，包含首次请求；默认 3，范围 1..5。 */
  readonly maxAttempts?: number;
  /** 含取凭据、传输和退避的总预算；默认 20_000。wait 的每次轮询分别计算。 */
  readonly maxElapsedMs?: number;
}

export interface ClientOptions {
  readonly endpoint: string;
  readonly credential: CredentialProvider;
  /** 从取凭据到响应或下载句柄的单次尝试超时；默认 10_000。 */
  readonly requestTimeoutMs?: number;
  readonly retry?: RetryOptions;
  /** 可信的替代传输，仅在确需自定义传输或离线测试时提供。 */
  readonly fetch?: typeof globalThis.fetch;
}

export interface RequestOptions {
  readonly signal?: AbortSignal;
}

export interface ResponseMeta {
  readonly requestId: string;
  readonly rateLimitRemaining?: number;
}

export interface ApiResponse<T> {
  readonly data: T;
  readonly meta: ResponseMeta;
}

export type InputMediaType = "application/pdf" | "text/plain";

export interface StoredFile {
  readonly id: FileId;
  readonly filename: string;
  readonly mediaType: string;
  readonly sizeBytes: number;
  /** RFC 3339 UTC 时间。 */
  readonly createdAt: string;
  readonly expiresAt: string;
}

export interface UploadInput {
  readonly filename: string;
  readonly mediaType: InputMediaType;
  /** 1..16 MiB；SDK 在调用时复制，确保并发修改不影响重试。 */
  readonly bytes: Uint8Array;
  /** 同一逻辑操作的所有尝试使用同一个键。 */
  readonly idempotencyKey: string;
}

export interface FileDownload {
  readonly mediaType: string;
  readonly sizeBytes: number;
  /** 单次消费；迭代结束或提前退出后仍须调用 close。 */
  readonly chunks: AsyncIterable<Uint8Array>;
  /** 必须显式调用；重复调用不重复清理，且返回同一次关闭的结果。 */
  close(): Promise<void>;
}

export interface FilesApi {
  upload(input: UploadInput, options?: RequestOptions): Promise<ApiResponse<StoredFile>>;
  openDownload(id: FileId, options?: RequestOptions): Promise<ApiResponse<FileDownload>>;
}

export interface StartTextExtractionInput {
  readonly sourceFileId: FileId;
  readonly idempotencyKey: string;
}

export interface JobBase {
  readonly id: JobId;
  readonly kind: "text-extraction";
  readonly sourceFileId: FileId;
  readonly createdAt: string;
  readonly updatedAt: string;
}

export type QueuedJob = JobBase & { readonly state: "queued" };
export type RunningJob = JobBase & {
  readonly state: "running";
  /** 0..100；服务未报告时缺失。 */
  readonly progressPercent?: number;
};
export type SucceededJob = JobBase & {
  readonly state: "succeeded";
  readonly outputFileId: FileId;
};
export type JobFailure =
  | { readonly code: "invalid_file" | "processing_failed"; readonly message: string }
  | { readonly code: "unknown"; readonly rawCode: string; readonly message: string };
export type FailedJob = JobBase & {
  readonly state: "failed";
  readonly failure: JobFailure;
};
export type CancelledJob = JobBase & { readonly state: "cancelled" };
export type UnknownJob = JobBase & {
  readonly state: "unknown";
  readonly rawState: string;
};
export type Job =
  | QueuedJob
  | RunningJob
  | SucceededJob
  | FailedJob
  | CancelledJob
  | UnknownJob;
export type TerminalJob =
  | SucceededJob
  | FailedJob
  | CancelledJob;

export interface WaitOptions extends RequestOptions {
  /** 本地等待预算，单位毫秒；默认 60_000，不取消远端任务。 */
  readonly timeoutMs?: number;
}

export interface ListJobsOptions {
  /** 默认 50，范围 1..200。 */
  readonly pageSize?: number;
  readonly cursor?: string;
  readonly state?: Exclude<Job["state"], "unknown">;
}

export interface Page<T> {
  readonly items: readonly T[];
  /** 末页时不存在；令牌不应被解析或修改。 */
  readonly nextCursor?: string;
}

export interface JobsApi {
  startTextExtraction(input: StartTextExtractionInput, options?: RequestOptions): Promise<ApiResponse<Job>>;
  get(id: JobId, options?: RequestOptions): Promise<ApiResponse<Job>>;
  waitForCompletion(
    id: JobId,
    options?: WaitOptions,
  ): Promise<ApiResponse<TerminalJob>>;
  /** 请求远端取消；返回状态不保证已经是 cancelled。 */
  cancel(id: JobId, options?: RequestOptions): Promise<ApiResponse<Job>>;
  listPage(
    options?: ListJobsOptions,
    requestOptions?: RequestOptions,
  ): Promise<ApiResponse<Page<Job>>>;
}

export type FileFlowErrorCode =
  | "invalid_input"
  | "credential_unavailable"
  | "unauthenticated"
  | "permission_denied"
  | "not_found"
  | "conflict"
  | "rate_limited"
  | "service_unavailable"
  | "transport_failure"
  | "aborted"
  | "wait_timeout"
  | "outcome_unknown"
  | "unsupported_service_state"
  | "download_closed";

export declare class FileFlowError extends Error {
  readonly code: FileFlowErrorCode;
  readonly requestId?: string;
  readonly retryAfterMs?: number;
}

/** 无后台资源；可并发复用，无需 close。 */
export declare class FileFlowClient {
  constructor(options: ClientOptions);
  readonly files: FilesApi;
  readonly jobs: JobsApi;
}
