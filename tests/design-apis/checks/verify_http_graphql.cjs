#!/usr/bin/env node
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const SwaggerParser = require('@apidevtools/swagger-parser');
const Ajv2020 = require('ajv/dist/2020').default;
const addFormats = require('ajv-formats').default;
const {
  buildSchema,
  execute,
  GraphQLError,
  parse,
  print,
  validate,
} = require('graphql');

const fixtures = path.resolve(process.argv[2] || path.join(__dirname, '..', 'cases'));
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8'));
const readText = (p) => fs.readFileSync(p, 'utf8');
const pass = (label) => console.log(`PASS ${label}`);
const fixture = (...parts) => path.join(fixtures, ...parts);

function makeAjv() {
  const ajv = new Ajv2020({ allErrors: true, strict: false });
  addFormats(ajv);
  return ajv;
}

function validatorFor(ajv, components, ref) {
  const root = { $schema: 'https://json-schema.org/draft/2020-12/schema', components };
  root.$ref = `#/components/${ref}`;
  return ajv.compile(root);
}

function expectValid(validateValue, value, label) {
  assert.equal(validateValue(value), true, `${label}: ${JSON.stringify(validateValue.errors)}`);
  pass(label);
}

function expectInvalid(validateValue, value, label) {
  assert.equal(validateValue(value), false, `${label}: expected invalid value`);
  pass(label);
}

async function testHttp() {
  const profilePath = fixture('http-profile');
  const profileApi = await SwaggerParser.validate(path.join(profilePath, 'openapi.json'));
  const profileCases = readJson(path.join(profilePath, 'cases.json'));
  const replace = profileApi.paths['/profiles/{profileId}'].put;
  assert.equal(replace.operationId, 'replaceProfile');
  assert.ok(replace.parameters.some((p) => p.name === 'If-Match' && p.required));
  assert.ok(replace.responses['401'].headers['WWW-Authenticate']);
  assert.ok(replace.responses['403']);
  assert.equal(profileCases.unauthorizedAndStale.expectedStatus, 401);
  assert.equal(profileCases.unauthorizedAndStale.expectedHeaders['WWW-Authenticate'], 'Bearer realm="profiles"');
  assert.equal(profileCases.authenticatedButForbidden.expectedStatus, 403);
  assert.equal(profileCases.staleVersion.expectedStatus, 412);
  pass('HTTP profile contract parses and distinguishes unauthenticated 401, forbidden 403, and stale 412');

  const profileAjv = makeAjv();
  const problem = validatorFor(profileAjv, profileApi.components, 'schemas/Problem');
  for (const name of ['unauthorizedAndStale', 'invalidBodyProblem']) {
    const vector = profileCases[name];
    expectValid(problem, vector.problem, `HTTP Problem Details shape (${name})`);
    assert.equal(vector.problem.status, vector.expectedStatus, `${name}: Problem.status must match HTTP status`);
  }
  const unauthorizedProblem = profileCases.unauthorizedAndStale.problem;
  assert.equal(unauthorizedProblem.status, profileCases.unauthorizedAndStale.expectedStatus);
  pass('HTTP Problem Details status matches the actual status for 401 and 400 cases');

  const asyncPath = fixture('http-exports');
  const asyncApi = await SwaggerParser.validate(path.join(asyncPath, 'openapi.json'));
  const vectors = readJson(path.join(asyncPath, 'cases.json'));
  const asyncAjv = makeAjv();
  const exportRequest = validatorFor(asyncAjv, asyncApi.components, 'schemas/ExportRequest');
  const operation = validatorFor(asyncAjv, asyncApi.components, 'schemas/Operation');
  const page = validatorFor(asyncAjv, asyncApi.components, 'schemas/ProfilePage');
  expectValid(exportRequest, vectors.create.body, 'HTTP export request accepted by OpenAPI schema');
  expectInvalid(exportRequest, { profileId: '', format: 'xml' }, 'HTTP invalid export request rejected');
  assert.equal(vectors.create.expected.status, 202);
  assert.equal(asyncApi.paths['/exports'].post.responses['202'].headers.Location.required, true);
  assert.equal(vectors.create.expected.headers.Location, '/exports/op-1');
  expectValid(operation, vectors.create.expected.body, 'HTTP 202 operation response has a monitorable identity and state');
  expectValid(operation, vectors.pollSucceeded.expected.body, 'HTTP succeeded long-running operation includes result');
  expectValid(operation, vectors.pollFailed.expected.body, 'HTTP failed long-running operation includes problem');
  expectInvalid(operation, { id: 'op-bad', state: 'succeeded' }, 'HTTP succeeded operation without result rejected');
  expectInvalid(operation, { id: 'op-bad', state: 'failed' }, 'HTTP failed operation without error rejected');
  pass('HTTP long-running operation schema enforces terminal result/error presence');

  assert.equal(vectors.sameKeySameRequestRetry.headers['Idempotency-Key'], vectors.create.headers['Idempotency-Key']);
  assert.deepEqual(vectors.sameKeySameRequestRetry.body, vectors.create.body);
  assert.equal(vectors.sameKeyDifferentRequest.headers['Idempotency-Key'], vectors.create.headers['Idempotency-Key']);
  assert.notDeepEqual(vectors.sameKeyDifferentRequest.body, vectors.create.body);
  assert.equal(vectors.sameKeyDifferentRequest.expected.status, 409);
  const problemValidator = validatorFor(asyncAjv, asyncApi.components, 'schemas/Problem');
  expectValid(problemValidator, vectors.sameKeyDifferentRequest.expected.body, 'HTTP idempotency conflict is a valid Problem Details response');
  pass('HTTP idempotency vectors cover same-request retry and same-key/different-request conflict');

  for (const name of ['pageOne', 'emptyIntermediatePage', 'pageAfterEmpty']) {
    expectValid(page, vectors[name].expected.body, `HTTP pagination response schema (${name})`);
  }
  assert.equal(vectors.emptyIntermediatePage.expected.body.profiles.length, 0);
  assert.equal(vectors.emptyIntermediatePage.expected.body.next_page_token, 'opaque-b');
  assert.ok(vectors.pageAfterEmpty.expected.body.next_page_token === '');
  assert.equal(vectors.filterChangedWithToken.expected.status, 400);
  assert.notEqual(new URL(`https://api.example.test${vectors.pageOne.path}`).searchParams.get('status'), new URL(`https://api.example.test${vectors.filterChangedWithToken.path}`).searchParams.get('status'));
  expectValid(problemValidator, vectors.filterChangedWithToken.expected.body, 'HTTP changed-filter continuation failure uses Problem Details');
  expectInvalid(page, { profiles: [], next_page_token: 42 }, 'HTTP invalid continuation token response type rejected');
  pass('HTTP pagination handles empty nonterminal page, filter-bound token, and explicit terminal token');
}

