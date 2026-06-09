import { useQuery } from '@tanstack/react-query'
import { api } from '../lib/apiClient'
import { qk } from '../lib/queryKeys'

export function useCurrentUser() {
  return useQuery({
    queryKey: qk.me,
    queryFn: api.me,
    retry: false,
    staleTime: 5 * 60_000,
  })
}
