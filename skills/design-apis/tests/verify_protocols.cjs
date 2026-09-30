"use strict";

const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const SwaggerParser = require("@apidevtools/swagger-parser");
const gql = require("graphql");
const protobuf = require("protobufjs");
const Ajv2020 = require("ajv/dist/2020");
const addFormats = require("ajv-formats");

const fixtures = process.argv[2];
const read = (branch, name) => fs.readFileSync(path.join(fixtures, branch, name));
const json = (branch, name) => JSON.parse(read(branch, name).toString("utf8"));

async function httpFixture() {
  const file = path.join(fixtures, "http-profile", "openapi.json");
  const api = await SwaggerParser.validate(file);
  assert.equal(api.openapi, "3.1.1");
  const put = api.paths["/profiles/{profileId}"].put;
  assert.equal(put.parameters.find(p => p.name.toLowerCase() === "if-match")?.required, true);
  assert.ok(put.responses["204"] && !put.responses["204"].content);
  for (const status of ["400", "403", "412"]) assert.ok(put.responses[status]);
  const examples = json("http-profile", "cases.json");
  const validateBody = new Ajv2020().compile(api.components.schemas.ProfileInput);
  const evaluate = request => {
    if (!request.headers.Authorization) return 403;
    if (!request.headers["If-Match"] || !validateBody(request.body)) return 400;
    if (request.headers["If-Match"] !== '"v7"') return 412;
    return 204;
  };
  for (const [name, request] of Object.entries(examples)) {
    assert.equal(request.method, "PUT", name);
    assert.equal(evaluate(request), request.expectedStatus, name);
  }
  assert.equal(examples.missingPrecondition.headers["If-Match"], undefined);
  console.log("PASS HTTP OpenAPI and request model (missing/stale preconditions rejected)");
}

async function graphqlFixture() {
  const branch = "graphql-order";
  const schema = gql.buildSchema(read(branch, "schema.graphql").toString("utf8"));
  assert.deepEqual(gql.validateSchema(schema), []);
  const oldQuery = gql.parse('{ order(id: "42") { id note legacyNote } }');
  assert.deepEqual(gql.validate(schema, oldQuery), []);
  const success = await gql.graphql({
    schema, source: '{ order(id: "42") { id note } }',
    rootValue: { order: () => ({ id: "42", note: "ready" }) },
  });
  assert.deepEqual(JSON.parse(JSON.stringify(success.data)), { order: { id: "42", note: "ready" } });
  assert.equal(success.errors, undefined);
  const rootValue = { order: () => ({ id: "42", legacyNote: "old", note: () => { throw new Error("note unavailable"); } }) };
  const partial = await gql.graphql({ schema, source: '{ order(id: "42") { id note } }', rootValue });
  assert.deepEqual(JSON.parse(JSON.stringify(partial.data)), { order: { id: "42", note: null } });
  assert.deepEqual(partial.errors[0].path, ["order", "note"]);
  const broken = gql.buildSchema(read(branch, "broken.graphql").toString("utf8"));
  assert.ok(gql.validate(broken, oldQuery).some(error => error.message.includes("legacyNote")));
  const bubbled = await gql.graphql({ schema: broken, source: '{ order(id: "42") { id note } }', rootValue });
  assert.deepEqual(JSON.parse(JSON.stringify(bubbled.data)), { order: null });
  assert.deepEqual(bubbled.errors[0].path, ["order", "note"]);
  console.log("PASS GraphQL old query and error propagation (breaking SDL rejected)");
}

