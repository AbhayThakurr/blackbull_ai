import { BACKEND_URL } from "../constants";
import type { MemoryItem } from "../types";

// Check health of backend
export const checkHealthApi = async (): Promise<boolean> => {
  try {
    const res = await fetch(`${BACKEND_URL}/`);
    return res.ok;
  } catch {
    return false;
  }
};

// Fetch user memories from API
export const fetchMemoriesApi = async (userId: string): Promise<MemoryItem[]> => {
  if (!userId.trim()) return [];
  const res = await fetch(`${BACKEND_URL}/memory/${encodeURIComponent(userId)}`);
  if (!res.ok) throw new Error("Failed to load memories");
  return await res.json();
};

// Create memory
export const createMemoryApi = async (
  userId: string,
  key: string,
  value: string,
  agentName: string
): Promise<boolean> => {
  const res = await fetch(`${BACKEND_URL}/memory/${encodeURIComponent(userId)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ key, value, agent_name: agentName }),
  });
  return res.ok;
};

// Delete memory
export const deleteMemoryApi = async (userId: string, key: string): Promise<boolean> => {
  const res = await fetch(
    `${BACKEND_URL}/memory/${encodeURIComponent(userId)}/${encodeURIComponent(key)}`,
    { method: "DELETE" }
  );
  return res.ok;
};

// Clear memories
export const clearMemoriesApi = async (userId: string): Promise<boolean> => {
  const res = await fetch(`${BACKEND_URL}/memory/${encodeURIComponent(userId)}`, {
    method: "DELETE",
  });
  return res.ok;
};

// Send chat message
export const sendChatMessageApi = async (
  userId: string,
  message: string
): Promise<{ response: string; session_id: string; extracted_memories: any[] }> => {
  const res = await fetch(`${BACKEND_URL}/chat/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-User-Id": userId,
    },
    body: JSON.stringify({ message, user_id: userId }),
  });
  if (!res.ok) throw new Error("Failed to communicate with chat service");
  return await res.json();
};

// Heuristic: simulate routing logs based on text content
export const getSimulatedRoutingLogs = (text: string, userId: string): { agent: string; steps: string[] } => {
  const lowerText = text.toLowerCase();
  const baseSteps = ["Request received", `Active User ID: ${userId}`];
  
  if (
    lowerText.includes("search") ||
    lowerText.includes("google") ||
    lowerText.includes("youtube") ||
    lowerText.includes("web") ||
    lowerText.includes("browse") ||
    lowerText.includes("url") ||
    lowerText.includes("link") ||
    lowerText.includes("netflix")
  ) {
    return {
      agent: "Finral",
      steps: [
        ...baseSteps,
        "Supervisor Node: Captain Yami loading memories...",
        "Graph State: Injecting User Memory Context",
        "Supervisor Node: Captain Yami matched web action.",
        "Routing trigger: delegate_to_finral()",
        "Transitioning state: [yami] ──> [finral]",
        "Agent Node: Finral executing spatial search tools...",
      ],
    };
  } else if (
    lowerText.includes("calendar") ||
    lowerText.includes("meet") ||
    lowerText.includes("schedule") ||
    lowerText.includes("email") ||
    lowerText.includes("summary") ||
    lowerText.includes("event")
  ) {
    return {
      agent: "Noelle",
      steps: [
        ...baseSteps,
        "Supervisor Node: Captain Yami loading memories...",
        "Graph State: Injecting User Memory Context",
        "Supervisor Node: Captain Yami matched schedule action.",
        "Routing trigger: delegate_to_noelle()",
        "Transitioning state: [yami] ──> [noelle]",
        "Agent Node: Noelle loading Google credentials & executing calendar tools...",
      ],
    };
  } else {
    return {
      agent: "Yami",
      steps: [
        ...baseSteps,
        "Supervisor Node: Captain Yami loading memories...",
        "Graph State: Injecting User Memory Context",
        "Supervisor Node: Captain Yami handling query directly.",
        "Running system capabilities or conversational prompt...",
      ],
    };
  }
};
