const assert = require('node:assert/strict');
const path = require('node:path');
const {createBus}=require(path.join(process.argv[2] || __dirname,'async/index.cjs'));
(async()=>{
  const events=[], bus=createBus();
  bus.subscribe(value=>events.push(value));
  bus.publish(1); bus.publish(2);
  assert.deepEqual(events,[]);
  await Promise.resolve();
  assert.deepEqual(events,[1,2]);
  bus.publish(3); bus.close();
  await Promise.resolve();
  assert.deepEqual(events,[1,2]);
  console.log(JSON.stringify(events));
})().catch(error=>{console.error(error);process.exitCode=1;});
