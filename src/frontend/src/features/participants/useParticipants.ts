import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'

export function useParticipants(chatId: number) {
  return useQuery({
    queryKey: qk.participants(chatId),
    queryFn: () => api.participants(chatId),
  })
}
