import { useState, useRef, useEffect, useLayoutEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { qk } from '../../lib/queryKeys'
import type { Message } from '../../types/models'

interface MessageBubbleProps {
  message: Message
  showAuthor: boolean
  isOwn: boolean
  isOptimistic: boolean
  authorName: string
}

export function MessageBubble({ message, showAuthor, isOwn, isOptimistic, authorName }: MessageBubbleProps) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState(message.content)
  const [menuOpen, setMenuOpen] = useState(false)
  const [openUp, setOpenUp] = useState(false)
  const { send } = useWebSocket()
  const { data: me } = useCurrentUser()
  const qc = useQueryClient()
  const menuRef = useRef<HTMLDivElement>(null)
  const menuDivRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!editing) {
      setDraft(message.content)
    }
  }, [message.content, editing])

  useEffect(() => {
    if (!menuOpen) return
    const onClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false)
      }
    }
    window.addEventListener('mousedown', onClick)
    return () => window.removeEventListener('mousedown', onClick)
  }, [menuOpen])

  useLayoutEffect(() => {
    if (!menuOpen) return
    if (!menuRef.current || !menuDivRef.current) return
    const wrapRect = menuRef.current.getBoundingClientRect()
    const menuRect = menuDivRef.current.getBoundingClientRect()
    const spaceBelow = window.innerHeight - wrapRect.bottom
    const spaceAbove = wrapRect.top
    setOpenUp(spaceBelow < menuRect.height && spaceAbove > spaceBelow)
  }, [menuOpen])

  useEffect(() => {
    if (!menuOpen) return
    const onScroll = (e: Event) => {
      if (menuRef.current && e.target instanceof Node && menuRef.current.contains(e.target)) {
        return
      }
      setMenuOpen(false)
    }
    window.addEventListener('scroll', onScroll, true)
    return () => window.removeEventListener('scroll', onScroll, true)
  }, [menuOpen])

  useEffect(() => {
    if (!menuOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [menuOpen])

  const submitEdit = () => {
    const trimmed = draft.trim()
    if (!trimmed || trimmed === message.content) {
      setEditing(false)
      setDraft(message.content)
      return
    }
    qc.setQueryData<Message[]>(qk.messages(message.chat_id), (old = []) =>
      old.map((m) => (m.id === message.id ? { ...m, content: trimmed } : m)),
    )
    send({
      type: 'message_update',
      message: { id: message.id, content: trimmed },
    })
    setEditing(false)
  }

  const remove = () => {
    qc.setQueryData<Message[]>(qk.messages(message.chat_id), (old = []) =>
      old.filter((m) => m.id !== message.id),
    )
    send({
      type: 'message_delete',
      message,
    })
    setMenuOpen(false)
  }

  return (
    <div
      className={`group flex w-full ${isOwn ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`flex max-w-[70%] flex-col ${isOwn ? 'items-end' : 'items-start'}`}
      >
        {showAuthor && !isOwn && (
          <div className="mb-0.5 px-1 text-xs font-medium text-tg-accent">
            {authorName}
          </div>
        )}
        <div
          className={`relative rounded-bubble px-3 py-2 text-sm shadow-sm ${
            isOwn ? 'bg-tg-bubbleOut text-tg-text' : 'bg-tg-bubbleIn text-tg-text'
          }`}
        >
          {editing ? (
            <div className="flex flex-col gap-1">
              <textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                className="resize-none rounded bg-tg-bg p-1 text-tg-text outline-none"
                rows={Math.min(5, draft.split('\n').length)}
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    submitEdit()
                  }
                  if (e.key === 'Escape') {
                    setEditing(false)
                    setDraft(message.content)
                  }
                }}
              />
              <div className="flex justify-end gap-2 text-xs">
                <button
                  className="text-tg-mute hover:text-tg-text"
                  onClick={() => {
                    setEditing(false)
                    setDraft(message.content)
                  }}
                >
                  Cancel
                </button>
                <button
                  className="text-tg-accent hover:underline"
                  onClick={submitEdit}
                >
                  Save
                </button>
              </div>
            </div>
          ) : (
            <div className="whitespace-pre-wrap break-all">{message.content}</div>
          )}
          {isOwn && !editing && me && (
            <div
              className={`absolute -left-1 top-1/2 -translate-x-full -translate-y-1/2 transition ${
                menuOpen ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
              }`}
              ref={menuRef}
            >
              <button
                onClick={() => setMenuOpen((v) => !v)}
                className="flex h-6 w-6 items-center justify-center rounded-full bg-tg-sidebar text-tg-mute hover:bg-tg-sidebarHover hover:text-tg-text"
                title="More"
              >
                ⋯
              </button>
              {menuOpen && (
                <div
                  ref={menuDivRef}
                  className={`absolute right-0 w-32 rounded-lg border border-tg-border bg-tg-panel py-1 text-sm shadow-lg ${
                    openUp ? 'bottom-full mb-1' : 'top-full mt-1'
                  }`}
                >
                  <button
                    onClick={() => {
                      setEditing(true)
                      setMenuOpen(false)
                    }}
                    className="block w-full px-3 py-1.5 text-left hover:bg-tg-sidebar"
                  >
                    Edit
                  </button>
                  <button
                    onClick={remove}
                    className="block w-full px-3 py-1.5 text-left text-tg-danger hover:bg-tg-sidebar"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
        <div className="mt-0.5 px-1 text-[10px] text-tg-mute">
          {isOptimistic ? 'sending…' : formatClock(message.created_at)}
        </div>
      </div>
    </div>
  )
}

function formatClock(iso: string) {
  return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}
