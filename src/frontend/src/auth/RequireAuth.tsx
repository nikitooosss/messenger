import type { QueryClient } from '@tanstack/react-query'
import { redirect } from '@tanstack/react-router'
import { ApiError, api } from '../lib/apiClient'
import { qk } from '../lib/queryKeys'

export async function ensureAuthenticated(qc: QueryClient) {
  try {
    return await qc.fetchQuery({
      queryKey: qk.me,
      queryFn: api.me,
      staleTime: 5 * 60_000,
    })
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) {
      throw redirect({ to: '/login' })
    }
    throw e
  }
}
