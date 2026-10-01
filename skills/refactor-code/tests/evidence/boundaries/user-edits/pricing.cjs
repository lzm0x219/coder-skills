const tax = 0.1;
function total(items) { return items.reduce((n, x) => n + x.price * x.quantity, 0) * (1 + tax); }
module.exports = { total };
