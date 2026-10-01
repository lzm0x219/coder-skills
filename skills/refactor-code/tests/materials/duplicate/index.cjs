function retail(items, record) {
  if (items.some(x => x < 0)) throw new RangeError('negative');
  const sum = items.reduce((a, b) => a + b, 0);
  record('retail', sum);
  return Math.round(sum * 1.1);
}
function wholesale(items, record) {
  if (items.some(x => x < 0)) throw new RangeError('negative');
  const sum = items.reduce((a, b) => a + b, 0);
  record('wholesale', sum);
  return Math.round(sum * 0.9);
}
module.exports = { retail, wholesale };
