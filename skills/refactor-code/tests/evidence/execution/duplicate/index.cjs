const { charge } = require('./charge.cjs');
function retail(items, record) { return charge(items, record, 'retail', 1.1); }
function wholesale(items, record) { return charge(items, record, 'wholesale', 0.9); }
module.exports = { retail, wholesale };
