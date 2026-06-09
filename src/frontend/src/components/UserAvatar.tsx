import { useOnline } from '../features/presence/useOnline'
import type { User } from '../types/models'

interface UserAvatarProps {
  user?: Pick<User, 'id' | 'name' | 'uniq_name' | 'avatar_url'> | null
  size?: number
  showOnline?: boolean
}

function initials(u: UserAvatarProps['user']): string {
  if (!u) return '?'
  const src = u.name?.trim() || u.uniq_name || '?'
  return src.slice(0, 2).toUpperCase()
}

function hue(u: UserAvatarProps['user']): number {
  if (!u) return 200
  const src = u.name || u.uniq_name || ''
  let h = 0
  for (let i = 0; i < src.length; i++) h = (h * 31 + src.charCodeAt(i)) % 360
  return h
}

export function UserAvatar({ user, size = 40, showOnline = false }: UserAvatarProps) {
  const online = useOnline(showOnline ? user?.id : null)
  const bg = `hsl(${hue(user)} 60% 55%)`
  const fontSize = Math.max(11, Math.floor(size * 0.4))

  return (
    <div className="relative inline-block shrink-0" style={{ width: size, height: size }}>
      {user?.avatar_url ? (
        <img
          src={user.avatar_url}
          alt={user.name ?? user.uniq_name}
          className="h-full w-full rounded-full object-cover"
        />
      ) : (
        <div
          className="flex h-full w-full items-center justify-center rounded-full font-semibold text-white"
          style={{ background: bg, fontSize }}
        >
          {initials(user)}
        </div>
      )}
      {showOnline && online && (
        <span
          className="absolute bottom-0 right-0 block rounded-full border-2 border-tg-panel bg-tg-online"
          style={{ width: size * 0.28, height: size * 0.28 }}
        />
      )}
    </div>
  )
}
