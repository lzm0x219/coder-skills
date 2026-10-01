const { createSubscriptions } = require('./subscriptions.cjs');
const { createPublisher } = require('./publisher.cjs');
function createBus() {
  const subscriptions = createSubscriptions();
  return { subscribe: subscriptions.subscribe, publish: createPublisher(subscriptions), close: subscriptions.close };
}
module.exports = { createBus };
