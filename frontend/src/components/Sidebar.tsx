import React from "react";
import {
  DashboardIcon,
  ChatIcon,
  AgentIcon,
  BrainIcon,
  UserIcon,
  RefreshIcon,
} from "./Icons";

interface SidebarProps {
  currentTab: "dashboard" | "chat" | "agents" | "memory";
  setCurrentTab: (tab: "dashboard" | "chat" | "agents" | "memory") => void;
  userId: string;
  sessionUser: string;
  setSessionUser: (user: string) => void;
  backendStatus: "checking" | "online" | "offline";
  discordStatus: "checking" | "online" | "offline";
  isSending: boolean;
  memoriesCount: number;
  onRefresh: () => void;
  onSetUser: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  setCurrentTab,
  sessionUser,
  setSessionUser,
  backendStatus,
  discordStatus,
  isSending,
  memoriesCount,
  onRefresh,
  onSetUser,
}) => {
  return (
    <aside className="w-72 bg-[#0c0f24] border-r border-[#1e295d]/30 flex flex-col shrink-0">
      {/* Logo / Portal Title */}
      <div className="p-6 border-b border-[#1e295d]/30 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 via-red-500 to-indigo-600 flex items-center justify-center font-bold text-white shadow-lg shadow-indigo-500/20">
          🐂
        </div>
        <div>
          <h1 className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-amber-400 via-indigo-200 to-white bg-clip-text text-transparent">
            BLACKBULL AI
          </h1>
          <p className="text-[10px] text-zinc-400 font-semibold tracking-wider uppercase">
            Agent Command System
          </p>
        </div>
      </div>

      {/* User context quick switcher */}
      <div className="p-4 mx-4 my-4 bg-zinc-900/60 rounded-xl border border-zinc-800 flex flex-col gap-2">
        <div className="flex items-center gap-2 text-xs text-zinc-400 font-medium">
          <UserIcon size={14} className="text-amber-500" />
          <span>Active Memory ID</span>
        </div>
        <div className="flex gap-1.5">
          <input
            type="text"
            value={sessionUser}
            onChange={(e) => setSessionUser(e.target.value)}
            className="bg-zinc-950 border border-zinc-800 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-amber-500/50 w-full"
            placeholder="User ID (e.g. abhay)"
          />
          <button
            onClick={onSetUser}
            className="bg-amber-600 hover:bg-amber-500 text-white rounded-lg px-2.5 py-1 text-xs font-semibold transition"
          >
            Set
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <nav className="flex-1 px-4 space-y-1">
        <button
          onClick={() => setCurrentTab("dashboard")}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition duration-200 ${
            currentTab === "dashboard"
              ? "bg-gradient-to-r from-indigo-950/80 to-indigo-900/40 text-indigo-200 border-l-4 border-indigo-500"
              : "text-zinc-400 hover:bg-zinc-900/50 hover:text-zinc-200"
          }`}
        >
          <DashboardIcon className={currentTab === "dashboard" ? "text-indigo-400" : "text-zinc-500"} />
          <span>System Overview</span>
        </button>

        <button
          onClick={() => setCurrentTab("chat")}
          className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition duration-200 ${
            currentTab === "chat"
              ? "bg-gradient-to-r from-indigo-950/80 to-indigo-900/40 text-indigo-200 border-l-4 border-indigo-500"
              : "text-zinc-400 hover:bg-zinc-900/50 hover:text-zinc-200"
          }`}
        >
          <div className="flex items-center gap-3">
            <ChatIcon className={currentTab === "chat" ? "text-indigo-400" : "text-zinc-500"} />
            <span>Agent Chat Terminal</span>
          </div>
          {isSending && (
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span>
          )}
        </button>

        <button
          onClick={() => setCurrentTab("agents")}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition duration-200 ${
            currentTab === "agents"
              ? "bg-gradient-to-r from-indigo-950/80 to-indigo-900/40 text-indigo-200 border-l-4 border-indigo-500"
              : "text-zinc-400 hover:bg-zinc-900/50 hover:text-zinc-200"
          }`}
        >
          <AgentIcon className={currentTab === "agents" ? "text-indigo-400" : "text-zinc-500"} />
          <span>Squad Roster</span>
        </button>

        <button
          onClick={() => setCurrentTab("memory")}
          className={`w-full flex items-center justify-between px-4 py-3 rounded-xl text-sm font-medium transition duration-200 ${
            currentTab === "memory"
              ? "bg-gradient-to-r from-indigo-950/80 to-indigo-900/40 text-indigo-200 border-l-4 border-indigo-500"
              : "text-zinc-400 hover:bg-zinc-900/50 hover:text-zinc-200"
          }`}
        >
          <div className="flex items-center gap-3">
            <BrainIcon className={currentTab === "memory" ? "text-indigo-400" : "text-zinc-500"} />
            <span>Memory Vault</span>
          </div>
          {memoriesCount > 0 && (
            <span className="bg-zinc-800 text-zinc-300 text-[10px] px-2 py-0.5 rounded-full font-bold">
              {memoriesCount}
            </span>
          )}
        </button>
      </nav>

      {/* Bottom Health indicators */}
      <div className="p-4 border-t border-[#1e295d]/30 bg-zinc-950/40 flex flex-col gap-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
            Core System
          </span>
          <span className={`font-semibold capitalize flex items-center gap-1.5 ${
            backendStatus === "online" ? "text-emerald-400" : backendStatus === "offline" ? "text-rose-400" : "text-amber-400"
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${
              backendStatus === "online" ? "bg-emerald-400 animate-pulse" : backendStatus === "offline" ? "bg-rose-400" : "bg-amber-400 animate-bounce"
            }`}></span>
            {backendStatus}
          </span>
        </div>

        <div className="flex items-center justify-between text-xs">
          <span className="text-zinc-500 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-500"></span>
            Discord Link
          </span>
          <span className={`font-semibold capitalize flex items-center gap-1.5 ${
            discordStatus === "online" ? "text-emerald-400" : discordStatus === "offline" ? "text-rose-400" : "text-amber-400"
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${
              discordStatus === "online" ? "bg-emerald-400 animate-pulse" : discordStatus === "offline" ? "bg-rose-400" : "bg-amber-400 animate-bounce"
            }`}></span>
            {discordStatus}
          </span>
        </div>

        <button
          onClick={onRefresh}
          className="mt-2 w-full py-1.5 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 border border-zinc-800 transition"
        >
          <RefreshIcon size={12} />
          Refresh Systems
        </button>
      </div>
    </aside>
  );
};
