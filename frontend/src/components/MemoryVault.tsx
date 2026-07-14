import React from "react";
import { BrainIcon, PlusIcon, TrashIcon, SearchIcon, RefreshIcon } from "./Icons";
import type { MemoryItem } from "../types";

interface MemoryVaultProps {
  memories: MemoryItem[];
  searchMemoryQuery: string;
  setSearchMemoryQuery: (val: string) => void;
  isMemoriesLoading: boolean;
  newMemoryKey: string;
  setNewMemoryKey: (val: string) => void;
  newMemoryValue: string;
  setNewMemoryValue: (val: string) => void;
  newMemoryAgent: string;
  setNewMemoryAgent: (val: string) => void;
  isAddingMemory: boolean;
  onWipeCache: () => void;
  onCreateMemory: (e: React.FormEvent) => void;
  onDeleteMemory: (key: string) => void;
}

export const MemoryVault: React.FC<MemoryVaultProps> = ({
  memories,
  searchMemoryQuery,
  setSearchMemoryQuery,
  isMemoriesLoading,
  newMemoryKey,
  setNewMemoryKey,
  newMemoryValue,
  setNewMemoryValue,
  newMemoryAgent,
  setNewMemoryAgent,
  isAddingMemory,
  onWipeCache,
  onCreateMemory,
  onDeleteMemory,
}) => {
  const filteredMemories = memories.filter((m) =>
    m.key.toLowerCase().includes(searchMemoryQuery.toLowerCase()) ||
    m.value.toLowerCase().includes(searchMemoryQuery.toLowerCase()) ||
    m.agent_name.toLowerCase().includes(searchMemoryQuery.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header and statistics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-2xl font-extrabold text-white flex items-center gap-2">
            <BrainIcon className="text-amber-500" />
            Cognitive Memory Vault
          </h2>
          <p className="text-zinc-400 text-sm">
            Review and modify key-value facts collected by agents. Clear memory cache for full resetting.
          </p>
        </div>
        {memories.length > 0 && (
          <button
            onClick={onWipeCache}
            className="bg-rose-950/30 hover:bg-rose-900/30 text-rose-400 border border-rose-900/50 rounded-xl px-4 py-2 text-xs font-semibold transition"
          >
            Clear All Memories
          </button>
        )}
      </div>

      {/* Memory Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Manual fact injection form */}
        <div className="bg-[#0c0f24]/30 border border-[#1e295d]/30 rounded-2xl p-6 h-fit space-y-4">
          <h3 className="font-bold text-white text-sm pb-2 border-b border-[#1e295d]/20 flex items-center gap-2">
            <PlusIcon size={16} className="text-amber-500" />
            Inject Manual Memory Fact
          </h3>
          
          <form onSubmit={onCreateMemory} className="space-y-4">
            <div className="space-y-1">
              <label className="text-xs text-zinc-400 font-medium">Memory Key</label>
              <input
                type="text"
                value={newMemoryKey}
                onChange={(e) => setNewMemoryKey(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                placeholder="e.g. favorite_food"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs text-zinc-400 font-medium">Fact Value</label>
              <input
                type="text"
                value={newMemoryValue}
                onChange={(e) => setNewMemoryValue(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                placeholder="e.g. Katsudon and ramen"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs text-zinc-400 font-medium">Agent Scope Namespace</label>
              <select
                value={newMemoryAgent}
                onChange={(e) => setNewMemoryAgent(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-xl px-3 py-2 text-xs text-zinc-300 focus:outline-none focus:border-indigo-500"
              >
                <option value="shared">Shared (All agents)</option>
                <option value="yami">Yami (Supervisor)</option>
                <option value="finral">Finral (Spatial)</option>
                <option value="noelle">Noelle (Calendar)</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={isAddingMemory}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:bg-zinc-800 text-white rounded-xl py-2.5 text-xs font-semibold shadow-lg shadow-indigo-500/10 transition"
            >
              {isAddingMemory ? "Injecting..." : "Inject Fact"}
            </button>
          </form>
        </div>

        {/* Facts Database Viewer */}
        <div className="lg:col-span-2 space-y-4">
          {/* Search filter bar */}
          <div className="relative">
            <SearchIcon size={16} className="absolute left-4 top-3 text-zinc-500" />
            <input
              type="text"
              value={searchMemoryQuery}
              onChange={(e) => setSearchMemoryQuery(e.target.value)}
              className="w-full bg-[#0c0f24]/30 border border-[#1e295d]/30 focus:border-[#1e295d]/60 rounded-xl pl-11 pr-4 py-2.5 text-xs text-white focus:outline-none placeholder-zinc-500 transition"
              placeholder="Filter database memory tags by key or content..."
            />
          </div>

          {/* Vault List */}
          {isMemoriesLoading ? (
            <div className="bg-zinc-950/30 border border-zinc-800 rounded-2xl p-12 text-center text-zinc-500 text-xs flex flex-col items-center justify-center gap-2">
              <RefreshIcon size={24} className="animate-spin text-indigo-500" />
              Loading Database Records...
            </div>
          ) : filteredMemories.length === 0 ? (
            <div className="bg-zinc-950/30 border border-zinc-800 rounded-2xl p-12 text-center text-zinc-500 text-xs space-y-1">
              <div>No persistent memory records found.</div>
              <div className="text-zinc-600">Chat with the agents or use the panel to manually inject facts.</div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredMemories.map((memory, index) => (
                <div
                  key={index}
                  className="bg-zinc-900/30 hover:bg-zinc-900/50 border border-zinc-800 rounded-2xl p-5 space-y-3 flex flex-col justify-between group transition duration-200"
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-start gap-2">
                      <span className="bg-zinc-950 text-indigo-400 font-mono text-[10px] px-2.5 py-0.5 rounded-md border border-zinc-800 font-bold max-w-[70%] truncate">
                        {memory.key}
                      </span>
                      <span className="text-[9px] text-zinc-500 uppercase font-semibold">
                        {memory.agent_name}
                      </span>
                    </div>
                    <p className="text-sm text-zinc-300 font-medium">
                      {memory.value}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-zinc-800/40 flex justify-end">
                    <button
                      onClick={() => onDeleteMemory(memory.key)}
                      className="text-zinc-500 hover:text-rose-400 transition"
                      title="Delete memory key"
                    >
                      <TrashIcon size={14} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
