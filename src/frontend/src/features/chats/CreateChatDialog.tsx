import { useEffect, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useCreateChat } from './useCreateChat'
import { useChats } from './useChats'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { Dialog } from '../../components/Dialog'
import { Button } from '../../components/Button'
import { UserAvatar } from '../../components/UserAvatar'
import type { ChatParticipant } from '../../types/models'

interface Props {
  open: boolean
  onClose: () => void
}

export function CreateChatDialog({ open, onClose }: Props) {
  const [step, setStep] = useState<'type' | 'details'>('type')
  const [chatType, setChatType] = useState<'personal' | 'group' | null>(null)
  const [name, setName] = useState('')
  const [selected, setSelected] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const qc = useQueryClient()
  const { data: me } = useCurrentUser()
  const { data: users = [] } = useQuery({ queryKey: qk.users, queryFn: api.users, enabled: open })
  const { data: chats = [] } = useChats(me?.id)
  const createChat = useCreateChat()

  const others = users.filter((u) => u.id !== me?.id)

  const personalPeerIds = (() => {
    const ids = new Set<number>()
    if (!me) return ids
    for (const c of chats) {
      if (c.is_group) continue
      const parts = qc.getQueryData<ChatParticipant[]>(qk.participants(c.id))
      if (!parts) continue
      const peer = parts.find((p) => p.user_id !== me.id)
      if (peer) ids.add(peer.user_id)
    }
    return ids
  })()

  useEffect(() => {
    if (!open || !me) return
    for (const c of chats) {
      if (c.is_group) continue
      if (qc.getQueryData(qk.participants(c.id))) continue
      qc.prefetchQuery({
        queryKey: qk.participants(c.id),
        queryFn: () => api.participants(c.id),
      })
    }
  }, [open, me, chats, qc])

  const visibleOthers = chatType === 'personal'
    ? others.filter((u) => !personalPeerIds.has(u.id))
    : others

  const reset = () => {
    setStep('type')
    setChatType(null)
    setName('')
    setSelected(new Set())
    setError(null)
  }

  const handleClose = () => {
    reset()
    onClose()
  }

  const selectType = (type: 'personal' | 'group') => {
    setChatType(type)
    setStep('details')
    setError(null)
  }

  const toggle = (id: number) => {
    setError(null)
    if (chatType === 'personal') {
      setSelected(new Set([id]))
      const user = users.find((u) => u.id === id)
      if (user) setName(user.uniq_name)
      return
    }
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
    if (chatType === 'group' && !name.trim()) {
      setError('Enter a chat name')
      return
    }
    const finalName = chatType === 'group'
      ? name.trim()
      : 'personal_chat'
    try {
      const chat = await createChat.mutateAsync({
        name: finalName,
        participantUserIds: Array.from(new Set([me.id, ...selected])),
        meId: me.id,
        chatType,
      })
      reset()
      onClose()
      navigate({ to: '/chat/$chatId', params: { chatId: chat.id } })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to create chat')
    }
  }

  const title = step === 'type' ? 'New chat' : chatType === 'personal' ? 'New personal chat' : 'New group chat'

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      title={title}
      width="28rem"
      footer={
        step === 'details' ? (
          <>
            <Button variant="secondary" onClick={() => { setStep('type'); setSelected(new Set()); setName(''); setError(null) }}>
              Back
            </Button>
            <Button onClick={submit} disabled={createChat.isPending}>
              {createChat.isPending ? 'Creating…' : 'Create'}
            </Button>
          </>
        ) : (
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
        )
      }
    >
      {step === 'type' ? (
        <div className="flex flex-col gap-3">
          <button
            onClick={() => selectType('personal')}
            className="flex items-center gap-4 rounded-lg border border-tg-border p-4 text-left transition hover:border-tg-accent hover:bg-tg-accent/5"
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-tg-accent text-lg font-semibold text-white">
              1
            </div>
            <div>
              <div className="font-medium text-tg-text">Personal chat</div>
              <div className="text-sm text-tg-mute">Direct message with one user</div>
            </div>
          </button>
          <button
            onClick={() => selectType('group')}
            className="flex items-center gap-4 rounded-lg border border-tg-border p-4 text-left transition hover:border-tg-accent hover:bg-tg-accent/5"
          >
            <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-tg-accent text-lg font-semibold text-white">
              #
            </div>
            <div>
              <div className="font-medium text-tg-text">Group chat</div>
              <div className="text-sm text-tg-mute">Chat with multiple users</div>
            </div>
          </button>
        </div>
      ) : (
        <>
          {chatType === 'group' && (
            <label className="mb-3 block text-sm font-medium text-tg-text">
              Chat name
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter chat name"
                className="mt-1 block w-full rounded-lg border border-tg-border bg-tg-bg px-3 py-2 outline-none focus:border-tg-accent"
              />
            </label>
          )}

          <div className="mb-1 text-sm font-medium text-tg-text">
            {chatType === 'personal' ? 'Select user' : 'Select members'}
          </div>
          <div className="max-h-64 overflow-y-auto rounded-lg border border-tg-border">
            {visibleOthers.length === 0 && (
              <div className="px-3 py-2 text-sm text-tg-mute">
                {chatType === 'personal'
                  ? 'No available users for a new personal chat.'
                  : 'No other users yet.'}
              </div>
            )}
            {visibleOthers.map((u) => (
              <label
                key={u.id}
                className={`flex cursor-pointer items-center gap-3 px-3 py-2 hover:bg-tg-sidebar ${
                  selected.has(u.id) ? 'bg-tg-accent/10' : ''
                }`}
              >
                {chatType === 'personal' ? (
                  <input
                    type="radio"
                    name="personal-user"
                    checked={selected.has(u.id)}
                    onChange={() => toggle(u.id)}
                    className="h-4 w-4 accent-tg-accent"
                  />
                ) : (
                  <input
                    type="checkbox"
                    checked={selected.has(u.id)}
                    onChange={() => toggle(u.id)}
                    className="h-4 w-4 accent-tg-accent"
                  />
                )}
                <UserAvatar user={u} size={32} />
                <div className="flex flex-col">
                  <span className="text-sm text-tg-text">{u.name?.trim() || u.uniq_name}</span>
                  {u.name && <span className="text-xs text-tg-mute">@{u.uniq_name}</span>}
                </div>
              </label>
            ))}
          </div>
        </>
      )}

      {error && <div className="mt-3 text-sm text-tg-danger">{error}</div>}
    </Dialog>
  )
}
