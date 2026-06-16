import { useMutation, useQueryClient } from '@tanstack/react-query'
import { qk } from '../../lib/queryKeys'
import { useWebSocket } from '../../ws/WebSocketProvider'
import { useCurrentUser } from '../../auth/useCurrentUser'
import type { Message } from '../../types/models'

interface SendMessageInput {
  content: string
}

export function useSendMessage(chatId: number) {
  const qc = useQueryClient()
  const { send: wsSend } = useWebSocket()
  const { data: me } = useCurrentUser()

  const mutation = useMutation<
    void,
    Error,
    SendMessageInput,
    { previous: Message[] | undefined }
  >({
    mutationFn: () => Promise.resolve(),

    onMutate: async ({ content }) => {
      if (!me) return { previous: undefined }
      const trimmed = content.trim()
      if (!trimmed) return { previous: undefined }
      const tempId = -Date.now()

      const optimistic: Message = {
        id: tempId,
        chat_id: chatId,
        user_id: me.id,
        content: trimmed,
        created_at: new Date().toISOString(),
      }

      await qc.cancelQueries({ queryKey: qk.messages(chatId) })
      const previous = qc.getQueryData<Message[]>(qk.messages(chatId))
      qc.setQueryData<Message[]>(qk.messages(chatId), (old = []) => [...old, optimistic])

      wsSend({
        type: 'message_create',
        message: {
          chat_id: chatId,
          user_id: me.id,
          content: trimmed,
        },
      })

      return { previous }
    },

    onError: (_err, _vars, ctx) => {
      if (ctx?.previous !== undefined) {
        qc.setQueryData(qk.messages(chatId), ctx.previous)
      }
    },
  })

  return {
    send: mutation.mutate,
    isPending: mutation.isPending,
    error: mutation.error,
  }
}
