import { QueryClient } from '@tanstack/react-query'
import { qk } from '../lib/queryKeys'
import { notifyChatCreated, notifyParticipantCreated } from '../lib/wsWait'
import { seedOnlineFromRoster } from '../features/presence/useOnline'
import type { Chat, ChatParticipant, Message, User } from '../types/models'
import type { ServerEvent } from '../types/wsEvents'
import { presenceBus } from '../features/presence/presenceStore'

export function handleWsEvent(ev: ServerEvent, qc: QueryClient): void {
  switch (ev.type) {
    case 'message_created': {
      qc.setQueryData<Message[]>(qk.messages(ev.message.chat_id), (old = []) => {
        const real = ev.message
        if (old.some((m) => m.id === real.id)) return old
        const idx = old.findIndex(
          (m) => m.id < 0 && m.user_id === real.user_id,
        )
        if (idx === -1) return [...old, real]
        const next = old.slice()
        next[idx] = real
        return next
      })
      break
    }

    case 'message_updated': {
      qc.setQueryData<Message[]>(qk.messages(ev.message.chat_id), (old = []) =>
        old.map((m) => (m.id === ev.message.id ? ev.message : m)),
      )
      break
    }

    case 'message_deleted': {
      qc.getQueriesData<Message[]>({ queryKey: qk.messagesRoot }).forEach(([key, list]) => {
        if (!list) return
        qc.setQueryData<Message[]>(
          key,
          list.filter((m) => m.id !== ev.message.id),
        )
      })
      break
    }

    case 'chat_created': {
      const flat: Chat = {
        id: ev.chat.id,
        name: ev.chat.name,
        is_group: ev.chat.is_group,
        created_at: ev.chat.created_at,
      }
      qc.setQueryData<Chat[]>(qk.chats(), (old = []) =>
        old.some((c) => c.id === flat.id) ? old : [flat, ...old],
      )
      qc.setQueryData(qk.chat(flat.id), flat)
      qc.setQueryData<ChatParticipant[]>(qk.participants(flat.id), ev.participants)
      notifyChatCreated(ev.chat)
      break
    }

    case 'chat_updated': {
      qc.setQueryData<Chat[]>(qk.chats(), (old = []) =>
        old.map((c) => (c.id === ev.chat.id ? { ...c, ...ev.chat } : c)),
      )
      qc.setQueryData<Chat>(qk.chat(ev.chat.id), (old) =>
        old ? { ...old, ...ev.chat } : old,
      )
      break
    }

    case 'chat_deleted': {
      qc.setQueryData<Chat[]>(qk.chats(), (old = []) =>
        old.filter((c) => c.id !== ev.chat.id),
      )
      qc.invalidateQueries({ queryKey: qk.chats() })
      qc.removeQueries({ queryKey: qk.chat(ev.chat.id) })
      qc.removeQueries({ queryKey: qk.messages(ev.chat.id) })
      qc.removeQueries({ queryKey: qk.participants(ev.chat.id) })
      break
    }

    case 'chat_participant_created': {
      qc.setQueryData<ChatParticipant[]>(
        qk.participants(ev.chat_participant.chat_id),
        (old = []) =>
          old.some((p) => p.id === ev.chat_participant.id)
            ? old
            : [...old, ev.chat_participant],
      )
      notifyParticipantCreated(ev.chat_participant)
      break
    }

    case 'chat_participant_updated': {
      qc.setQueryData<ChatParticipant[]>(
        qk.participants(ev.chat_participant.chat_id),
        (old = []) =>
          old.map((p) => (p.id === ev.chat_participant.id ? ev.chat_participant : p)),
      )
      break
    }

    case 'chat_participant_deleted': {
      qc.setQueryData<ChatParticipant[]>(
        qk.participants(ev.chat_participant.chat_id),
        (old = []) => old.filter((p) => p.id !== ev.chat_participant.id),
      )
      break
    }

    case 'presence_roster': {
      seedOnlineFromRoster(ev.user_ids)
      break
    }

    case 'user_online':
    case 'user_offline':
      qc.setQueryData<User[]>(qk.users, (old = []) =>
        old.length === 0
          ? old
          : old.map((u) => (u.id === ev.user.id ? ev.user : u)),
      )
      presenceBus.emit(ev)
      break

    case 'user_start_typing':
    case 'user_stop_typing':
      presenceBus.emit(ev)
      break

    case 'error':
      console.error('[WS server error]', ev.message)
      break
  }
}
