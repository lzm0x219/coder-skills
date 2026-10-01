const assert = require('node:assert/strict');
const {createLedger}=require('./index.cjs');
assert.deepEqual(Object.keys(require('./index.cjs')),['createLedger']);
const events=[];
let ledger, reentered=false;
ledger=createLedger(2,(amount,delta)=>{
  events.push([amount,delta,ledger.receipt()]);
  if (!reentered) {reentered=true;events.push(['nested',ledger.add(4)]);}
});
assert.equal(ledger.add(3),9);
assert.deepEqual(events,[[2,3,'Total: 2.00'],[2,4,'Total: 2.00'],['nested',6]]);
assert.equal(ledger.receipt(),'Total: 9.00');
const failure=createLedger(10,()=>{throw new Error('record-failed');});
assert.throws(()=>failure.add(2),{name:'Error',message:'record-failed'});
assert.equal(failure.receipt(),'Total: 10.00');
let calls=0;
const a=createLedger(1,()=>calls++), b=createLedger(5,()=>{});
for(const delta of [NaN,Infinity,-Infinity,'1',null,undefined]) assert.throws(()=>a.add(delta),{name:'RangeError',message:'delta'});
assert.equal(calls,0);assert.equal(a.receipt(),'Total: 1.00');
assert.equal(a.add(-2),-1);assert.equal(b.receipt(),'Total: 5.00');assert.equal(a.add(0),-1);assert.equal(calls,2);
const detached=a.add;assert.equal(detached(2),1);const read=a.receipt;assert.equal(read(),'Total: 1.00');
console.log(JSON.stringify({exports:['createLedger'],events,final:ledger.receipt(),failure:failure.receipt(),a:a.receipt(),b:b.receipt(),calls}));
