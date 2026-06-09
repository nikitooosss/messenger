import { useEffect, useRef } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { useMessages } from './useMessages'
import { MessageBubble } from './MessageBubble'
import { MessageInput } from './MessageInput'
import { TypingIndicator } from './TypingIndicator'
import { AddParticipantDialog } from '../participants/AddParticipantDialog'
import { ParticipantList } from '../participants/ParticipantList'
import { UserAvatar } from '../../components/UserAvatar'
import { Spinner } from '../../components/Spinner'
import { formatDateLabel } from '../../lib/time'
import { formatLastSeen } from '../../lib/time'
import { useState } from 'react'
import type { Message } from '../../types/models'
import type { User } from '../../types/models'

interface MessageViewProps {
  chatId: number
}

export function MessageView({ chatId }: MessageViewProps) {
  const { data: me } = useCurrentUser()
  const { data: messages, isLoading } = useMessages(chatId)
  const { data: users = [] } = useQuery<User[]>({ queryKey: qk.users, queryFn: api.users })
  const { data: participants = [] } = useQuery({
    queryKey: qk.participants(chatId),
    queryFn: () => api.participants(chatId),
  })
  const { data: chats = [] } = useQuery({
    queryKey: qk.chats(),
    queryFn: () => api.chats(me!.id),
  })
  const chat = chats.find((c) => c.id === chatId)
  const [addOpen, setAddOpen] = useState(false)
  const [infoOpen, setInfoOpen] = useState(false)
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [messages, chatId])

  const sorted = [...(messages ?? [])].sort((a, b) =>
    a.created_at.localeCompare(b.created_at),
  )

  const peer = chat && !chat.is_group
    ? participants.find((p) => p.user_id !== me?.id)
    : null
  const peerUser = peer ? users.find((u) => u.id === peer.user_id) : null
  const displayName = chat?.is_group
    ? chat.name
    : peerUser?.name?.trim() || peerUser?.uniq_name || chat?.name || 'Chat'

  const headerSubtitle = !chat?.is_group && peerUser
    ? formatLastSeen(peerUser.last_seen)
    : chat?.is_group
      ? `${participants.length} members`
      : ''

  return (
    <section className="flex h-full min-w-0 flex-1 flex-col bg-tg-bg">
      <header className="flex items-center gap-3 border-b border-tg-border bg-tg-panel px-4 py-3">
        {chat?.is_group ? (
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-tg-accent text-sm font-semibold text-white">
            #
          </div>
        ) : (
          <UserAvatar user={peerUser ?? null} size={40} showOnline />
        )}
        <div className="min-w-0 flex-1">
          <div className="truncate font-medium text-tg-text">{displayName}</div>
          <div className="truncate text-xs text-tg-mute">{headerSubtitle}</div>
        </div>
        {chat?.is_group && (
          <button
            onClick={() => setInfoOpen((v) => !v)}
            className="rounded-lg px-3 py-1.5 text-sm text-tg-accent hover:bg-tg-sidebar"
          >
            Info
          </button>
        )}
      </header>

      <div className="flex min-h-0 flex-1">
        <div className="flex min-w-0 flex-1 flex-col">
          <div ref={scrollRef} className="flex-1 space-y-1 overflow-y-auto px-4 py-3">
            {isLoading ? (
              <div className="flex h-full items-center justify-center">
                <Spinner />
              </div>
            ) : sorted.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-tg-mute">
                No messages yet. Say hi!
              </div>
            ) : (
              <MessageList sorted={sorted} meId={me?.id ?? -1} users={users} />
            )}
          </div>
          <TypingIndicator chatId={chatId} />
          <MessageInput chatId={chatId} />
        </div>

        {infoOpen && chat?.is_group && (
          <aside className="w-72 shrink-0 border-l border-tg-border bg-tg-sidebar">
            <div className="flex items-center justify-between border-b border-tg-border px-4 py-3">
              <div className="font-medium text-tg-text">Members</div>
              <button
                onClick={() => setAddOpen(true)}
                className="text-sm text-tg-accent hover:underline"
              >
                Add
              </button>
            </div>
            <ParticipantList
              chatId={chatId}
              participants={participants}
              users={users}
              meId={me?.id ?? -1}
            />
          </aside>
        )}
      </div>

      <AddParticipantDialog
        open={addOpen}
        onClose={() => setAddOpen(false)}
        chatId={chatId}
        existingUserIds={participants.map((p) => p.user_id)}
      />
    </section>
  )
}

function MessageList({
  sorted,
  meId,
  users,
}: {
  sorted: Message[]
  meId: number
  users: User[]
}) {
  const items: React.ReactNode[] = []
  let lastDate = ''
  for (let i = 0; i < sorted.length; i++) {
    const m = sorted[i]
    const dateLabel = formatDateLabel(m.created_at)
    if (dateLabel !== lastDate) {
      items.push(
        <div key={`d-${i}`} className="my-2 flex justify-center">
          <span className="rounded-full bg-tg-sidebar px-3 py-0.5 text-xs text-tg-mute">
            {dateLabel}
          </span>
        </div>,
      )
      lastDate = dateLabel
    }
    const prev = sorted[i - 1]
    const showAuthor = !prev || prev.user_id !== m.user_id || isNewAuthorBreak(prev, m)
    const isOwn = m.user_id === meId
    const isOptimistic = m.id < 0
    const author = users.find((u) => u.id === m.user_id)
    const authorName = author?.name?.trim() || author?.uniq_name || 'user'
    items.push(
      <MessageBubble
        key={m.id}
        message={m}
        showAuthor={showAuthor}
        isOwn={isOwn}
        isOptimistic={isOptimistic}
        authorName={authorName}
      />,
    )
  }
  return <>{items}</>
}

function isNewAuthorBreak(a: Message, b: Message) {
  return new Date(b.created_at).getTime() - new Date(a.created_at).getTime() > 60_000 * 5
}
