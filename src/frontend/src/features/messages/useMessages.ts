import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'

export function useMessages(chatId: number) {
  return useQuery({
    queryKey: qk.messages(chatId),
    queryFn: () => api.messages(chatId, 100),
    refetchOnMount: 'always',
  })
}
