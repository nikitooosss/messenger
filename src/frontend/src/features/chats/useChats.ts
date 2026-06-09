import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'

export function useChats(userId: number | undefined) {
  return useQuery({
    queryKey: qk.chats(),
    queryFn: () => api.chats(userId!),
    enabled: userId != null,
  })
}
