import React from "react";
import { SendIcon, BrainIcon, RefreshIcon } from "./Icons";
import type { Message } from "../types";

interface ChatTerminalProps {
  chatMessages: Message[];
  messageInput: string;
  setMessageInput: (val: string) => void;
  isSending: boolean;
  liveLogs: string[];
  onSendMessage: (e?: React.FormEvent) => void;
  chatEndRef: React.RefObject<HTMLDivElement | null>;
}

export const ChatTerminal: React.FC<ChatTerminalProps> = ({
  chatMessages,
  messageInput,
  setMessageInput,
  isSending,
  liveLogs,
  onSendMessage,
  chatEndRef,
}) => {
  return (
    <div className="max-w-5xl mx-auto h-[calc(100vh-12rem)] flex flex-col gap-4">
      {/* Chat messages viewport */}
      <div className="flex-1 bg-[#0c0f24]/30 border border-[#1e295d]/20 rounded-2xl p-6 overflow-y-auto space-y-4">
        {chatMessages.map((msg, index) => (
          <div
            key={index}
            className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            {/* Bot avatar */}
            {msg.role !== "user" && (
              <div className="w-9 h-9 rounded-xl bg-indigo-950 border border-indigo-500/30 flex items-center justify-center text-sm shadow-md shrink-0">
                {msg.agent === "Finral" ? "🌀" : msg.agent === "Noelle" ? "🌊" : "🐈‍⬛"}
              </div>
            )}

            <div className="max-w-[70%] space-y-1.5">
              {/* Name / Header */}
              {msg.role !== "user" && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="font-bold text-indigo-300">
                    {msg.agent || "System"}
                  </span>
                  <span className="text-[10px] text-zinc-500">
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              )}

              {/* Message Bubble */}
              <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-indigo-600 text-white rounded-tr-none shadow-md shadow-indigo-600/10"
                  : msg.role === "system"
                  ? "bg-rose-950/30 text-rose-300 border border-rose-900/50 rounded-tl-none font-mono text-xs"
                  : "bg-[#11142e]/90 text-zinc-200 border border-[#1e295d]/30 rounded-tl-none"
              }`}>
                {msg.content}
              </div>

              {/* Extracted Memories Notification */}
              {msg.extracted && msg.extracted.length > 0 && (
                <div className="bg-amber-950/20 border border-amber-500/20 rounded-xl p-3 space-y-2 mt-2">
                  <div className="text-[10px] text-amber-400 font-bold uppercase tracking-wider flex items-center gap-1.5">
                    <BrainIcon size={12} />
                    Persistent facts extracted
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {msg.extracted.map((item, idx) => (
                      <span key={idx} className="bg-amber-950/50 text-amber-300 text-xs px-2.5 py-0.5 rounded-md border border-amber-500/10">
                        {item.key}: {item.value}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* User avatar */}
            {msg.role === "user" && (
              <div className="w-9 h-9 rounded-xl bg-zinc-800 border border-zinc-700 flex items-center justify-center text-sm shadow-md shrink-0">
                👤
              </div>
            )}
          </div>
        ))}

        {/* Simulated live logs inside the stream */}
        {isSending && (
          <div className="flex gap-4">
            <div className="w-9 h-9 rounded-xl bg-indigo-950 border border-indigo-500/30 flex items-center justify-center text-sm shadow-md shrink-0 animate-pulse">
              🐈‍⬛
            </div>
            <div className="max-w-[70%] space-y-3">
              <div className="flex items-center gap-2 text-xs">
                <span className="font-bold text-indigo-300">BlackBull Graph Execution</span>
                <span className="text-[10px] text-amber-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-ping"></span>
                  Running Nodes
                </span>
              </div>
              
              {/* Log viewer bubble */}
              <div className="p-4 bg-zinc-950/80 border border-zinc-800 rounded-2xl rounded-tl-none font-mono text-[11px] text-zinc-400 w-full space-y-1.5">
                {liveLogs.map((log, index) => (
                  <div key={index} className="flex gap-2">
                    <span className="text-zinc-600">{`[${index + 1}]`}</span>
                    <span className={log.includes("State") || log.includes("resolved") ? "text-indigo-400" : log.includes("executing") ? "text-emerald-400" : "text-zinc-300"}>
                      {log}
                    </span>
                  </div>
                ))}
                <div className="flex items-center gap-1 text-[10px] text-zinc-500 mt-2 italic">
                  <RefreshIcon size={10} className="animate-spin text-zinc-500" />
                  Awaiting LLM generation...
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Chat Input form */}
      <form onSubmit={onSendMessage} className="flex gap-3 shrink-0">
        <input
          type="text"
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
          disabled={isSending}
          className="flex-1 bg-[#0c0f24] border border-[#1e295d]/30 focus:border-[#1e295d]/70 rounded-xl px-5 py-3.5 text-sm text-white focus:outline-none focus:ring-1 focus:ring-indigo-500/50 placeholder-zinc-500 transition disabled:opacity-50"
          placeholder="Ask Captain Yami to delegate or run system tools... (e.g., 'search for nearby restaurants')"
        />
        <button
          type="submit"
          disabled={isSending || !messageInput.trim()}
          className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 text-white rounded-xl px-6 py-3.5 flex items-center gap-2 font-semibold shadow-lg shadow-indigo-500/10 transition disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <SendIcon size={16} />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
};
