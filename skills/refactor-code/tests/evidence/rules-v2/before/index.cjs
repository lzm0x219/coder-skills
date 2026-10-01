function total(hours, rate) { return hours * rate; }
function receipt(hours, rate) { return '$' + total(hours, rate).toFixed(2); }
module.exports = { total, receipt };
