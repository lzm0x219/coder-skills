const assert = require('node:assert/strict');
const path = require('node:path');
const root = process.argv[2] || __dirname;
const lib = require(path.join(root, 'library/dist/src'));
const billing = require(path.join(root, 'duplicate/index.cjs'));
const { createBus } = require(path.join(root, 'async/index.cjs'));
const observations = {};
assert.deepEqual(Object.keys(lib).sort(),['format','receipt','total']);
assert.deepEqual(Object.keys(billing).sort(),['retail','wholesale']);
assert.equal(Number.isNaN(lib.total([],NaN)),true);
function capture(fn) { try { return fn(); } catch (e) { return [e.constructor.name, e.message]; } }
observations.library = [[], [{name:'tea', cents:105}], [{name:'a', cents:-1},{name:'b', cents:206}]].flatMap(items => [-0.1,0,0.1,1,1.1,NaN].map(discount => [capture(()=>lib.total(items,discount)),capture(()=>lib.receipt(items,discount))]));
observations.format = [-1,0,105,NaN,Infinity].map(lib.format);
observations.billing = [];
for (const name of ['retail','wholesale']) for (const items of [[],[1,4],[-1],[0.5], [NaN]]) {
  const records=[]; const result=capture(()=>billing[name](items,(...args)=>records.push(args)));
  observations.billing.push({name,result,records});
}
for (const name of ['retail','wholesale']) assert.deepEqual(capture(()=>billing[name]([1],()=>{throw new Error('record');})),['Error','record']);
const queued=[]; const original=global.queueMicrotask; global.queueMicrotask=fn=>queued.push(fn);
try {
  const bus=createBus(), events=[];
  const a=value=>events.push(['a',value]); const b=value=>events.push(['b',value]);
  const off=bus.subscribe(a); bus.publish(1); bus.subscribe(b); assert.equal(off(),true); bus.subscribe(a); queued.shift()();
  assert.deepEqual(events,[['a',1]]);
  bus.publish(2); bus.close(); bus.close(); queued.shift()(); assert.deepEqual(events,[['a',1]]);
  assert.deepEqual(capture(()=>bus.subscribe(b)),['Error','closed']); bus.publish(3); assert.equal(queued.length,0); assert.equal(off(),false);
  const mutation=createBus(), order=[]; let remove;
  mutation.subscribe(()=>{order.push('first');remove();mutation.subscribe(()=>order.push('late'));}); remove=mutation.subscribe(()=>order.push('removed')); mutation.publish(1); queued.shift()(); assert.deepEqual(order,['first']);
  const failing=createBus(), failures=[]; const stop=failing.subscribe(()=>{failures.push('throw');throw new Error('callback');}); failing.subscribe(()=>failures.push('next')); failing.publish(1); assert.deepEqual(capture(()=>queued.shift()()),['Error','callback']); assert.deepEqual(failures,['throw']); stop(); failing.publish(2); queued.shift()(); assert.deepEqual(failures,['throw','next']); failing.close();
  observations.async={events,order,failures};
} finally {global.queueMicrotask=original;}
console.log(JSON.stringify(observations));