function rpcFixture() {
  const branch = "rpc-profile";
  const parse = name => protobuf.parse(read(branch, name).toString("utf8")).root;
  const oldType = parse("v1.proto").lookupType("example.profile.v1.Profile");
  const nextType = parse("candidate.proto").lookupType("example.profile.v1.Profile");
  const brokenType = parse("broken.proto").lookupType("example.profile.v1.Profile");
  assert.equal(oldType.fields.legacyName.id, 2);
  assert.equal(nextType.fields.displayName.id, 3);
  assert.ok(nextType.reserved.some(range => range[0] <= 2 && range[1] >= 2));
  const oldWire = oldType.encode(oldType.create({ id: "42", legacyName: "old" })).finish();
  const nextRead = nextType.decode(oldWire);
  assert.equal(nextRead.id, "42");
  assert.equal(Object.hasOwn(nextRead, "displayName"), false);
  assert.equal(nextType.toObject(nextRead, { oneofs: true }).displayName, undefined);
  const newWire = nextType.encode(nextType.create({ id: "42", displayName: "new" })).finish();
  assert.equal(oldType.decode(newWire).id, "42");
  const oldNumbers = new Map(Object.values(oldType.fields).map(field => [field.id, field.name]));
  const reused = Object.values(brokenType.fields).some(field =>
    oldNumbers.has(field.id) && oldNumbers.get(field.id) !== field.name);
  assert.equal(reused, true, "the negative fixture must reuse a published number");
  assert.equal(Object.values(nextType.fields).some(field =>
    oldNumbers.has(field.id) && oldNumbers.get(field.id) !== field.name), false);
  console.log("PASS Proto parsing and binary compatibility model (number reuse rejected)");
}

function eventsFixture() {
  const branch = "events-order";
  const ajv = new Ajv2020({ allErrors: true });
  addFormats(ajv);
  const validate = ajv.compile(json(branch, "event.schema.json"));
  const valid = json(branch, "valid.json");
  assert.equal(validate(valid), true, JSON.stringify(validate.errors));
  const invalid = json(branch, "invalid.json");
  assert.equal(validate(invalid), false);
  assert.ok(validate.errors.some(error => error.keyword === "required" && error.params.missingProperty === "id"));
  const eventKey = event => `${event.source}\u0000${event.id}`;
  const seen = new Set();
  assert.equal(seen.has(eventKey(valid)), false);
  seen.add(eventKey(valid));
  assert.equal(seen.has(eventKey({ ...valid, data: { ...valid.data } })), true);
  assert.notEqual(eventKey(valid), eventKey({ ...valid, id: "evt-43" }));
  console.log("PASS CloudEvents-shaped event schema and dedup model (missing id rejected)");
}

function webhookFixture() {
  const raw = read("webhook-github", "payload.json");
  const secret = crypto.randomBytes(32);
  const signature = data => "sha256=" + crypto.createHmac("sha256", secret).update(data).digest("hex");
  const seen = new Set();
  const receive = (body, headers) => {
    const supplied = headers["X-Hub-Signature-256"];
    if (!supplied || !/^sha256=[a-f0-9]{64}$/.test(supplied)) return 401;
    const expected = Buffer.from(signature(body));
    const actual = Buffer.from(supplied);
    if (actual.length !== expected.length || !crypto.timingSafeEqual(actual, expected)) return 401;
    const delivery = headers["X-GitHub-Delivery"];
    if (!delivery) return 400;
    JSON.parse(body.toString("utf8"));
    if (seen.has(delivery)) return 200;
    seen.add(delivery); // Models durable receive; no database is exercised here.
    return 202;
  };
  const headers = { "X-GitHub-Delivery": "delivery-42", "X-Hub-Signature-256": signature(raw) };
  assert.equal(receive(raw, headers), 202);
  assert.equal(receive(raw, headers), 200);
  const tampered = Buffer.from(raw.toString("utf8").replace("opened", "closed"));
  assert.equal(receive(tampered, { ...headers, "X-GitHub-Delivery": "delivery-43" }), 401);
  assert.equal(receive(raw, { "X-GitHub-Delivery": "delivery-44" }), 401);
  assert.equal(seen.size, 1);
  console.log("PASS GitHub webhook raw-body signature and dedup model (tamper/missing signature rejected)");
}

(async () => {
  await httpFixture();
  await graphqlFixture();
  rpcFixture();
  eventsFixture();
  webhookFixture();
})().catch(error => { console.error(error); process.exitCode = 1; });