function loadOperation(document, name) {
  const parsed = parse(document);
  const definition = parsed.definitions.find((d) => d.kind === 'OperationDefinition' && d.name && d.name.value === name);
  assert.ok(definition, `missing GraphQL operation ${name}`);
  return { kind: 'Document', definitions: [definition] };
}

async function executeOperation(schema, operation, variableValues, rootValue, fieldResolver) {
  return execute({ schema, document: operation, variableValues, rootValue, fieldResolver });
}

async function testGraphql() {
  const root = fixture('graphql-order');
  const schema = buildSchema(readText(path.join(root, 'schema.graphql')));
  const ops = readText(path.join(root, 'operations.graphql'));
  const vars = readJson(path.join(root, 'variables.json'));
  const update = loadOperation(ops, 'UpdateOrder');
  const oldConsumer = loadOperation(ops, 'OldConsumer');
  const twoReads = loadOperation(ops, 'TwoOrderReads');
  const threeReads = loadOperation(ops, 'ThreeAliasedOrderReads');
  const nullableFailure = loadOperation(ops, 'NullableNoteFailure');
  let mutationCalls = 0;
  let capturedInput;
  const rootValue = {
    updateOrder(args) {
      mutationCalls += 1;
      capturedInput = args.input;
      return { id: args.id, ...args.input };
    },
    order({ id }) { return { id, note: 'note', priority: 1, displayLabel: null, legacyNote: 'legacy' }; },
  };

  let result = await executeOperation(schema, update, vars.omittedInputFields, rootValue);
  assert.deepEqual(result.errors, undefined);
  assert.equal(capturedInput.note, 'default note');
  assert.equal(capturedInput.priority, 1);
  assert.equal(Object.hasOwn(capturedInput, 'displayLabel'), false);
  pass('GraphQL omitted input fields apply field defaults and preserve truly omitted nullable field');

  result = await executeOperation(schema, update, vars.explicitNullOptionalFields, rootValue);
  assert.deepEqual(result.errors, undefined);
  assert.equal(capturedInput.note, null);
  assert.equal(capturedInput.displayLabel, null);
  assert.equal(capturedInput.priority, 1);
  pass('GraphQL explicit null remains distinct from omission and does not trigger default');

  result = await executeOperation(schema, update, vars.explicitValues, rootValue);
  assert.deepEqual(result.errors, undefined);
  assert.equal(capturedInput.note, 'packed');
  assert.equal(capturedInput.priority, 4);
  assert.equal(capturedInput.displayLabel, 'gift');
  pass('GraphQL explicitly supplied input values reach mutation resolver');

  const callsBeforeInvalid = mutationCalls;
  result = await executeOperation(schema, update, vars.invalidNonNullWithDefault, rootValue);
  assert.ok(result.errors && result.errors.length > 0);
  assert.equal(Object.hasOwn(result, 'data'), false);
  assert.equal(mutationCalls, callsBeforeInvalid);
  pass('GraphQL invalid nullable value for non-null-with-default input is request error; mutation does not execute');

  result = await executeOperation(schema, update, vars.missingRequiredOperationVariable, rootValue);
  assert.ok(result.errors && result.errors.length > 0);
  assert.equal(Object.hasOwn(result, 'data'), false);
  assert.equal(mutationCalls, callsBeforeInvalid);
  pass('GraphQL omitted required operation variable fails before resolver execution');

  result = await executeOperation(schema, oldConsumer, undefined, rootValue);
  assert.deepEqual(result.errors, undefined);
  assert.equal(result.data.order.legacyNote, 'legacy');
  pass('GraphQL old consumer operation remains valid while deprecated field is retained');

  let orderCalls = 0;
  const countingRoot = { ...rootValue, order({ id }) { orderCalls += 1; return { id, note: 'n', priority: 1 }; } };
  result = await executeOperation(schema, twoReads, undefined, countingRoot);
  assert.deepEqual(result.errors, undefined);
  assert.equal(orderCalls, 2);
  pass('GraphQL two aliased top-level selections execute as two field resolutions');
  result = await executeOperation(schema, threeReads, undefined, countingRoot);
  assert.deepEqual(result.errors, undefined);
  assert.equal(orderCalls, 5);
  pass('GraphQL executor confirms three aliases cause three separate top-level field resolutions');

  const rootOrderBudget = (context) => ({
    OperationDefinition(node) {
      if (node.operation !== 'query') return;
      const orderSelections = node.selectionSet.selections.filter(
        (selection) => selection.kind === 'Field' && selection.name.value === 'order',
      );
      if (orderSelections.length > 2) {
        context.reportError(new GraphQLError('A query may select order at most twice at the root.', { nodes: node }));
      }
    },
  });
  assert.equal(validate(schema, twoReads, [rootOrderBudget]).length, 0);
  assert.equal(validate(schema, threeReads, [rootOrderBudget]).length, 1);
  pass('GraphQL alias-aware candidate root-selection budget accepts two and rejects three');

  const failingFieldResolver = (source, args, context, info) => {
    if (info.parentType.name === 'Order' && info.fieldName === 'note') throw new Error('note backend unavailable');
    const value = source[info.fieldName];
    return typeof value === 'function' ? value.call(source, args, context, info) : value;
  };
  result = await executeOperation(schema, nullableFailure, undefined, rootValue, failingFieldResolver);
  assert.equal(result.data.order.id, '42');
  assert.equal(result.data.order.note, null);
  assert.deepEqual(result.errors[0].path, ['order', 'note']);
  pass('GraphQL nullable field execution failure retains sibling data and reports errors.path');

  const brokenSchema = buildSchema(readText(path.join(root, 'broken.graphql')));
  const oldValidationErrors = validate(brokenSchema, oldConsumer);
  assert.ok(oldValidationErrors.some((e) => /legacyNote/.test(e.message)));
  result = await executeOperation(brokenSchema, nullableFailure, undefined, rootValue, failingFieldResolver);
  assert.equal(result.data.order, null);
  assert.deepEqual(result.errors[0].path, ['order', 'note']);
  pass('GraphQL negative schema rejects old consumer and non-null failure bubbles to nullable parent');
}

(async () => {
  await testHttp();
  await testGraphql();
  console.log('PASS HTTP and GraphQL design fixtures complete');
})().catch((error) => {
  console.error(error.stack || error);
  process.exitCode = 1;
});
