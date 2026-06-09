import { useEffect, useState } from 'react'
import { presenceBus } from './presenceStore'

const online = new Set<number>()
const listeners = new Set<() => void>()

function notify() {
  listeners.forEach((l) => l())
}

presenceBus.on((ev) => {
  if (ev.type === 'user_online') {
    online.add(ev.user_id)
    notify()
  } else if (ev.type === 'user_offline') {
    online.delete(ev.user.id)
    notify()
  }
})

export function seedOnline(id: number, isOnline: boolean) {
  if (isOnline) online.add(id)
  else online.delete(id)
  notify()
}

export function useOnline(userId: number | null | undefined): boolean {
  const [, force] = useState(0)
  useEffect(() => {
    const l = () => force((n) => n + 1)
    listeners.add(l)
    return () => {
      listeners.delete(l)
    }
  }, [])
  if (userId == null) return false
  return online.has(userId)
}
