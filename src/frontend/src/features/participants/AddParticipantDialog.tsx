import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { waitForNextParticipantCreated } from '../../lib/wsWait'
import { Dialog } from '../../components/Dialog'
import { Button } from '../../components/Button'
import { UserAvatar } from '../../components/UserAvatar'

interface Props {
  open: boolean
  onClose: () => void
  chatId: number
  existingUserIds: number[]
}

export function AddParticipantDialog({ open, onClose, chatId, existingUserIds }: Props) {
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const { data: users = [] } = useQuery({ queryKey: qk.users, queryFn: api.users, enabled: open })
  const { send } = useWebSocket()

  const candidates = users.filter((u) => !existingUserIds.includes(u.id))

  const toggle = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const submit = async () => {
    if (selected.size === 0) {
      setError('Pick at least one user')
      return
    }
    setBusy(true)
    setError(null)
    try {
      for (const userId of selected) {
        const wait = waitForNextParticipantCreated(
          (p) => p.chat_id === chatId && p.user_id === userId,
        )
        send({
          type: 'chat_participant_create',
          chat_participant: { chat_id: chatId, user_id: userId, role: 'member' },
        })
        await wait
      }
      setSelected(new Set())
      onClose()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to add member')
    } finally {
      setBusy(false)
    }
  }

  return (
    <Dialog
      open={open}
      onClose={onClose}
      title="Add members"
      width="24rem"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={submit} disabled={busy}>
            {busy ? 'Adding…' : 'Add'}
          </Button>
        </>
      }
    >
      <div className="max-h-72 overflow-y-auto rounded-lg border border-tg-border">
        {candidates.length === 0 && (
          <div className="px-3 py-2 text-sm text-tg-mute">No users to add.</div>
        )}
        {candidates.map((u) => (
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
            <UserAvatar user={u} size={28} />
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
