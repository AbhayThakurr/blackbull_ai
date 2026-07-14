import React from "react";
import { MemoryVault } from "../components";
import type { MemoryItem } from "../types";

interface MemoryPageProps {
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

export const MemoryPage: React.FC<MemoryPageProps> = ({
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
  return (
    <MemoryVault
      memories={memories}
      searchMemoryQuery={searchMemoryQuery}
      setSearchMemoryQuery={setSearchMemoryQuery}
      isMemoriesLoading={isMemoriesLoading}
      newMemoryKey={newMemoryKey}
      setNewMemoryKey={setNewMemoryKey}
      newMemoryValue={newMemoryValue}
      setNewMemoryValue={setNewMemoryValue}
      newMemoryAgent={newMemoryAgent}
      setNewMemoryAgent={setNewMemoryAgent}
      isAddingMemory={isAddingMemory}
      onWipeCache={onWipeCache}
      onCreateMemory={onCreateMemory}
      onDeleteMemory={onDeleteMemory}
    />
  );
};
