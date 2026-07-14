import { useState, useEffect, useRef } from "react";
import { Sidebar } from "./components";
import { DashboardPage, ChatPage, RosterPage, MemoryPage } from "./pages";
import type { Message, MemoryItem } from "./types";
import {
  checkHealthApi,
  fetchMemoriesApi,
  createMemoryApi,
  deleteMemoryApi,
  clearMemoriesApi,
  sendChatMessageApi,
  getSimulatedRoutingLogs,
} from "./helpers";

export default function App() {
  const [currentTab, setCurrentTab] = useState<"dashboard" | "chat" | "agents" | "memory">("dashboard");
  const [userId, setUserId] = useState<string>("abhay");
  const [sessionUser, setSessionUser] = useState<string>("abhay");
  const [backendStatus, setBackendStatus] = useState<"checking" | "online" | "offline">("checking");
  const [discordStatus, setDiscordStatus] = useState<"checking" | "online" | "offline">("checking");

  // Chat States
  const [chatMessages, setChatMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Captain Yami here. What needs doing? I can trigger system apps, or delegate to Noelle for scheduling/emails and Finral for browsing/searches. Don't waste my time.",
      timestamp: new Date(),
      agent: "Yami",
    },
  ]);
  const [messageText, setMessageText] = useState<string>("");
  const [isSending, setIsSending] = useState<boolean>(false);
  const [liveLogs, setLiveLogs] = useState<string[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Memory States
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [searchMemoryQuery, setSearchMemoryQuery] = useState<string>("");
  const [isMemoriesLoading, setIsMemoriesLoading] = useState<boolean>(false);
  const [newMemoryKeyVal, setNewMemoryKeyVal] = useState<string>("");
  const [newMemoryValue, setNewMemoryValue] = useState<string>("");
  const [newMemoryAgent, setNewMemoryAgent] = useState<string>("shared");
  const [isAddingMemory, setIsAddingMemory] = useState<boolean>(false);

  // Sync health and database context
  useEffect(() => {
    checkHealth();
    fetchMemories();
  }, [userId]);

  const checkHealth = async () => {
    setBackendStatus("checking");
    const online = await checkHealthApi();
    if (online) {
      setBackendStatus("online");
      setDiscordStatus("online");
    } else {
      setBackendStatus("offline");
      setDiscordStatus("offline");
    }
  };

  const fetchMemories = async () => {
    if (!userId.trim()) return;
    setIsMemoriesLoading(true);
    try {
      const data = await fetchMemoriesApi(userId);
      setMemories(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsMemoriesLoading(false);
    }
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!messageText.trim() || isSending) return;

    const userMsgText = messageText;
    setMessageText("");
    setIsSending(true);

    // Get simulated logs from helper
    const logInfo = getSimulatedRoutingLogs(userMsgText, userId);
    setLiveLogs(logInfo.steps);

    // Append User message
    const userMessage: Message = {
      role: "user",
      content: userMsgText,
      timestamp: new Date(),
    };
    setChatMessages((prev) => [...prev, userMessage]);

    try {
      const data = await sendChatMessageApi(userId, userMsgText);

      // Complete execution flow animation
      setTimeout(() => {
        setLiveLogs((prev) => [
          ...prev,
          "Post-Agent Node: extract_memory_node running...",
          data.extracted_memories?.length > 0
            ? `Extracted ${data.extracted_memories.length} new memory fact(s).`
            : "No new memories extracted.",
          "Graph completed successfully with state 'END'.",
        ]);

        const assistantMessage: Message = {
          role: "assistant",
          content: data.response,
          timestamp: new Date(),
          agent: logInfo.agent,
          extracted: data.extracted_memories,
        };

        setChatMessages((prev) => [...prev, assistantMessage]);
        setIsSending(false);
        setLiveLogs([]);

        if (data.extracted_memories && data.extracted_memories.length > 0) {
          fetchMemories();
        }
      }, 2500);
    } catch {
      setTimeout(() => {
        setChatMessages((prev) => [
          ...prev,
          {
            role: "system",
            content: "Portal connection lost. Please verify the Python backend is active on localhost:8000.",
            timestamp: new Date(),
          },
        ]);
        setIsSending(false);
        setLiveLogs([]);
      }, 2500);
    }
  };

  const handleCreateMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMemoryKeyVal.trim() || !newMemoryValue.trim() || isAddingMemory) return;

    setIsAddingMemory(true);
    try {
      const ok = await createMemoryApi(userId, newMemoryKeyVal, newMemoryValue, newMemoryAgent);
      if (ok) {
        setNewMemoryKeyVal("");
        setNewMemoryValue("");
        setNewMemoryAgent("shared");
        await fetchMemories();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsAddingMemory(false);
    }
  };

  const handleDeleteMemory = async (key: string) => {
    try {
      const ok = await deleteMemoryApi(userId, key);
      if (ok) {
        await fetchMemories();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleClearMemories = async () => {
    if (!window.confirm(`Are you sure you want to wipe all memories for user '${userId}'?`)) return;
    try {
      const ok = await clearMemoriesApi(userId);
      if (ok) {
        await fetchMemories();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleSetUser = () => {
    setUserId(sessionUser);
  };

  return (
    <div className="min-h-screen bg-[#070913] text-zinc-100 flex overflow-hidden">
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        userId={userId}
        sessionUser={sessionUser}
        setSessionUser={setSessionUser}
        backendStatus={backendStatus}
        discordStatus={discordStatus}
        isSending={isSending}
        memoriesCount={memories.length}
        onRefresh={() => {
          checkHealth();
          fetchMemories();
        }}
        onSetUser={handleSetUser}
      />

      <main className="flex-1 flex flex-col min-w-0 bg-[#070913]">
        {/* Header */}
        <header className="h-16 border-b border-[#1e295d]/30 bg-[#0c0f24]/50 backdrop-blur-md px-8 flex items-center justify-between z-10 shrink-0">
          <div className="flex items-center gap-2">
            <span className="text-xs text-zinc-400 bg-zinc-900 border border-zinc-800 rounded-md px-2 py-0.5">
              WORKSPACE
            </span>
            <span className="text-zinc-400 text-xs font-semibold">/</span>
            <span className="text-zinc-200 text-xs font-bold capitalize">{currentTab}</span>
          </div>

          <div className="flex items-center gap-4">
            <div className="bg-[#121633] border border-[#1e295d]/50 rounded-xl px-4 py-1.5 flex items-center gap-2.5">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-md shadow-emerald-500/50"></div>
              <span className="text-xs font-semibold text-zinc-200">User Context: {userId}</span>
            </div>
          </div>
        </header>

        {/* Dynamic page context */}
        <div className="flex-1 overflow-y-auto p-8">
          {currentTab === "dashboard" && (
            <DashboardPage
              memoriesCount={memories.length}
              userId={userId}
              onTabChange={setCurrentTab}
              onWipeCache={handleClearMemories}
            />
          )}

          {currentTab === "chat" && (
            <ChatPage
              chatMessages={chatMessages}
              messageInput={messageText}
              setMessageInput={setMessageText}
              isSending={isSending}
              liveLogs={liveLogs}
              onSendMessage={handleSendMessage}
              chatEndRef={chatEndRef}
            />
          )}

          {currentTab === "agents" && <RosterPage />}

          {currentTab === "memory" && (
            <MemoryPage
              memories={memories}
              searchMemoryQuery={searchMemoryQuery}
              setSearchMemoryQuery={setSearchMemoryQuery}
              isMemoriesLoading={isMemoriesLoading}
              newMemoryKey={newMemoryKeyVal}
              setNewMemoryKey={setNewMemoryKeyVal}
              newMemoryValue={newMemoryValue}
              setNewMemoryValue={setNewMemoryValue}
              newMemoryAgent={newMemoryAgent}
              setNewMemoryAgent={setNewMemoryAgent}
              isAddingMemory={isAddingMemory}
              onWipeCache={handleClearMemories}
              onCreateMemory={handleCreateMemory}
              onDeleteMemory={handleDeleteMemory}
            />
          )}
        </div>
      </main>
    </div>
  );
}
