const assert = require('node:assert/strict');
const api = require(process.argv[2]);
assert.equal(api.total(1.5,3.5),5);
