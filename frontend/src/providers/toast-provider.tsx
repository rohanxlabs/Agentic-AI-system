"use client";

import { Toaster } from "@/components/feedback/toaster";

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <Toaster />
    </>
  );
}
