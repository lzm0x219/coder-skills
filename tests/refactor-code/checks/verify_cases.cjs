// Evaluator-only checks. Pass the executor's isolated case root.
const assert = require('node:assert/strict');
const path = require('node:path');
const root = path.resolve(process.argv[2] || path.join(__dirname, '..', 'cases'));
async function main() {
  const lib = require(path.join(root, 'library/dist/src/index.js'));
  assert.deepEqual(Object.keys(lib).sort(), ['format', 'receipt', 'total']);
  assert.equal(lib.total([{name:'x',cents:105}], .1), 95);
  assert.equal(lib.receipt([], 0), ':0.00');
  assert.equal(lib.receipt([{name:'x',cents:105}]), 'x:1.05');
  assert.throws(() => lib.total([], -1), {name:'RangeError',message:'discount'});
  const {createBus} = require(path.join(root, 'async/index.cjs'));
  const bus = createBus(), events = [];
  const cancel = bus.subscribe(x => events.push(x));
  bus.publish(1); assert.deepEqual(events, []);
  cancel(); await Promise.resolve(); assert.deepEqual(events, []);
  bus.subscribe(x => events.push(x)); bus.publish(2);
  await Promise.resolve(); assert.deepEqual(events, [2]);
  bus.publish(3); bus.close(); bus.close();
  await Promise.resolve(); assert.deepEqual(events, [2]);
  assert.throws(() => bus.subscribe(() => {}), /closed/);
  bus.publish(4); await Promise.resolve(); assert.deepEqual(events, [2]);
  const another = createBus(), sequence = [];
  another.subscribe(x => sequence.push(x)); another.publish('a'); another.publish('b');
  await Promise.resolve(); assert.deepEqual(sequence, ['a','b']);
  another.close();
  const billing = require(path.join(root, 'duplicate/index.cjs'));
  for (const [name, factor] of [['retail',1.1],['wholesale',.9]]) {
    const log = [];
    assert.equal(billing[name]([5,10], (...args) => log.push(args)), Math.round(15*factor));
    assert.deepEqual(log, [[name,15]]);
    assert.equal(billing[name]([], () => {}), 0);
    let calls = 0;
    assert.throws(() => billing[name]([-1], () => calls++), {name:'RangeError',message:'negative'});
    assert.equal(calls, 0);
    assert.throws(() => billing[name]([1], () => {throw new Error('record');}), /record/);
  }
  console.log('PASS library public consumer/runtime, async order/cancel/close, duplicate boundaries/side effects');
}
main().catch(error => {console.error(error);process.exitCode = 1;});
