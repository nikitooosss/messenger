import type { ChatDetails, ChatParticipant } from '../types/models'

type Resolver<T> = (value: T) => void
type Rejecter = (reason?: unknown) => void

interface Waiter<T> {
  match: (v: T) => boolean
  resolve: Resolver<T>
  reject: Rejecter
  timer: ReturnType<typeof setTimeout>
}

const TIMEOUT_MS = 15_000

let chatCreatedWaiters: Waiter<ChatDetails>[] = []
let participantCreatedWaiters: Waiter<ChatParticipant>[] = []

export function waitForNextChatCreated(
  match: (chat: ChatDetails) => boolean = () => true,
): Promise<ChatDetails> {
  return new Promise<ChatDetails>((resolve, reject) => {
    const timer = setTimeout(() => {
      chatCreatedWaiters = chatCreatedWaiters.filter((w) => w.timer !== timer)
      reject(new Error('Timed out waiting for chat_created'))
    }, TIMEOUT_MS)
    chatCreatedWaiters.push({ match, resolve, reject, timer })
  })
}

export function waitForNextParticipantCreated(
  match: (p: ChatParticipant) => boolean = () => true,
): Promise<ChatParticipant> {
  return new Promise<ChatParticipant>((resolve, reject) => {
    const timer = setTimeout(() => {
      participantCreatedWaiters = participantCreatedWaiters.filter((w) => w.timer !== timer)
      reject(new Error('Timed out waiting for chat_participant_created'))
    }, TIMEOUT_MS)
    participantCreatedWaiters.push({ match, resolve, reject, timer })
  })
}

export function notifyChatCreated(chat: ChatDetails) {
  const remaining: Waiter<ChatDetails>[] = []
  for (const w of chatCreatedWaiters) {
    if (w.match(chat)) {
      clearTimeout(w.timer)
      w.resolve(chat)
    } else {
      remaining.push(w)
    }
  }
  chatCreatedWaiters = remaining
}

export function notifyParticipantCreated(p: ChatParticipant) {
  const remaining: Waiter<ChatParticipant>[] = []
  for (const w of participantCreatedWaiters) {
    if (w.match(p)) {
      clearTimeout(w.timer)
      w.resolve(p)
    } else {
      remaining.push(w)
    }
  }
  participantCreatedWaiters = remaining
}
