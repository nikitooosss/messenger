import { useMutation } from '@tanstack/react-query'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { useCurrentUser } from '../../auth/useCurrentUser'
import type { Chat } from '../../types/models'

interface DeleteChatArgs {
  chat: Chat
}

export function useDeleteChat() {
  const { send } = useWebSocket()
  const { data: me } = useCurrentUser()

  return useMutation({
    mutationFn: async ({ chat }: DeleteChatArgs): Promise<void> => {
      if (!me) throw new Error('Not authenticated')

      send({
        type: 'chat_delete',
        chat,
        user_id: me.id,
      })
    },
  })
}
