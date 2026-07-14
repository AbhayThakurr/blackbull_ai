export interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: Date;
  agent?: string;
  extracted?: Array<{ key: string; value: string }>;
  logs?: string[];
}

export interface MemoryItem {
  key: string;
  value: string;
  agent_name: string;
}

export interface AgentDetails {
  id: string;
  name: string;
  role: string;
  magic: string;
  color: string;
  borderColor: string;
  glowColor: string;
  status: "ACTIVE" | "INACTIVE";
  description: string;
  tools: string[];
  avatar: string;
}
