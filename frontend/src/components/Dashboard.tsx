import React from "react";
import { BrainIcon, ActivityIcon, TerminalIcon, SettingsIcon } from "./Icons";
import type { AgentDetails } from "../types";

interface DashboardProps {
  memoriesCount: number;
  userId: string;
  agents: AgentDetails[];
  onTabChange: (tab: "dashboard" | "chat" | "agents" | "memory") => void;
  onWipeCache: () => void;
}

export const Dashboard: React.FC<DashboardProps> = ({
  memoriesCount,
  userId,
  agents,
  onTabChange,
  onWipeCache,
}) => {
  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Hero welcome header */}
      <div className="relative p-8 rounded-3xl overflow-hidden bg-gradient-to-r from-indigo-950 via-[#101438] to-[#070913] border border-indigo-500/20 shadow-2xl">
        <div className="absolute right-0 bottom-0 top-0 w-1/3 opacity-10 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-indigo-400 to-transparent"></div>
        <div className="relative z-10 space-y-3">
          <span className="px-3 py-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full text-[10px] font-bold uppercase tracking-widest">
            Black Clover Engine v1.0
          </span>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Multi-Agent Portal Panel
          </h2>
          <p className="text-zinc-400 text-sm max-w-2xl leading-relaxed">
            Welcome to the orchestrator cockpit. Below is the operational status of the Black Clover agents. Send tasks to Captain Yami Sukehiro to trigger system automation, search the web, manage schedules, and let the system build memory facts of your preferences.
          </p>
        </div>
      </div>

      {/* Health Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Database Info */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 flex items-start gap-4">
          <div className="p-3 bg-indigo-500/10 rounded-xl text-indigo-400 border border-indigo-500/20">
            <BrainIcon size={24} />
          </div>
          <div className="space-y-1 flex-1">
            <div className="text-zinc-500 text-xs font-bold tracking-wider uppercase">Database Storage</div>
            <div className="text-xl font-bold text-white">PostgreSQL Vector</div>
            <div className="text-xs text-zinc-400 flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              PGVector Extension Active
            </div>
          </div>
        </div>

        {/* Memory facts count */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 flex items-start gap-4">
          <div className="p-3 bg-amber-500/10 rounded-xl text-amber-400 border border-amber-500/20">
            <ActivityIcon size={24} />
          </div>
          <div className="space-y-1 flex-1">
            <div className="text-zinc-500 text-xs font-bold tracking-wider uppercase">Memory State</div>
            <div className="text-xl font-bold text-white">{memoriesCount} Extracted Facts</div>
            <div className="text-xs text-zinc-400 flex items-center justify-between mt-1">
              <span>Namespace: {userId}</span>
              <button onClick={() => onTabChange("memory")} className="text-amber-400 hover:underline">Manage</button>
            </div>
          </div>
        </div>

        {/* System actions stats */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 flex items-start gap-4">
          <div className="p-3 bg-teal-500/10 rounded-xl text-teal-400 border border-teal-500/20">
            <TerminalIcon size={24} />
          </div>
          <div className="space-y-1 flex-1">
            <div className="text-zinc-500 text-xs font-bold tracking-wider uppercase">Automations Node</div>
            <div className="text-xl font-bold text-white">LangGraph Runtime</div>
            <div className="text-xs text-zinc-400 flex items-center gap-1.5 mt-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
              15 Integrated Automation Tools
            </div>
          </div>
        </div>
      </div>

      {/* Agent Quick Overview cards */}
      <div>
        <h3 className="text-lg font-bold text-white mb-5 flex items-center gap-2">
          <ActivityIcon size={18} className="text-indigo-400" />
          Active Command Agents
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className={`relative bg-zinc-900/20 hover:bg-zinc-900/40 border ${agent.borderColor} rounded-2xl p-6 transition duration-300 group flex flex-col justify-between`}
            >
              <div className="space-y-4">
                <div className="flex justify-between items-start">
                  <span className="text-3xl">{agent.avatar}</span>
                  <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold border ${
                    agent.status === "ACTIVE"
                      ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20 animate-pulse"
                      : "bg-zinc-800 text-zinc-500 border-zinc-700"
                  }`}>
                    {agent.status}
                  </span>
                </div>
                <div>
                  <h4 className="font-bold text-white group-hover:text-amber-400 transition">
                    {agent.name.split(" ")[1] || agent.name}
                  </h4>
                  <p className="text-[10px] text-zinc-500 font-semibold uppercase mt-0.5">
                    {agent.magic}
                  </p>
                  <p className="text-xs text-zinc-400 mt-2 line-clamp-3">
                    {agent.description}
                  </p>
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-zinc-800/50 flex items-center justify-between text-[11px] text-zinc-500">
                <span>{agent.tools.length} Sub-tools</span>
                <button
                  onClick={() => onTabChange("agents")}
                  className="text-indigo-400 hover:text-indigo-300 font-medium hover:underline"
                >
                  View Skills
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Config */}
      <div className="bg-zinc-900/30 border border-zinc-800 rounded-2xl p-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div className="space-y-1">
            <h4 className="font-bold text-white flex items-center gap-2">
              <SettingsIcon size={16} className="text-zinc-400" />
              Configure Workspace Parameters
            </h4>
            <p className="text-xs text-zinc-400">
              Alter the global query target and configure developer settings.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => onTabChange("chat")}
              className="bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl px-5 py-2 text-xs font-semibold shadow-lg shadow-indigo-500/20 transition duration-200"
            >
              Open Chat Terminal
            </button>
            <button
              onClick={onWipeCache}
              className="bg-zinc-800 hover:bg-zinc-700 text-zinc-200 border border-zinc-700 rounded-xl px-5 py-2 text-xs font-semibold transition"
            >
              Wipe Cache
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
