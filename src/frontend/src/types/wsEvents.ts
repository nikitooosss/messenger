import type {
  Chat,
  ChatDetails,
  ChatParticipant,
  Message,
  User,
  UserRole,
} from './models'

export interface MessagePostPayload {
  chat_id: number
  user_id: number
  content: string
}

export interface MessagePatchPayload {
  id: number
  content?: string
}

export interface ChatPostPayload {
  name: string
  is_group: boolean
}

export interface ChatPatchPayload {
  id: number
  name?: string
}

export interface ParticipantPostPayload {
  chat_id: number
  user_id: number
  role: UserRole
}

export interface ParticipantPatchPayload {
  id: number
  role?: UserRole
}

export type ClientEvent =
  | { type: 'message_create'; message: MessagePostPayload }
  | { type: 'message_update'; message: MessagePatchPayload }
  | { type: 'message_delete'; message: Message }
  | { type: 'chat_create'; chat: ChatPostPayload; participants: ParticipantPostPayload[] }
  | { type: 'chat_update'; chat: ChatPatchPayload }
  | { type: 'chat_delete'; chat: Chat; user_id: number }
  | { type: 'chat_participant_create'; chat_participant: ParticipantPostPayload }
  | { type: 'chat_participant_update'; chat_participant: ParticipantPatchPayload }
  | { type: 'chat_participant_delete'; chat_participant: ChatParticipant }
  | { type: 'user_start_typing'; user_id: number; chat_id: number }
  | { type: 'user_stop_typing'; user_id: number; chat_id: number }

export type ServerEvent =
  | { type: 'message_created'; message: Message }
  | { type: 'message_updated'; message: Message }
  | { type: 'message_deleted'; message: { id: number } }
  | { type: 'chat_created'; chat: ChatDetails; participants: ChatParticipant[] }
  | { type: 'chat_updated'; chat: Chat }
  | { type: 'chat_deleted'; chat: { id: number }; participants: ChatParticipant[] }
  | { type: 'chat_participant_created'; chat_participant: ChatParticipant }
  | { type: 'chat_participant_updated'; chat_participant: ChatParticipant }
  | { type: 'chat_participant_deleted'; chat_participant: { id: number; chat_id: number; user_id: number } }
  | { type: 'user_online'; user: User }
  | { type: 'user_offline'; user: User }
  | { type: 'presence_roster'; user_ids: number[] }
  | { type: 'user_start_typing'; user_id: number; chat_id: number }
  | { type: 'user_stop_typing'; user_id: number; chat_id: number }
  | { type: 'error'; message: string }

export type AnyEvent = ClientEvent | ServerEvent

export type PresenceEvent = Extract<
  ServerEvent,
  {
    type:
      | 'user_online'
      | 'user_offline'
      | 'user_start_typing'
      | 'user_stop_typing'
  }
>
