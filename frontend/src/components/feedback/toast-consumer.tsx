"use client";

import { useToastStore } from "@/components/feedback/toaster-context";

export function useToast() {
  const toast = useToastStore((s) => s.toast);
  const dismiss = useToastStore((s) => s.dismiss);
  const toasts = useToastStore((s) => s.toasts);

  return {
    toast,
    toasts,
    dismiss,
  };
}
