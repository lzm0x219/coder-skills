const {formatTotal} = require('./display.cjs');
const {createAmount} = require('./amount.cjs');
const {createPosting} = require('./posting.cjs');
function createLedger(initial, record) {
  const amount = createAmount(initial);
  const add = createPosting(amount, record);
  function receipt() { return formatTotal(amount.read()); }
  return {add, receipt};
}
module.exports = {createLedger};
