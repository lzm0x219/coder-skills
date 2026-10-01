function createSubscriptions() {
  const listeners = new Set();
  let closed = false;
  return {
    subscribe(fn) {
      if (closed) throw new Error('closed');
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    snapshot: () => [...listeners],
    has: fn => listeners.has(fn),
    isClosed: () => closed,
    close() { closed = true; listeners.clear(); }
  };
}
module.exports = { createSubscriptions };
