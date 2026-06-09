import type { PresenceEvent } from '../../types/wsEvents'

class Bus {
  private listeners = new Set<(e: PresenceEvent) => void>()

  emit(e: PresenceEvent) {
    this.listeners.forEach((l) => l(e))
  }

  on(l: (e: PresenceEvent) => void) {
    this.listeners.add(l)
    return () => {
      this.listeners.delete(l)
    }
  }
}

export const presenceBus = new Bus()
