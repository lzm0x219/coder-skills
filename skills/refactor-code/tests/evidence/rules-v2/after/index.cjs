const { total } = require('./pricing.cjs');
function receipt(hours, rate) { return '$' + total(hours, rate).toFixed(2); }
module.exports = { total, receipt };
