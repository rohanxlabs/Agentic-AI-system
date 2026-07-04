/**
 * Global type declarations.
 */

export type Theme = "light" | "dark" | "system";

export type RunRequest = {
  prompt: string;
  context?: Record<string, unknown>;
};

export type RunResponse = {
  results: string[];
  session_id: string;
};

export type StreamEvent =
  | { type: "start"; session_id: string }
  | { type: "step"; agent: string; content: string; step: number }
  | { type: "complete"; result: string }
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
