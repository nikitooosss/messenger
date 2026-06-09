export type UserRole = 'admin' | 'member'

export interface User {
  id: number
  uniq_name: string
  name: string | null
  is_active: boolean
  avatar_url: string | null
  created_at: string
  last_seen: string
}

export interface Chat {
  id: number
  name: string
  is_group: boolean
  created_at: string
}

export interface ChatDetails extends Chat {
  participants: ChatParticipant[]
}

export interface ChatParticipant {
  id: number
  chat_id: number
  user_id: number
  role: UserRole
  joined_at: string
}

export interface Message {
  id: number
  chat_id: number
  user_id: number
  content: string
  created_at: string
}
