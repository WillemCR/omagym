export function createEventBus() {
  return {
    on(_event, _listener) { throw new Error('TODO: register a listener'); },
    emit(_event, _payload) { throw new Error('TODO: dispatch a snapshot'); },
    listenerCount(_event) { throw new Error('TODO: count registrations'); },
  };
}
