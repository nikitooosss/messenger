import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate, Link } from '@tanstack/react-router'
import { ApiError, api } from '../lib/apiClient'

export function RegisterPage() {
  const [uniqName, setUniqName] = useState('')
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  const mutation = useMutation({
    mutationFn: () =>
      api.register({
        uniq_name: uniqName,
        name: name || undefined,
        password_hash: password,
      }),
    onSuccess: () => navigate({ to: '/login' }),
    onError: (e) => {
      if (e instanceof ApiError && e.status === 409) {
        setError('A user with that username already exists')
      } else {
        setError('Registration failed. Please try again.')
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
        <h1 className="mb-1 text-2xl font-semibold text-tg-text">Create account</h1>
        <p className="mb-6 text-sm text-tg-mute">Join the conversation.</p>

        <label className="mb-3 block text-sm font-medium text-tg-text">
          Username
          <input
            type="text"
            autoFocus
            value={uniqName}
            onChange={(e) => setUniqName(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-tg-border bg-tg-bg px-3 py-2 outline-none focus:border-tg-accent"
            required
          />
        </label>

        <label className="mb-3 block text-sm font-medium text-tg-text">
          Display name <span className="text-tg-mute">(optional)</span>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-tg-border bg-tg-bg px-3 py-2 outline-none focus:border-tg-accent"
          />
        </label>

        <label className="mb-4 block text-sm font-medium text-tg-text">
          Password
          <input
            type="password"
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
          {mutation.isPending ? 'Creating…' : 'Create account'}
        </button>

        <p className="mt-4 text-center text-sm text-tg-mute">
          Already have an account?{' '}
          <Link to="/login" className="text-tg-accent hover:underline">
            Sign in
          </Link>
        </p>
      </form>
    </div>
  )
}
