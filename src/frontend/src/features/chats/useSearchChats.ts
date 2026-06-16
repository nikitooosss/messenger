import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'

export function useSearchChats(userId: number | undefined, query: string) {
  return useQuery({
    queryKey: qk.chatSearch(userId ?? 0, query),
    queryFn: () => api.searchChats(userId!, query || undefined),
    enabled: userId != null && query.length > 0,
    placeholderData: (prev) => prev,
  })
}
