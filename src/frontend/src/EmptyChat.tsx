export function EmptyChat() {
  return (
    <div className="flex h-full min-w-0 flex-1 items-center justify-center bg-tg-bg text-tg-mute">
      <div className="text-center">
        <div className="mb-2 text-5xl">💬</div>
        <p className="text-lg">Select a chat to start messaging</p>
      </div>
    </div>
  )
}
