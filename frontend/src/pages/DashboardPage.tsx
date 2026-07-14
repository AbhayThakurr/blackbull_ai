import React from "react";
import { Dashboard } from "../components";
import { AGENTS_DATA } from "../constants";

interface DashboardPageProps {
  memoriesCount: number;
  userId: string;
  onTabChange: (tab: "dashboard" | "chat" | "agents" | "memory") => void;
  onWipeCache: () => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  memoriesCount,
  userId,
  onTabChange,
  onWipeCache,
}) => {
  return (
    <Dashboard
      memoriesCount={memoriesCount}
      userId={userId}
      agents={AGENTS_DATA}
      onTabChange={onTabChange}
      onWipeCache={onWipeCache}
    />
  );
};
