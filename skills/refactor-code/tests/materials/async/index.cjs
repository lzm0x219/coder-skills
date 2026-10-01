function createBus() {
  const listeners = new Set();
  let closed = false;
  function subscribe(fn) {
    if (closed) throw new Error('closed');
    listeners.add(fn);
    return () => listeners.delete(fn);
  }
  function publish(value) {
    if (closed) return;
    const snapshot = [...listeners];
    queueMicrotask(() => {
      if (closed) return;
      for (const fn of snapshot) if (listeners.has(fn)) fn(value);
    });
  }
  function close() { closed = true; listeners.clear(); }
  return { subscribe, publish, close };
}
module.exports = { createBus };
