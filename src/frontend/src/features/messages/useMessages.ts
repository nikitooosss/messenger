import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import type { Message } from '../../types/models'

export function useMessages(chatId: number) {
  const qc = useQueryClient()

  return useQuery<Message[]>({
    queryKey: qk.messages(chatId),
    queryFn: async () => {
      const serverMessages = await api.messages(chatId, 100)
      const merged = qc.getQueryData<Message[]>(qk.messages(chatId)) ?? serverMessages
      const knownRealIds = new Set(serverMessages.map((m) => m.id))
      const optimistics = merged.filter((m) => m.id < 0)
      const realFromOld = merged.filter(
        (m) => m.id > 0 && !knownRealIds.has(m.id),
      )
      return [...serverMessages, ...realFromOld, ...optimistics]
    },
    refetchOnMount: 'always',
    refetchOnWindowFocus: true,
    refetchOnReconnect: 'always',
  })
}
