function createPosting(amount, record) {
  return function add(delta) {
    if (!Number.isFinite(delta)) throw new RangeError('delta');
    record(amount.read(), delta);
    return amount.apply(delta);
  };
}
module.exports = {createPosting};
