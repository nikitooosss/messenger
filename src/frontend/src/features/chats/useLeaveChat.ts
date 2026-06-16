import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { qk } from '../../lib/queryKeys'
import type { Chat, ChatParticipant } from '../../types/models'

interface LeaveChatArgs {
  chatId: number
}

export function useLeaveChat() {
  const { send } = useWebSocket()
  const qc = useQueryClient()
  const { data: me } = useCurrentUser()

  return useMutation({
    mutationFn: async ({ chatId }: LeaveChatArgs): Promise<void> => {
      if (!me) throw new Error('Not authenticated')

      const participants = qc.getQueryData<ChatParticipant[]>(qk.participants(chatId))
      const myParticipant = participants?.find((p) => p.user_id === me.id)

      if (!myParticipant) throw new Error('Not a participant of this chat')

      // Remove from cache optimistically
      qc.setQueryData<ChatParticipant[]>(qk.participants(chatId), (old = []) =>
        old.filter((p) => p.id !== myParticipant.id),
      )

      // Remove chat from list
      qc.setQueryData<Chat[]>(qk.chats(), (old = []) =>
        old.filter((c) => c.id !== chatId),
      )

      // Remove related queries
      qc.removeQueries({ queryKey: qk.chat(chatId) })
      qc.removeQueries({ queryKey: qk.messages(chatId) })
      qc.removeQueries({ queryKey: qk.participants(chatId) })

      send({
        type: 'chat_participant_delete',
        chat_participant: myParticipant,
      })
    },
  })
}
