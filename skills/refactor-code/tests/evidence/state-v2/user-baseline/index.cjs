function createLedger(initial, record) {
  let amount = initial;
  function add(delta) {
    if (!Number.isFinite(delta)) throw new RangeError('delta');
    record(amount, delta);
    amount += delta;
    return amount;
  }
  function receipt() { return 'User total: ' + amount.toFixed(2); }
  return {add, receipt};
}
module.exports = {createLedger};
