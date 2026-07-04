"use client";

import { create } from "zustand";

export type ToasterToast = {
  id: string;
  title?: string;
  description?: string;
  variant?: "default" | "success" | "error";
  duration?: number;
};

interface ToastState {
  toasts: ToasterToast[];
  toast: (props: Omit<ToasterToast, "id">) => string;
  dismiss: (id: string) => void;
}

let toastId = 0;

export const useToastStore = create<ToastState>((set, get) => ({
  toasts: [],
  toast: ({ title, description, variant, duration = 5000 }) => {
    const id = `toast-${++toastId}-${Date.now()}`;
    set((state) => ({
      toasts: [...state.toasts, { id, title, description, variant, duration }],
    }));
    setTimeout(() => get().dismiss(id), duration);
    return id;
  },
  dismiss: (id) =>
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    })),
}));
