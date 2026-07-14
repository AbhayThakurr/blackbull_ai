import React from "react";
import { ChatTerminal } from "../components";
import type { Message } from "../types";

interface ChatPageProps {
  chatMessages: Message[];
  messageInput: string;
  setMessageInput: (val: string) => void;
  isSending: boolean;
  liveLogs: string[];
  onSendMessage: (e?: React.FormEvent) => void;
  chatEndRef: React.RefObject<HTMLDivElement | null>;
}

export const ChatPage: React.FC<ChatPageProps> = ({
  chatMessages,
  messageInput,
  setMessageInput,
  isSending,
  liveLogs,
  onSendMessage,
  chatEndRef,
}) => {
  return (
    <ChatTerminal
      chatMessages={chatMessages}
      messageInput={messageInput}
      setMessageInput={setMessageInput}
      isSending={isSending}
      liveLogs={liveLogs}
      onSendMessage={onSendMessage}
      chatEndRef={chatEndRef}
    />
  );
};
