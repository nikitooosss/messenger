import { useQueryClient } from '@tanstack/react-query'
import { qk } from '../../lib/queryKeys'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { useCurrentUser } from '../../auth/useCurrentUser'
import type { Message } from '../../types/models'

export function useSendMessage(chatId: number) {
  const qc = useQueryClient()
  const { send } = useWebSocket()
  const { data: me } = useCurrentUser()

  return {
    send: (content: string) => {
      if (!me) return
      const trimmed = content.trim()
      if (!trimmed) return
      const tempId = -Date.now()
      const optimistic: Message = {
        id: tempId,
        chat_id: chatId,
        user_id: me.id,
        content: trimmed,
        created_at: new Date().toISOString(),
      }
      qc.setQueryData<Message[]>(qk.messages(chatId), (old = []) => [...old, optimistic])
      send({
        type: 'message_create',
        message: { chat_id: chatId, user_id: me.id, content: trimmed },
      })
    },
  }
}
