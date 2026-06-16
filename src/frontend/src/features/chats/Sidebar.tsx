import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { useChats } from './useChats'
import { useSearchChats } from './useSearchChats'
import { ChatListItem } from './ChatListItem'
import { CreateChatDialog } from './CreateChatDialog'
import { UserAvatar } from '../../components/UserAvatar'
import { Spinner } from '../../components/Spinner'
import { Button } from '../../components/Button'

export function Sidebar() {
  const { data: me } = useCurrentUser()
  const navigate = useNavigate()
  const [search, setSearch] = useState('')
  const [createOpen, setCreateOpen] = useState(false)
  const { data: chats, isLoading: isLoadingChats } = useChats(me?.id)
  const { data: searchResults, isLoading: isLoadingSearch } = useSearchChats(
    me?.id,
    search,
  )

  const isSearching = search.length > 0
  const filtered = isSearching ? (searchResults ?? []) : (chats ?? [])
  const isLoading = isSearching ? isLoadingSearch : isLoadingChats

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-r border-tg-border bg-tg-sidebar">
      <div className="flex items-center justify-between gap-2 border-b border-tg-border px-4 py-3">
        <button
          onClick={() => navigate({ to: '/' })}
          className="flex min-w-0 items-center gap-2"
        >
          <UserAvatar user={me} size={36} showOnline />
          <div className="min-w-0 text-left">
            <div className="truncate text-sm font-medium text-tg-text">
              {me?.name?.trim() || me?.uniq_name}
            </div>
            <div className="truncate text-xs text-tg-mute">@{me?.uniq_name}</div>
          </div>
        </button>
        <Button variant="ghost" onClick={() => setCreateOpen(true)} title="New chat">
          +
        </Button>
      </div>

      <div className="border-b border-tg-border px-3 py-2">
        <input
          type="text"
          placeholder="Search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full rounded-lg border border-tg-border bg-tg-bg px-3 py-1.5 text-sm outline-none focus:border-tg-accent"
        />
      </div>

      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <div className="flex h-full items-center justify-center">
            <Spinner />
          </div>
        ) : filtered.length === 0 ? (
          <div className="px-4 py-8 text-center text-sm text-tg-mute">
            {chats && chats.length > 0
              ? 'No chats match your search'
              : 'No chats yet. Click + to start one.'}
          </div>
        ) : (
          <ul>
            {filtered.map((chat) => (
              <li key={chat.id}>
                <ChatListItem chat={chat} />
              </li>
            ))}
          </ul>
        )}
      </div>

      <CreateChatDialog open={createOpen} onClose={() => setCreateOpen(false)} />
    </aside>
  )
}
