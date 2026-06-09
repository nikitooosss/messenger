import { useEffect, useState } from 'react'
import { presenceBus } from '../presence/presenceStore'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useCurrentUser } from '../../auth/useCurrentUser'

interface TypingIndicatorProps {
  chatId: number
}

const SAFETY_TIMEOUT_MS = 5000

export function TypingIndicator({ chatId }: TypingIndicatorProps) {
  const { data: me } = useCurrentUser()
  const { data: users = [] } = useQuery({ queryKey: qk.users, queryFn: api.users })
  const [typers, setTypers] = useState<Map<number, number>>(new Map())

  useEffect(() => {
    const off = presenceBus.on((ev) => {
      if (ev.type === 'user_start_typing' && ev.chat_id === chatId) {
        setTypers((prev) => {
          const next = new Map(prev)
          next.set(ev.user_id, Date.now())
          return next
        })
      } else if (ev.type === 'user_stop_typing' && ev.chat_id === chatId) {
        setTypers((prev) => {
          if (!prev.has(ev.user_id)) return prev
          const next = new Map(prev)
          next.delete(ev.user_id)
          return next
        })
      }
    })
    return off
  }, [chatId])

  useEffect(() => {
    const t = window.setInterval(() => {
      const now = Date.now()
      setTypers((prev) => {
        let changed = false
        const next = new Map(prev)
        for (const [id, last] of prev) {
          if (now - last > SAFETY_TIMEOUT_MS) {
            next.delete(id)
            changed = true
          }
        }
        return changed ? next : prev
      })
    }, 1000)
    return () => clearInterval(t)
  }, [])

  const visible = Array.from(typers.keys()).filter((id) => id !== me?.id)
  if (visible.length === 0) return null

  const names = visible
    .map((id) => users.find((u) => u.id === id))
    .filter((u): u is NonNullable<typeof u> => Boolean(u))
    .map((u) => u.name?.trim() || u.uniq_name)

  if (names.length === 0) return null

  const label =
    names.length === 1
      ? `${names[0]} is typing…`
      : names.length === 2
        ? `${names[0]} and ${names[1]} are typing…`
        : `${names[0]} and ${names.length - 1} others are typing…`

  return (
    <div className="px-4 py-1 text-xs italic text-tg-mute">
      <span className="mr-1 inline-flex gap-0.5 align-middle">
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-tg-mute" style={{ animationDelay: '0ms' }} />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-tg-mute" style={{ animationDelay: '150ms' }} />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-tg-mute" style={{ animationDelay: '300ms' }} />
      </span>
      {label}
    </div>
  )
}
