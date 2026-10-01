function createPublisher(subscriptions) {
  return function publish(value) {
    if (subscriptions.isClosed()) return;
    const snapshot = subscriptions.snapshot();
    queueMicrotask(() => {
      if (subscriptions.isClosed()) return;
      for (const fn of snapshot) if (subscriptions.has(fn)) fn(value);
    });
  };
}
module.exports = { createPublisher };
