"use strict";

const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const Ajv = require("ajv");
const Ajv2020 = require("ajv/dist/2020");
const addFormats = require("ajv-formats");

const fixtures = process.argv[2];
if (!fixtures) throw new Error("usage: node verify_events_webhooks.cjs <fixture-root>");
const read = (branch, name) => fs.readFileSync(path.join(fixtures, branch, name));
const json = (branch, name) => JSON.parse(read(branch, name).toString("utf8"));

function eventFixtures() {
  const branch = "events-order";
  const officialSchema = json(branch, "cloudevents-v1.0.2.schema.json");
  const ceAjv = new Ajv({ allErrors: true, strict: false });
  addFormats(ceAjv);
  const validateCloudEvent = ceAjv.compile(officialSchema);
  const profileAjv = new Ajv2020({ allErrors: true });
  addFormats(profileAjv);
  profileAjv.addSchema(json(branch, "consumer-v1.schema.json"));
  const validateProfile = profileAjv.compile(json(branch, "event.schema.json"));

  const valid = json(branch, "valid.json");
  assert.equal(validateCloudEvent(valid), true, JSON.stringify(validateCloudEvent.errors));
  assert.equal(validateProfile(valid), true, JSON.stringify(validateProfile.errors));
  assert.match(valid.source, /^https:\/\//, "fixture source is an absolute URI");
  assert.equal(valid.datacontenttype, "application/json");

  const invalid = json(branch, "invalid.json");
  assert.equal(validateCloudEvent(invalid), false, "official CloudEvents schema rejects invalid URI-reference");
  assert.equal(validateProfile(invalid), false, "project event profile rejects invalid URI-reference");
  assert.ok(validateCloudEvent.errors.some(error => error.instancePath === "" && error.keyword === "required"));
  const invalidSource = json(branch, "invalid-source.json");
  assert.equal(validateCloudEvent(invalidSource), false, "official CloudEvents schema rejects malformed source URI-reference");
  assert.equal(validateProfile(invalidSource), false, "project event profile rejects malformed source URI-reference");

  const additive = json(branch, "candidate-additive.json");
  assert.equal(validateCloudEvent(additive), true, JSON.stringify(validateCloudEvent.errors));
  assert.equal(validateProfile(additive), true, JSON.stringify(validateProfile.errors));
  const oldConsumer = profileAjv.getSchema("https://schemas.example.test/events/order-created-v1.json");
  assert.ok(oldConsumer);
  assert.equal(oldConsumer(additive.data), true, "old consumer tolerates additive optional data");

  const breaking = json(branch, "candidate-breaking.json");
  assert.equal(validateCloudEvent(breaking), true, "CloudEvents envelope can be valid while payload contract breaks");
  assert.equal(oldConsumer(breaking.data), false, "old consumer rejects removal of required revision");

  const delivery = json(branch, "delivery-cases.json");
  assert.equal(delivery.guarantee, "at-least-once");
  assert.equal(delivery.orderingScope, "per-order partition key");
  assert.equal(delivery.retry.transient.maxAttempts, 5);
  assert.equal(delivery.replay.retentionDays, 30);
  const simulateRevisions = revisions => {
    let current = 0;
    const parked = new Map();
    for (const revision of revisions) {
      if (revision <= current) continue;
      parked.set(revision, true);
      while (parked.has(current + 1)) {
        current += 1;
        parked.delete(current);
      }
    }
    return current;
  };
  for (const sequence of delivery.sequences) {
    const finalRevision = simulateRevisions(sequence.revisions);
    assert.equal(finalRevision, sequence.expectedRevision, sequence.name);
    if (sequence.parkForReconciliation) assert.equal(sequence.expectedRevision, 1, sequence.name);
  }
  console.log("PASS events: CloudEvents v1.0.2 official schema, source URI, content type, consumer evolution and delivery-policy cases");
}

function hmacSha256(key, bytes, encoding) {
  return crypto.createHmac("sha256", key).update(bytes).digest(encoding);
}

function safeEqualText(left, right) {
  const a = Buffer.from(left, "utf8");
  const b = Buffer.from(right, "utf8");
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function githubFixtures() {
  const vector = json("webhook-github", "github-hmac-vector.json");
  const computed = hmacSha256(Buffer.from(vector.secret, "utf8"), Buffer.from(vector.payload, "utf8"), "hex");
  assert.equal(computed, vector.signature.slice("sha256=".length), "GitHub published HMAC-SHA256 vector");

  const rawBody = read("webhook-github", "payload.json");
  const localSecret = Buffer.from("fixture secret only", "utf8");
  const bodySignature = `sha256=${hmacSha256(localSecret, rawBody, "hex")}`;
  const receive = (body, headers) => safeEqualText(
    headers["X-Hub-Signature-256"],
    `sha256=${hmacSha256(localSecret, body, "hex")}`,
  );
  const headers = { "X-Hub-Signature-256": bodySignature, "X-GitHub-Delivery": "delivery-42" };
  assert.equal(receive(rawBody, headers), true);
  assert.equal(receive(Buffer.from(rawBody.toString("utf8").replace("opened", "closed")), headers), false);
  // GitHub's documented HMAC signs payload bytes only; the delivery header is outside this authentication input.
  assert.equal(receive(rawBody, { ...headers, "X-GitHub-Delivery": "delivery-forged" }), true,
    "changing X-GitHub-Delivery does not alter body-only signature verification");
  console.log("PASS GitHub receiver: official HMAC vector, raw bytes and unsigned delivery-header boundary");
}

function standardWebhookSenderFixtures() {
  const contract = json("webhook-github", "sender-contract.json");
  const body = Buffer.from(contract.rawBody, "utf8");
  const signingInput = Buffer.from(`${contract.eventId}.${contract.timestamp}.${body.toString("utf8")}`, "utf8");
  assert.equal(signingInput.toString("utf8"), contract.signatureInput);

  const currentKey = Buffer.from(contract.secretBase64, "base64");
  const previousKey = Buffer.from(contract.previousSecretBase64, "base64");
  assert.ok(currentKey.length >= 24, "Standard Webhooks symmetric key guidance is >= 24 bytes");
  assert.ok(previousKey.length >= 24);
  const sign = key => `v1,${hmacSha256(key, signingInput, "base64")}`;
  const signatures = contract.headers["webhook-signature"].split(" ");
  assert.equal(sign(currentKey), signatures[0], "pinned self-owned sender vector with current key");
  assert.equal(sign(previousKey), signatures[1], "pinned rotation overlap vector with previous key");

  const verify = (payload, headers, trustedKeys, nowSeconds, toleranceSeconds = 300) => {
    const id = headers["webhook-id"];
    const timestampText = headers["webhook-timestamp"];
    const timestamp = Number(timestampText);
    if (!id || id.includes(".") || !Number.isSafeInteger(timestamp)) return false;
    if (Math.abs(nowSeconds - timestamp) > toleranceSeconds) return false;
    const signed = Buffer.from(`${id}.${timestampText}.${payload.toString("utf8")}`, "utf8");
    const provided = (headers["webhook-signature"] || "").split(" ");
    return trustedKeys.some(key => provided.some(token => {
      const separator = token.indexOf(",");
      if (separator < 0 || token.slice(0, separator) !== "v1") return false;
      const supplied = token.slice(separator + 1);
      const expected = hmacSha256(key, signed, "base64");
      return safeEqualText(supplied, expected);
    }));
  };
  const headers = contract.headers;
  const now = contract.timestamp;
  assert.equal(verify(body, headers, [currentKey, previousKey], now), true, "rotation overlap accepts either trusted key");
  assert.equal(verify(body, headers, [currentKey], now), true, "retired endpoint can finish rotation on current key");
  assert.equal(verify(body, headers, [Buffer.alloc(32, 0x7a)], now), false, "untrusted key rejected");
  assert.equal(verify(Buffer.from(`${contract.rawBody} `), headers, [currentKey, previousKey], now), false, "raw body whitespace mutation rejected");
  assert.equal(verify(body, { ...headers, "webhook-id": `${contract.eventId}-changed` }, [currentKey, previousKey], now), false, "event ID is signed");
  assert.equal(verify(body, { ...headers, "webhook-timestamp": String(contract.timestamp + 1) }, [currentKey, previousKey], now), false, "attempt timestamp is signed");
  assert.equal(verify(body, headers, [currentKey, previousKey], now + 300), true, "freshness window boundary accepted");
  assert.equal(verify(body, headers, [currentKey, previousKey], now + 301), false, "stale replay rejected");

  const policy = contract.deliveryPolicy;
  assert.equal(policy["2xx"], "confirmed");
  assert.equal(policy["3xx"], "failed; do not follow redirect");
  assert.equal(policy["410"], "disable endpoint");
  assert.equal(policy.retryLimit, 8);
  assert.equal(policy.replayIdStable, true);
  assert.equal(policy.attemptTimestampChanges, true);
  console.log("PASS sender: Standard Webhooks 1.0.0-inspired signing, key rotation, freshness and delivery matrix");
}

eventFixtures();
githubFixtures();
standardWebhookSenderFixtures();
