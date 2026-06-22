import { useNavigate, useParams } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { formatDate, formatLastSeen } from '../../lib/time'
import { UserAvatar } from '../../components/UserAvatar'
import { useOnline } from '../presence/useOnline'
import { useCurrentUser } from '../../auth/useCurrentUser'
import type { Chat, ChatParticipant, ChatWithDisplayName, User } from '../../types/models'

interface ChatListItemProps {
  chat: Chat | ChatWithDisplayName
}

export function ChatListItem({ chat }: ChatListItemProps) {
  const navigate = useNavigate()
  const { chatId: activeId } = useParams({ strict: false }) as {
    chatId?: string | number
  }
  const isActive =
    activeId !== undefined && String(chat.id) === String(activeId)
  const { data: me } = useCurrentUser()

  const { data: participants = [] } = useQuery<ChatParticipant[]>({
    queryKey: qk.participants(chat.id),
    queryFn: () => api.participants(chat.id),
  })

  const { data: users = [] } = useQuery<User[]>({
    queryKey: qk.users,
    queryFn: api.users,
  })

  const { data: messages = [] } = useQuery({
    queryKey: qk.messages(chat.id),
    queryFn: () => api.messages(chat.id, 1),
  })

  const last = [...messages].sort((a, b) =>
    a.created_at.localeCompare(b.created_at),
  )[messages.length - 1]

  const peer = chat.is_group
    ? null
    : participants.find((p) => p.user_id !== me?.id) ?? null
  const peerUser = peer ? users.find((u) => u.id === peer.user_id) : null

  const peerOnline = useOnline(chat.is_group ? null : peerUser?.id)

  const displayName =
    'display_name' in chat
      ? chat.display_name
      : chat.is_group
        ? chat.name
        : peerUser?.name?.trim() || peerUser?.uniq_name || chat.name

  const previewAuthor = last
    ? users.find((u) => u.id === last.user_id)?.uniq_name ?? 'user'
    : null

  const subtitle = last
    ? `${previewAuthor}: ${last.content}`
    : chat.is_group
      ? `${participants.length} members`
      : peerOnline
        ? 'online'
        : peerUser
          ? formatLastSeen(peerUser.last_seen)
          : 'No messages yet'

  return (
    <button
      onClick={() => navigate({ to: '/chat/$chatId', params: { chatId: chat.id } })}
      className={`relative flex w-full items-center gap-3 px-3 py-2 pl-4 text-left transition ${
        isActive
          ? 'bg-tg-accent text-white'
          : 'hover:bg-tg-sidebarHover text-tg-text'
      }`}
    >
  
      {isActive && (
        <span
          aria-hidden
          className="absolute left-0 top-0 h-full w-[3px] bg-white"
        />
      )}
      {chat.is_group ? (
        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${
            isActive
              ? 'bg-white/20 text-white'
              : 'bg-tg-accent text-white'
          }`}
        >
          {chat.name.charAt(0).toUpperCase()}
        </div>
      ) : (
        <UserAvatar user={peerUser} size={40} showOnline maxInitials={1} />
      )}
      <div className="min-w-0 flex-1">
        <div className="flex items-center justify-between gap-2">
          <span
            className={`truncate font-medium ${
              isActive ? 'text-white' : 'text-tg-text'
            }`}
          >
            {displayName}
          </span>
          {last && (
            <span
              className={`shrink-0 text-xs ${
                isActive ? 'text-white/70' : 'text-tg-mute'
              }`}
            >
              {formatDate(last.created_at)}
            </span>
          )}
        </div>
        <div
          className={`truncate text-sm ${
            isActive ? 'text-white/80' : 'text-tg-mute'
          }`}
        >
          {last ? (
            subtitle
          ) : chat.is_group ? (
            `${participants.length} members`
          ) : peerOnline ? (
            <span
              className={isActive ? 'text-white' : 'text-tg-online'}
            >
              online
            </span>
          ) : peerUser ? (
            formatLastSeen(peerUser.last_seen)
          ) : (
            'No messages yet'
          )}
        </div>
      </div>
    </button>
  )
}
