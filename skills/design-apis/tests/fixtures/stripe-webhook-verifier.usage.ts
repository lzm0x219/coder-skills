/** 候选接口的编译期调用点；不包含 HTTP server 或验签实现。 */
import {
  createWebhookVerifier,
  VerifyError,
  type VerifiedSnapshotEvent,
  type WebhookVerifier,
} from "./stripe-webhook-verifier.api.js";

export interface IncomingWebhook {
  readonly rawBody: Uint8Array;
  readonly signatureHeader: string | undefined;
}

export type PersistOnce = (event: VerifiedSnapshotEvent) => Promise<"inserted" | "duplicate">;
export type Respond = (status: 200 | 400 | 413 | 500) => void;

export async function receiveWebhook(
  verifier: WebhookVerifier,
  request: IncomingWebhook,
  persistOnce: PersistOnce,
  respond: Respond,
): Promise<void> {
  if (request.signatureHeader === undefined) {
    respond(400);
    return;
  }

  let event: VerifiedSnapshotEvent;
  try {
    event = verifier.verify({
      rawBody: request.rawBody,
      signatureHeader: request.signatureHeader,
    });
  } catch (error) {
    if (error instanceof VerifyError) {
      respond(error.code === "payload_too_large" ? 413 : 400);
      return;
    }
    respond(500);
    return;
  }

  try {
    await persistOnce(event); // 事件 ID 持久去重由调用方实现。
    respond(200); // 已可靠接收；业务处理仍可在队列中进行。
  } catch {
    respond(500); // 持久接收失败，等待提供方重试。
  }
}

export function configureVerifier(secrets: readonly string[], live: boolean): WebhookVerifier {
  return createWebhookVerifier({
    secrets,
    expectedLivemode: live,
    maxBodyBytes: 1_048_576, // 本应用选择；不是 Stripe 通用上限。
  });
}

function rejectParsedBody(verifier: WebhookVerifier) {
  // @ts-expect-error 验签入口只接受原始字节。
  verifier.verify({ rawBody: { id: "evt_example" }, signatureHeader: "t=...,v1=..." });
}
