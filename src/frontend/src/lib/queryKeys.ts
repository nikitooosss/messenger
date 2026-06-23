export const qk = {
  me: ['me'] as const,
  users: ['users'] as const,
  chats: () => ['chats'] as const,
  chatSearch: (userId: number, q?: string) => ['chatSearch', userId, q] as const,
  chat: (id: number) => ['chat', id] as const,
  messagesRoot: ['messages'] as const,
  messages: (chatId: number) => ['messages', chatId] as const,
  participants: (chatId: number) => ['participants', chatId] as const,
}
