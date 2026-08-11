/**
 * Global type declarations.
 */

export type Theme = "light" | "dark" | "system";

export type RunRequest = {
  goal: string;
  session_id?: string;
  enable_tools?: boolean;
};

export type RunResponse = {
  results: string[];
  session_id: string;
};

export type StreamEvent =
  | { type: "plan"; content: string }
  | { type: "step_start"; step: string; agent?: string; iteration?: number; step_number?: number; total_steps?: number }
  | { type: "tool_call"; tool: string; input: string; output: string; status: string }
  | { type: "step_result"; content: string; agent: string }
  | { type: "critique"; content: string }
  | { type: "complete"; result: string; session_id?: string }
  | { type: "error"; message: string };

export type NavItem = {
  label: string;
  href: string;
  icon?: React.ComponentType<{ className?: string }>;
  disabled?: boolean;
};

export type Breadcrumb = {
  label: string;
  href?: string;
};

// New types for extended API

export interface Session {
  id: string;
  created_at: string;
  last_used: string;
  goal?: string;
  status: "idle" | "running" | "completed" | "error";
}

export interface MemoryStats {
  short_term: {
    count: number;
    max_size: number;
    usage_percent: number;
  };
  long_term: {
    count: number;
    growth_rate: number;
  };
}

export interface AgentStatus {
  name: string;
  status: "idle" | "busy" | "error";
  current_task: string | null;
  last_activity: string;
  task_count: number;
  avg_response_time: number;
}

export interface Tool {
  name: string;
  description: string;
  parameters: Record<string, unknown>;
  is_enabled: boolean;
  usage_count: number;
}

export interface Metrics {
  uptime: string;
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  avg_response_time: number;
  active_sessions: number;
  memory_usage: {
    used: number;
    total: number;
    unit: string;
  };
}