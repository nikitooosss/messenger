import { useEffect, useRef, useState } from 'react'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { useSendMessage } from './useSendMessage'

interface MessageInputProps {
  chatId: number
}

export function MessageInput({ chatId }: MessageInputProps) {
  const { data: me } = useCurrentUser()
  const { send } = useSendMessage(chatId)
  const { send: wsSend } = useWebSocket()
  const [value, setValue] = useState('')
  const stateRef = useRef<'start' | 'stop' | null>(null)
  const stopTimerRef = useRef<number | null>(null)

  const sendStop = () => {
    if (stateRef.current === 'start' && me) {
      wsSend({ type: 'user_stop_typing', user_id: me.id, chat_id: chatId })
      stateRef.current = 'stop'
    }
    if (stopTimerRef.current) {
      clearTimeout(stopTimerRef.current)
      stopTimerRef.current = null
    }
  }

  useEffect(() => {
    return () => {
      sendStop()
    }
  }, [chatId])

  const onChange = (val: string) => {
    setValue(val)
    if (!me) return
    if (val.length === 0) {
      sendStop()
      return
    }
    if (stateRef.current !== 'start') {
      wsSend({ type: 'user_start_typing', user_id: me.id, chat_id: chatId })
      stateRef.current = 'start'
    }
    if (stopTimerRef.current) clearTimeout(stopTimerRef.current)
    stopTimerRef.current = window.setTimeout(sendStop, 3000)
  }

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!value.trim()) return
    send(value)
    setValue('')
    sendStop()
  }

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSubmit(e)
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex items-end gap-2 border-t border-tg-border bg-tg-bg p-3">
      <textarea
        rows={1}
        placeholder="Write a message…"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={onKeyDown}
        className="flex-1 resize-none rounded-2xl border border-tg-border bg-tg-bg px-3 py-2 text-sm text-tg-text outline-none focus:border-tg-accent"
      />
      <button
        type="submit"
        disabled={!value.trim()}
        className="flex h-9 w-9 items-center justify-center rounded-full bg-tg-accent text-white transition hover:bg-tg-accentHover disabled:opacity-40"
        title="Send"
      >
        ➤
      </button>
    </form>
  )
}
