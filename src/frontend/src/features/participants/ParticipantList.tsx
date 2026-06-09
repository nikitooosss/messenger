import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { UserAvatar } from '../../components/UserAvatar'
import type { ChatParticipant, User } from '../../types/models'

interface Props {
  chatId: number
  participants: ChatParticipant[]
  users: User[]
  meId: number
}

export function ParticipantList({ chatId, participants, users, meId }: Props) {
  const qc = useQueryClient()
  const { send } = useWebSocket()

  const remove = useMutation({
    mutationFn: (id: number) => api.removeParticipant(id),
    onMutate: async (id) => {
      await qc.cancelQueries({ queryKey: qk.participants(chatId) })
      const previous = qc.getQueryData<ChatParticipant[]>(qk.participants(chatId))
      qc.setQueryData<ChatParticipant[]>(qk.participants(chatId), (old = []) =>
        old.filter((p) => p.id !== id),
      )
      const removed = previous?.find((p) => p.id === id)
      return { previous, removed }
    },
    onError: (_e, _id, ctx) => {
      if (ctx?.previous) qc.setQueryData(qk.participants(chatId), ctx.previous)
    },
    onSettled: (_data, _err, id) => {
      const removed = participants.find((p) => p.id === id)
      if (removed) {
        send({
          type: 'chat_participant_delete',
          chat_participant: removed,
        })
      }
    },
  })

  return (
    <ul className="flex-1 overflow-y-auto">
      {participants.map((p) => {
        const u = users.find((x) => x.id === p.user_id)
        const canRemove = p.role === 'member' || p.user_id !== meId
        return (
          <li
            key={p.id}
            className="flex items-center gap-3 border-b border-tg-border px-3 py-2"
          >
            <UserAvatar user={u ?? null} size={32} showOnline />
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm text-tg-text">
                {u?.name?.trim() || u?.uniq_name || `user #${p.user_id}`}
                {p.user_id === meId && (
                  <span className="ml-1 text-xs text-tg-mute">(you)</span>
                )}
              </div>
              <div className="truncate text-xs text-tg-mute">
                {p.role}
                {u && ` · @${u.uniq_name}`}
              </div>
            </div>
            {canRemove && p.user_id !== meId && (
              <button
                onClick={() => remove.mutate(p.id)}
                disabled={remove.isPending}
                className="text-xs text-tg-danger hover:underline"
                title="Remove from chat"
              >
                Remove
              </button>
            )}
          </li>
        )
      })}
    </ul>
  )
}
