function charge(items, record, channel, multiplier) {
  if (items.some(x => x < 0)) throw new RangeError('negative');
  const sum = items.reduce((a, b) => a + b, 0);
  record(channel, sum);
  return Math.round(sum * multiplier);
}
module.exports = { charge };
