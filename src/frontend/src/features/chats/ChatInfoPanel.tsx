import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '../../lib/apiClient'
import { qk } from '../../lib/queryKeys'
import { useCurrentUser } from '../../auth/useCurrentUser'
import { ParticipantList } from '../participants/ParticipantList'
import { AddParticipantDialog } from '../participants/AddParticipantDialog'
import { useDeleteChat } from './useDeleteChat'
import { useLeaveChat } from './useLeaveChat'
import { Dialog } from '../../components/Dialog'
import { Button } from '../../components/Button'
import { useNavigate } from '@tanstack/react-router'
import type { Chat, User } from '../../types/models'

interface ChatInfoPanelProps {
  chat: Chat
}

export function ChatInfoPanel({ chat }: ChatInfoPanelProps) {
  const { data: me } = useCurrentUser()
  const { data: participants = [] } = useQuery({
    queryKey: qk.participants(chat.id),
    queryFn: () => api.participants(chat.id),
  })
  const { data: users = [] } = useQuery<User[]>({ queryKey: qk.users, queryFn: api.users })

  const [addOpen, setAddOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [leaveDialogOpen, setLeaveDialogOpen] = useState(false)
  const navigate = useNavigate()

  const deleteChat = useDeleteChat()
  const leaveChat = useLeaveChat()

  const myParticipant = participants.find((p) => p.user_id === me?.id)
  const isAdmin = myParticipant?.role === 'admin'

  const handleDelete = async () => {
    await deleteChat.mutateAsync({ chat })
    setDeleteDialogOpen(false)
    navigate({ to: '/' })
  }

  const handleLeave = async () => {
    await leaveChat.mutateAsync({ chatId: chat.id })
    setLeaveDialogOpen(false)
    navigate({ to: '/' })
  }

  return (
    <aside className="w-72 shrink-0 border-l border-tg-border bg-tg-sidebar">
      <div className="flex items-center justify-between border-b border-tg-border px-4 py-3">
        <div className="font-medium text-tg-text">
          {chat.is_group ? 'Members' : 'Info'}
        </div>
        {chat.is_group && (
          <button
            onClick={() => setAddOpen(true)}
            className="text-sm text-tg-accent hover:underline"
          >
            Add
          </button>
        )}
      </div>

      {chat.is_group && (
        <ParticipantList
          chatId={chat.id}
          participants={participants}
          users={users}
          meId={me?.id ?? -1}
        />
      )}

      <div className="border-t border-tg-border px-4 py-3">
        {isAdmin ? (
          <button
            onClick={() => setDeleteDialogOpen(true)}
            className="w-full rounded-lg bg-tg-danger px-4 py-2 text-sm font-medium text-white hover:opacity-90"
          >
            Delete Chat
          </button>
        ) : (
          <button
            onClick={() => setLeaveDialogOpen(true)}
            className="w-full rounded-lg bg-tg-danger px-4 py-2 text-sm font-medium text-white hover:opacity-90"
          >
            Leave Chat
          </button>
        )}
      </div>

      <AddParticipantDialog
        open={addOpen}
        onClose={() => setAddOpen(false)}
        chatId={chat.id}
        existingUserIds={participants.map((p) => p.user_id)}
      />

      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        title="Delete Chat"
        footer={
          <>
            <Button variant="secondary" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDelete} disabled={deleteChat.isPending}>
              Delete
            </Button>
          </>
        }
      >
        <p className="text-sm text-tg-text">
          Are you sure you want to delete this chat? This action cannot be undone.
        </p>
      </Dialog>

      <Dialog
        open={leaveDialogOpen}
        onClose={() => setLeaveDialogOpen(false)}
        title="Leave Chat"
        footer={
          <>
            <Button variant="secondary" onClick={() => setLeaveDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleLeave} disabled={leaveChat.isPending}>
              Leave
            </Button>
          </>
        }
      >
        <p className="text-sm text-tg-text">
          Are you sure you want to leave this chat? You won't be able to see new messages.
        </p>
      </Dialog>
    </aside>
  )
}
