import {
  createRootRoute,
  createRoute,
  createRouter,
  Outlet,
} from '@tanstack/react-router'
import { LoginPage } from './auth/LoginPage'
import { RegisterPage } from './auth/RegisterPage'
import { AppLayout } from './AppLayout'
import { MessageView } from './features/messages/MessageView'
import { EmptyChat } from './EmptyChat'
import { ensureAuthenticated } from './auth/RequireAuth'
import { queryClient } from './lib/queryClient'

const rootRoute = createRootRoute({
  component: () => <Outlet />,
})

const loginRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/login',
  component: LoginPage,
})

const registerRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/register',
  component: RegisterPage,
})

const appRoute = createRoute({
  getParentRoute: () => rootRoute,
  id: 'app',
  beforeLoad: () => ensureAuthenticated(queryClient),
  component: AppLayout,
})

const indexRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/',
  component: EmptyChat,
})

const chatRoute = createRoute({
  getParentRoute: () => appRoute,
  path: '/chat/$chatId',
  parseParams: (p) => ({ chatId: Number(p.chatId) }),
  stringifyParams: (p) => ({ chatId: String(p.chatId) }),
  component: ChatRouteComponent,
})

function ChatRouteComponent() {
  const { chatId } = chatRoute.useParams()
  if (!Number.isFinite(chatId)) return <EmptyChat />
  return <MessageView chatId={chatId} />
}

const routeTree = rootRoute.addChildren([
  loginRoute,
  registerRoute,
  appRoute.addChildren([indexRoute, chatRoute]),
])

export const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultPreload: 'intent',
})

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
