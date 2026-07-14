import React from "react";
import { AgentHub } from "../components";
import { AGENTS_DATA } from "../constants";

export const RosterPage: React.FC = () => {
  return <AgentHub agents={AGENTS_DATA} />;
};
