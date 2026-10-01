const { total } = require('./pricing.cjs');
function receipt(items) { return 'USER Total: ' + total(items).toFixed(2); }
module.exports = { receipt };
