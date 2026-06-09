import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useCreateChat } from './useCreateChat'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { Dialog } from '../../components/Dialog'
import { Button } from '../../components/Button'

interface Props {
  open: boolean
  onClose: () => void
}

export function CreateChatDialog({ open, onClose }: Props) {
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const { data: me } = useCurrentUser()
  const { data: users = [] } = useQuery({ queryKey: qk.users, queryFn: api.users, enabled: open })
  const createChat = useCreateChat()

  const others = users.filter((u) => u.id !== me?.id)

  const toggle = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const submit = async () => {
    setError(null)
    if (!me) return
    if (selected.size === 0) {
      setError('Pick at least one user')
      return
    }
    const isGroup = selected.size > 1
    const finalName = isGroup
      ? name.trim() || 'Group chat'
      : users.find((u) => u.id === Array.from(selected)[0])?.uniq_name ?? 'Chat'
    try {
      const chat = await createChat.mutateAsync({
        name: finalName,
        participantUserIds: Array.from(new Set([me.id, ...selected])),
        meId: me.id,
      })
      setName('')
      setSelected(new Set())
      onClose()
      navigate({ to: '/chat/$chatId', params: { chatId: chat.id } })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to create chat')
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title="New chat"
      width="28rem"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={createChat.isPending}>
            {createChat.isPending ? 'Creating…' : 'Create'}
          </Button>
        </>
      }
    >
      <label className="mb-3 block text-sm font-medium text-tg-text">
        Group name <span className="text-tg-mute">(only for groups)</span>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Optional"
          className="mt-1 block w-full rounded-lg border border-tg-border bg-tg-bg px-3 py-2 outline-none focus:border-tg-accent"
        />
      </label>

      <div className="mb-1 text-sm font-medium text-tg-text">Members</div>
      <div className="max-h-64 overflow-y-auto rounded-lg border border-tg-border">
        {others.length === 0 && (
          <div className="px-3 py-2 text-sm text-tg-mute">No other users yet.</div>
        )}
        {others.map((u) => (
          <label
            key={u.id}
            className="flex cursor-pointer items-center gap-2 px-3 py-2 hover:bg-tg-sidebar"
          >
            <input
              type="checkbox"
              checked={selected.has(u.id)}
              onChange={() => toggle(u.id)}
              className="h-4 w-4 accent-tg-accent"
            />
            <div className="flex flex-col">
              <span className="text-sm text-tg-text">{u.name?.trim() || u.uniq_name}</span>
              {u.name && <span className="text-xs text-tg-mute">@{u.uniq_name}</span>}
            </div>
          </label>
        ))}
      </div>

      {error && <div className="mt-3 text-sm text-tg-danger">{error}</div>}
    </Dialog>
  )
}
