import { Outlet } from '@tanstack/react-router'
import { WebSocketProvider } from './ws/WebSocketProvider'
import { Sidebar } from './features/chats/Sidebar'

export function AppLayout() {
  return (
    <WebSocketProvider enabled>
      <div className="flex h-full w-full overflow-hidden">
        <Sidebar />
        <Outlet />
      </div>
    </WebSocketProvider>
  )
}
