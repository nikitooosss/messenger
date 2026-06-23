import type {
  Chat,
  ChatDetails,
  ChatParticipant,
  ChatWithDisplayName,
  Message,
  User,
  UserRole,
} from '../types/models'

export class ApiError extends Error {
  constructor(
    public status: number,
    public bodyText: string,
  ) {
    super(`HTTP ${status}: ${bodyText}`)
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }
  const res = await fetch(path, {
    credentials: 'include',
    ...init,
    headers,
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new ApiError(res.status, text)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

export const api = {
  register: (body: { uniq_name: string; name?: string; password_hash: string }) =>
    request<User>('/api/auth/register', { method: 'POST', body: JSON.stringify(body) }),

  login: (uniq_name: string, password: string) =>
    request<{ status: number }>('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ username: uniq_name, password }).toString(),
    }),

  me: () => request<User>('/api/user/me'),
  users: () => request<User[]>('/api/user/get'),
  user: (id: number) => request<User>(`/api/user/get/${id}`),

  chats: (userId: number) => request<Chat[]>(`/api/chat/get?user_id=${userId}`),
  searchChats: (userId: number, q?: string) =>
    request<ChatWithDisplayName[]>(
      `/api/chat/search?user_id=${userId}${q ? `&q=${encodeURIComponent(q)}` : ''}`,
    ),
  chat: (id: number) => request<ChatDetails>(`/api/chat/get/${id}`),
  createChat: (b: { name: string; is_group: boolean }) =>
    request<Chat>('/api/chat/create', { method: 'POST', body: JSON.stringify(b) }),

  messages: (chatId: number, limit = 100) =>
    request<Message[]>(`/api/message/get?chat_id=${chatId}&limit=${limit}`),
  createMessage: (b: { chat_id: number; user_id: number; content: string }) =>
    request<Message>('/api/message/create', { method: 'POST', body: JSON.stringify(b) }),
  updateMessage: (id: number, content: string) =>
    request<Message>(`/api/message/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ id, content }),
    }),
  deleteMessage: (id: number) =>
    request<void>(`/api/message/${id}`, { method: 'DELETE' }),

  participants: (chatId: number) =>
    request<ChatParticipant[]>(`/api/chat_participant/get?chat_id=${chatId}`),
  addParticipant: (b: { chat_id: number; user_id: number; role: UserRole }) =>
    request<ChatParticipant>('/api/chat_participant/create', {
      method: 'POST',
      body: JSON.stringify(b),
    }),
  removeParticipant: (id: number) =>
    request<void>(`/api/chat_participant/${id}`, { method: 'DELETE' }),
}
