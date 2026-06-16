import { useMutation } from '@tanstack/react-query'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { waitForNextChatCreated } from '../../lib/wsWait'
import type { ChatDetails, UserRole } from '../../types/models'

interface CreateGroupArgs {
  name: string
  participantUserIds: number[]
  meId: number
  chatType: 'personal' | 'group'
}

export function useCreateChat() {
  const { send } = useWebSocket()

  return useMutation({
    mutationFn: async ({
      name,
      participantUserIds,
      meId,
      chatType,
    }: CreateGroupArgs): Promise<ChatDetails> => {
      const isGroup = chatType === 'group'
      const finalName = isGroup ? name.trim() || 'Group chat' : name
      const participants = participantUserIds.map((userId) => ({
        chat_id: 0,
        user_id: userId,
        role: (isGroup ? (userId === meId ? 'admin' : 'member') : 'admin') as UserRole,
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
