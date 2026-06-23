import type { ChatDetails, ChatParticipant } from '../types/models'

export interface ChatParticipantDelete {
  id: number
  chat_id: number
  user_id: number
}

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
let participantDeletedWaiters: Waiter<ChatParticipantDelete>[] = []

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

export function waitForNextParticipantDeleted(
  match: (p: ChatParticipantDelete) => boolean = () => true,
): Promise<ChatParticipantDelete> {
  return new Promise<ChatParticipantDelete>((resolve, reject) => {
    const timer = setTimeout(() => {
      participantDeletedWaiters = participantDeletedWaiters.filter((w) => w.timer !== timer)
      reject(new Error('Timed out waiting for chat_participant_deleted'))
    }, TIMEOUT_MS)
    participantDeletedWaiters.push({ match, resolve, reject, timer })
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

export function notifyParticipantDeleted(p: ChatParticipantDelete) {
  const remaining: Waiter<ChatParticipantDelete>[] = []
  for (const w of participantDeletedWaiters) {
    if (w.match(p)) {
      clearTimeout(w.timer)
      w.resolve(p)
    } else {
      remaining.push(w)
    }
  }
  participantDeletedWaiters = remaining
}

export function rejectPendingParticipantDeleted(reason: string) {
  for (const w of participantDeletedWaiters) {
    clearTimeout(w.timer)
    w.reject(new Error(reason))
  }
  participantDeletedWaiters = []
}
