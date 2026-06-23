import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { qk } from '../../lib/queryKeys'
import type { Chat } from '../../types/models'

interface DeleteChatArgs {
  chat: Chat
}

export function useDeleteChat() {
  const { send } = useWebSocket()
  const qc = useQueryClient()
  const { data: me } = useCurrentUser()

  return useMutation({
    mutationFn: async ({ chat }: DeleteChatArgs): Promise<void> => {
      if (!me) throw new Error('Not authenticated')

      const chatId = chat.id

      qc.setQueryData<Chat[]>(qk.chats(), (old = []) =>
        old.filter((c) => c.id !== chatId),
      )
      qc.removeQueries({ queryKey: qk.chat(chatId) })
      qc.removeQueries({ queryKey: qk.messages(chatId) })
      qc.removeQueries({ queryKey: qk.participants(chatId) })

      send({
        type: 'chat_delete',
        chat,
        user_id: me.id,
      })
    },
  })
}
