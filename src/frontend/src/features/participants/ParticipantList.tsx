import { useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { UserAvatar } from '../../components/UserAvatar'
import { useOnline } from '../presence/useOnline'
import { formatLastSeen } from '../../lib/time'
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
      const removed = previous?.find((p) => p.id === id)
      qc.setQueryData<ChatParticipant[]>(qk.participants(chatId), (old = []) =>
        old.filter((p) => p.id !== id),
      )
      return { previous, removed }
    },
    onError: (_e, _id, ctx) => {
      if (ctx?.previous) qc.setQueryData(qk.participants(chatId), ctx.previous)
    },
    onSettled: (_data, _err, _id, ctx) => {
      if (ctx?.removed) {
        send({
          type: 'chat_participant_delete',
          chat_participant: ctx.removed,
        })
      }
    },
  })

  const myParticipant = participants.find((p) => p.user_id === meId)
  const isAdmin = myParticipant?.role === 'admin'

  return (
    <ul className="flex-1 overflow-y-auto">
      {participants.map((p) => {
        const u = users.find((x) => x.id === p.user_id)
        const canRemove = isAdmin && p.user_id !== meId
        return (
          <ParticipantRow
            key={p.id}
            participant={p}
            user={u ?? null}
            meId={meId}
            canRemove={canRemove}
            onRemove={() => remove.mutate(p.id)}
            isPending={remove.isPending}
          />
        )
      })}
    </ul>
  )
}

interface ParticipantRowProps {
  participant: ChatParticipant
  user: User | null
  meId: number
  canRemove: boolean
  onRemove: () => void
  isPending: boolean
}

function ParticipantRow({ participant, user, meId, canRemove, onRemove, isPending }: ParticipantRowProps) {
  const online = useOnline(user?.id)

  return (
    <li className="flex items-center gap-3 border-b border-tg-border px-3 py-2">
      <UserAvatar user={user} size={32} showOnline />
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm text-tg-text">
          {user?.name?.trim() || user?.uniq_name || `user #${participant.user_id}`}
          {participant.user_id === meId && (
            <span className="ml-1 text-xs text-tg-mute">(you)</span>
          )}
        </div>
        <div className="truncate text-xs text-tg-mute">
          {online ? (
            <>
              <span className="text-tg-online">online</span>
              <span> · {participant.role}</span>
            </>
          ) : (
            <>
              {participant.role}
              {user && ` · @${user.uniq_name}`}
            </>
          )}
        </div>
        {!online && user && (
          <div className="truncate text-xs text-tg-mute">
            {formatLastSeen(user.last_seen)}
          </div>
        )}
      </div>
      {canRemove && (
        <button
          onClick={onRemove}
          disabled={isPending}
          className="text-xs text-tg-danger hover:underline"
          title="Remove from chat"
        >
          Remove
        </button>
      )}
    </li>
  )
}
