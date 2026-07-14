import React from "react";
import type { AgentDetails } from "../types";

interface AgentHubProps {
  agents: AgentDetails[];
}

export const AgentHub: React.FC<AgentHubProps> = ({ agents }) => {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="flex flex-col gap-2">
        <h2 className="text-2xl font-extrabold text-white">Squad Members Skills & Capabilities</h2>
        <p className="text-zinc-400 text-sm">
          Review the exact tool configuration and magic elements assigned to each agent.
        </p>
      </div>

      <div className="space-y-6">
        {agents.map((agent) => (
          <div
            key={agent.id}
            className={`bg-[#0c0f24]/30 border ${agent.borderColor} rounded-2xl p-6 md:p-8 flex flex-col md:flex-row gap-6 relative overflow-hidden`}
          >
            {/* Visual glowing aura behind avatar */}
            <div className="absolute -left-20 -top-20 w-48 h-48 rounded-full bg-indigo-500/5 blur-3xl"></div>

            {/* Agent Avatar */}
            <div className="flex flex-col items-center gap-3 shrink-0">
              <div className="w-20 h-20 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-4xl shadow-xl">
                {agent.avatar}
              </div>
              <span className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold border ${
                agent.status === "ACTIVE"
                  ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                  : "bg-zinc-800 text-zinc-500 border-zinc-700"
              }`}>
                {agent.status}
              </span>
            </div>

            {/* Agent description and tools */}
            <div className="flex-1 space-y-4">
              <div>
                <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                  <h3 className="text-xl font-bold text-white">{agent.name}</h3>
                  <span className="text-xs text-amber-500 font-semibold bg-amber-500/5 px-2 py-0.5 rounded-md border border-amber-500/10">
                    {agent.magic}
                  </span>
                </div>
                <p className="text-xs text-indigo-300 font-semibold mt-1">
                  {agent.role}
                </p>
                <p className="text-sm text-zinc-400 mt-3 leading-relaxed">
                  {agent.description}
                </p>
              </div>

              {/* Tool configuration mapping */}
              <div className="space-y-2">
                <div className="text-xs font-bold text-zinc-500 uppercase tracking-wider">
                  Active Tool Invocation Methods
                </div>
                <div className="flex flex-wrap gap-2">
                  {agent.tools.map((tool, idx) => (
                    <span
                      key={idx}
                      className="bg-zinc-950 text-zinc-300 font-mono text-[11px] px-3 py-1.5 rounded-lg border border-zinc-800 flex items-center gap-1.5"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
