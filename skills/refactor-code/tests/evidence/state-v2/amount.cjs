function createAmount(initial) {
  let amount = initial;
  return {
    read: () => amount,
    apply(delta) { amount += delta; return amount; }
  };
}
module.exports = {createAmount};
