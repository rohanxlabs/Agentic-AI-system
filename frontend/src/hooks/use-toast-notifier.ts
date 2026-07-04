"use client";

import { useToast } from "@/components/feedback/toast-consumer";

export function useToasts() {
  const { toast, toasts, dismiss } = useToast();

  return {
    toasts,
    dismiss,
    success: (title: string, description?: string) => {
      toast({ title, description, variant: "success" });
    },
    error: (title: string, description?: string) => {
      toast({ title, description, variant: "error" });
    },
    info: (title: string, description?: string) => {
      toast({ title, description, variant: "default" });
    },
  };
}
