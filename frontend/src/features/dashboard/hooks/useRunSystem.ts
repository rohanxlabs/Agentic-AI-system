"use client";

import { useMutation, type UseMutationOptions } from "@tanstack/react-query";
import { runSystem } from "@/services/api";
import type { RunRequest, RunResponse } from "@/types";

export function useRunSystem(
  options?: UseMutationOptions<RunResponse, Error, RunRequest>
) {
  return useMutation({
    mutationFn: runSystem,
    ...options,
  });
}
