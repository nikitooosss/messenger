import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate, Link } from '@tanstack/react-router'
import { ApiError, api } from '../lib/apiClient'
import { qk } from '../lib/queryKeys'

export function LoginPage() {
  const [uniqName, setUniqName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const qc = useQueryClient()
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: () => api.login(uniqName, password),
    onSuccess: async () => {
      await qc.invalidateQueries({ queryKey: qk.me })
      await navigate({ to: '/' })
    },
    onError: (e) => {
      if (e instanceof ApiError && e.status === 401) {
        setError('Incorrect username or password')
      } else {
        setError('Login failed. Please try again.')
      }
    },
  })

  return (
    <div className="flex h-full items-center justify-center bg-tg-sidebar p-4">
      <form
        onSubmit={(e) => {
          e.preventDefault()
          setError(null)
          mutation.mutate()
        }}
        className="w-full max-w-sm rounded-2xl bg-tg-panel p-8 shadow-lg"
      >
        <h1 className="mb-1 text-2xl font-semibold text-tg-text">Sign in to Messenger</h1>
        <p className="mb-6 text-sm text-tg-mute">Welcome back.</p>

        <label className="mb-3 block text-sm font-medium text-tg-text">
          Username
          <input
            type="text"
            autoFocus
            autoComplete="username"
            value={uniqName}
            onChange={(e) => setUniqName(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-tg-border bg-tg-bg px-3 py-2 outline-none focus:border-tg-accent"
            required
          />
        </label>

        <label className="mb-4 block text-sm font-medium text-tg-text">
          Password
          <input
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-tg-border bg-tg-bg px-3 py-2 outline-none focus:border-tg-accent"
            required
          />
        </label>

        {error && <div className="mb-3 text-sm text-tg-danger">{error}</div>}

        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full rounded-lg bg-tg-accent px-4 py-2 font-medium text-white transition hover:bg-tg-accentHover disabled:opacity-50"
        >
          {mutation.isPending ? 'Signing in…' : 'Sign in'}
        </button>

        <p className="mt-4 text-center text-sm text-tg-mute">
          New here?{' '}
          <Link to="/register" className="text-tg-accent hover:underline">
            Create an account
          </Link>
        </p>
      </form>
    </div>
  )
}
