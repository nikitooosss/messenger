import { useMutation } from '@tanstack/react-query'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { waitForNextChatCreated } from '../../lib/wsWait'
import type { ChatDetails, UserRole } from '../../types/models'

interface CreateGroupArgs {
  name: string
  participantUserIds: number[]
  meId: number
}

export function useCreateChat() {
  const { send } = useWebSocket()

  return useMutation({
    mutationFn: async ({
      name,
      participantUserIds,
      meId,
    }: CreateGroupArgs): Promise<ChatDetails> => {
      const isGroup = participantUserIds.length > 1
      const finalName = isGroup ? name.trim() || 'Group chat' : name
      const participants = participantUserIds.map((userId) => ({
        chat_id: 0,
        user_id: userId,
        role: (userId === meId ? 'admin' : 'member') as UserRole,
      }))

      const promise = waitForNextChatCreated((c) => c.name === finalName)

      send({
        type: 'chat_create',
        chat: { name: finalName, is_group: isGroup },
        participants,
      })

      return promise
    },
  })
}
