/** 候选公开声明：仅供 API 设计评审，尚无运行时实现。 */

export type VerifyErrorCode =
  | "invalid_config"
  | "payload_too_large"
  | "invalid_signature"
  | "timestamp_out_of_range"
  | "invalid_payload"
  | "unexpected_mode";

export declare class VerifyError extends Error {
  readonly code: VerifyErrorCode;
}

export interface VerifiedSnapshotEvent {
  readonly id: string;
  readonly type: string;
  /** Unix 秒。 */
  readonly created: number;
  /** 事件数据创建时的服务版本；null 不表示当前版本。 */
  readonly apiVersion: string | null;
  readonly livemode: boolean;
  readonly data: { readonly object: unknown };
}

export interface VerifyInput {
  /** HTTP 框架修改或解析前的原始 body 字节。 */
  readonly rawBody: Uint8Array;
  readonly signatureHeader: string;
  /** 仅供确定性测试；生产调用省略以使用系统时钟。 */
  readonly nowSeconds?: number;
}

export interface WebhookVerifier {
  verify(input: VerifyInput): VerifiedSnapshotEvent;
}

export interface WebhookVerifierConfig {
  /** 同一 endpoint、同一 test/live 环境的一组当前有效密钥。 */
  readonly secrets: readonly string[];
  readonly expectedLivemode: boolean;
  /** 默认 300 秒；必须大于零。 */
  readonly toleranceSeconds?: number;
  /** 正整数；应用负责在读取请求体时也限制大小。 */
  readonly maxBodyBytes: number;
}

export declare function createWebhookVerifier(
  config: WebhookVerifierConfig,
): WebhookVerifier;
