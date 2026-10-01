const assert = require('node:assert/strict');
const api = require('./index.cjs');
assert.deepEqual(Object.keys(api).sort(), ['receipt','total']);
assert.equal(api.total([]), 0);
assert.equal(api.total([{price:10,quantity:2}]), 22);
assert.equal(api.receipt([{price:10,quantity:2}]), 'USER Total: 22.00');
console.log('consumer: PASS');
