/**
 * API service layer — single source of truth for all backend communication.
 */

import axios from "axios";
import { env } from "@/config/env";
import type { RunRequest, RunResponse, StreamEvent } from "@/types";

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
    ...(env.apiKey ? { "X-API-Key": env.apiKey } : {}),
  },
});

export async function runSystem(payload: RunRequest): Promise<RunResponse> {
  const { data } = await apiClient.post<RunResponse>("/run", payload);
  return data;
}

export async function* runSystemStream(
  payload: RunRequest
): AsyncGenerator<StreamEvent, void, unknown> {
  const response = await fetch(
    `${env.apiUrl}/run/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(env.apiKey ? { "X-API-Key": env.apiKey } : {}),
      },
      body: JSON.stringify(payload),
    }
  );

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

export async function checkHealth(): Promise<{ status: string; message: string }> {
  const { data } = await apiClient.get<{ message: string; status: string }>("/");
  return { status: data.status, message: data.message };
}
