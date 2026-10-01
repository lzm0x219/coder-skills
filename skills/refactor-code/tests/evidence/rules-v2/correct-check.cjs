const assert = require('node:assert/strict');
const api = require(process.argv[2]);
assert.deepEqual(Object.keys(api).sort(),['receipt','total']);
assert.equal(api.total(1.5,3.5),5.25);
assert.equal(api.receipt(1.5,3.5),'$5.25');
assert.equal(api.total(0,3.5),0);
assert.equal(api.total(-1.5,3.5),-5.25);
console.log('contract PASS');
