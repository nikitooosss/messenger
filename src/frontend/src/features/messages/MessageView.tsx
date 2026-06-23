import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";

import { api } from "../../lib/apiClient";
import { qk } from "../../lib/queryKeys";

import { useCurrentUser } from "../../auth/useCurrentUser";
import { useMessages } from "./useMessages";
import { useOnline } from "../presence/useOnline";

import { MessageBubble } from "./MessageBubble";
import { MessageInput } from "./MessageInput";
import { TypingIndicator } from "./TypingIndicator";

import { ChatInfoPanel } from "../chats/ChatInfoPanel";

import { UserAvatar } from "../../components/UserAvatar";
import { Spinner } from "../../components/Spinner";

import { formatDateLabel, formatLastSeen } from "../../lib/time";

import type { Message, User } from "../../types/models";

interface MessageViewProps {
  chatId: number;
}

export function MessageView({ chatId }: MessageViewProps) {
  const { data: me } = useCurrentUser();

  const { data: messages = [], isLoading } = useMessages(chatId);

  const { data: users = [] } = useQuery<User[]>({
    queryKey: qk.users,
    queryFn: api.users,
  });

  const { data: participants = [] } = useQuery({
    queryKey: qk.participants(chatId),
    queryFn: () => api.participants(chatId),
  });

  const chatsQuery = useQuery({
    queryKey: qk.chats(),
    queryFn: () => api.chats(me!.id),
    enabled: !!me,
  });
  const chats = chatsQuery.data ?? [];

  const [infoOpen, setInfoOpen] = useState(false);

  const scrollRef = useRef<HTMLDivElement>(null);

  const chat = chats.find((c) => c.id === chatId);

  const navigate = useNavigate();

  useEffect(() => {
    if (chatsQuery.isLoading) return;
    if (chat === undefined) {
      navigate({ to: "/" });
    }
  }, [chat, chatsQuery.isLoading, navigate]);

  const sortedMessages = useMemo(
    () =>
      [...messages].sort(
        (a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
      ),
    [messages],
  );

  const usersMap = useMemo(
    () => new Map<number, User>(users.map((u) => [u.id, u])),
    [users],
  );

  const peer =
    chat && !chat.is_group
      ? participants.find((p) => p.user_id !== me?.id)
      : null;

  const peerUser = peer ? usersMap.get(peer.user_id) : null;

  const peerOnline = useOnline(
    chat && !chat.is_group ? (peerUser?.id ?? null) : null,
  );

  const displayName = chat?.is_group
    ? chat.name
    : peerUser?.name?.trim() || peerUser?.uniq_name || chat?.name || "Chat";

  const headerSubtitle =
    !chat?.is_group && peerUser
      ? peerOnline
        ? "online"
        : formatLastSeen(peerUser.last_seen)
      : chat?.is_group
        ? `${participants.length} members`
        : "";

  useEffect(() => {
    const el = scrollRef.current;

    if (!el) return;

    el.scrollTop = el.scrollHeight;
  }, [chatId]);

  useEffect(() => {
    const el = scrollRef.current;

    if (!el) return;

    el.scrollTop = el.scrollHeight;
  }, [sortedMessages.length]);

  return (
    <section className="flex h-full min-w-0 flex-1 flex-col bg-tg-bg">
      <header className="flex items-center gap-3 border-b border-tg-border bg-tg-panel px-4 py-3">
        {chat?.is_group ? (
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-tg-accent text-sm font-semibold text-white">
            {chat.name.charAt(0).toUpperCase()}
          </div>
        ) : (
          <UserAvatar
            user={peerUser ?? null}
            size={40}
            showOnline
            maxInitials={1}
          />
        )}

        <div className="min-w-0 flex-1">
          <div className="truncate font-medium text-tg-text">{displayName}</div>

          <div className="truncate text-xs text-tg-mute">
            {peerOnline ? (
              <span className="text-tg-online">online</span>
            ) : (
              headerSubtitle
            )}
          </div>
        </div>

        {chat && (
          <button
            onClick={() => setInfoOpen((v) => !v)}
            className="rounded-lg px-3 py-1.5 text-sm text-tg-accent hover:bg-tg-sidebar"
          >
            Info
          </button>
        )}
      </header>

      <div className="flex min-h-0 flex-1">
        <div className="flex min-w-0 flex-1 flex-col">
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-3">
            {isLoading ? (
              <div className="flex h-full items-center justify-center">
                <Spinner />
              </div>
            ) : sortedMessages.length === 0 ? (
              <div className="flex h-full items-center justify-center text-sm text-tg-mute">
                No messages yet. Say hi!
              </div>
            ) : (
              <MessageList
                sorted={sortedMessages}
                meId={me?.id ?? -1}
                usersMap={usersMap}
                isGroup={chat?.is_group ?? false}
              />
            )}
          </div>

          <TypingIndicator chatId={chatId} />

          <MessageInput chatId={chatId} />
        </div>

        {infoOpen && chat && <ChatInfoPanel chat={chat} />}
      </div>
    </section>
  );
}

function MessageList({
  sorted,
  meId,
  usersMap,
  isGroup,
}: {
  sorted: Message[];
  meId: number;
  usersMap: Map<number, User>;
  isGroup: boolean;
}) {
  const items: React.ReactNode[] = [];

  let lastDate = "";

  for (let i = 0; i < sorted.length; i++) {
    const m = sorted[i];

    const dateLabel = formatDateLabel(m.created_at);

    if (dateLabel !== lastDate) {
      items.push(
        <div key={`date-${m.id}`} className="my-2 flex justify-center">
          <span className="rounded-full bg-tg-sidebar px-3 py-0.5 text-xs text-tg-mute">
            {dateLabel}
          </span>
        </div>,
      );

      lastDate = dateLabel;
    }

    const prev = sorted[i - 1];

    const showAuthor =
      isGroup &&
      (!prev || prev.user_id !== m.user_id || isNewAuthorBreak(prev, m));

    const author = usersMap.get(m.user_id);

    const authorName = author?.name?.trim() || author?.uniq_name || "user";

    items.push(
      <MessageBubble
        key={m.id}
        message={m}
        showAuthor={showAuthor}
        isOwn={m.user_id === meId}
        isOptimistic={m.id < 0}
        authorName={authorName}
      />,
    );
  }

  return <>{items}</>;
}

function isNewAuthorBreak(a: Message, b: Message) {
  return (
    new Date(b.created_at).getTime() - new Date(a.created_at).getTime() >
    5 * 60 * 1000
  );
}
