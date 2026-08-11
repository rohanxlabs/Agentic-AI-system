/**
 * API service layer — single source of truth for all backend communication.
 */

import axios from "axios";
import { env } from "@/config/env";
import {
  RunRequest,
  RunResponse,
  StreamEvent,
  Session,
  MemoryStats,
  AgentStatus,
  Tool,
  Metrics,
} from "@/types";

export type { StreamEvent };

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    ...(env.apiKey ? { "X-API-Key": env.apiKey } : {}),
  },
});

/**
 * Run the Agentic AI System with the given goal (non-streaming).
 */
export async function runSystem(payload: RunRequest): Promise<RunResponse> {
  const { data } = await apiClient.post<RunResponse>("/run", payload);
  return data;
}

/**
 * Run the Agentic AI System with streaming progress updates via SSE.
 */
export async function* runSystemStream(
  payload: RunRequest,
  options?: { signal?: AbortSignal }
): AsyncGenerator<StreamEvent, void, unknown> {
  const response = await fetch(`${env.apiUrl}/run/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(env.apiKey ? { "X-API-Key": env.apiKey } : {}),
    },
    body: JSON.stringify(payload),
    signal: options?.signal,
  });

  if (!response.ok) {
    throw new Error(`Stream error: ${response.statusText}`);
  }

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No response body");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed || !trimmed.startsWith("data: ")) continue;
      const json = trimmed.slice(6).trim();
      if (!json || json === "[DONE]") continue;
      try {
        yield JSON.parse(json) as StreamEvent;
      } catch {
        // skip malformed events
      }
    }
  }
}

/**
 * Check the health of the API.
 */
export async function checkHealth(): Promise<{ status: string; message: string }> {
  const { data } = await apiClient.get<{ message: string; status: string }>("/");
  return { status: data.status, message: data.message };
}

/**
 * Session management endpoints
 */
export async function getSessions(): Promise<Session[]> {
  const { data } = await apiClient.get<Session[] | { sessions: Session[] }>("/sessions");
  // Handle both array and {sessions: [...]} shapes for robustness
  return Array.isArray(data) ? data : (data as { sessions: Session[] }).sessions ?? [];
}

export async function createSession(goal?: string): Promise<Session> {
  const { data } = await apiClient.post<Session>("/sessions", { goal });
  return data;
}

export async function getSession(id: string): Promise<Session> {
  const { data } = await apiClient.get<Session>(`/sessions/${id}`);
  return data;
}

export async function deleteSession(id: string): Promise<void> {
  await apiClient.delete(`/sessions/${id}`);
}

/**
 * Memory statistics
 */
export async function getMemoryStats(): Promise<MemoryStats> {
  const { data } = await apiClient.get<MemoryStats>("/memory/stats");
  return data;
}

/**
 * Agent statuses
 */
export async function getAgentStatuses(): Promise<AgentStatus[]> {
  const { data } = await apiClient.get<AgentStatus[]>("/agents/status");
  return data;
}

/**
 * Available tools
 */
export async function getTools(): Promise<Tool[]> {
  const { data } = await apiClient.get<Tool[]>("/tools");
  return data;
}

/**
 * System metrics
 */
export async function getMetrics(): Promise<Metrics> {
  const { data } = await apiClient.get<Metrics>("/metrics");
  return data;
}