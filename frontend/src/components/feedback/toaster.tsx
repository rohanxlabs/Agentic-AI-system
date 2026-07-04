"use client";

import * as React from "react";
import {
  ToastProvider as RadixProvider,
  ToastViewport,
  Toast,
  ToastClose,
  ToastTitle,
  ToastDescription,
} from "@/components/ui/toast";
import { useToastStore, type ToasterToast } from "./toaster-context";

type ToasterToastProps = ToasterToast;

function Toasts() {
  const toasts = useToastStore((s) => s.toasts);
  return (
    <>
      {toasts.map((toast) => (
        <Toast key={toast.id} variant={toast.variant} {...(toast as ToasterToastProps)}>
          <div className="flex-1">
            {toast.title && <ToastTitle>{toast.title}</ToastTitle>}
            {toast.description && (
              <ToastDescription>{toast.description}</ToastDescription>
            )}
          </div>
          <ToastClose />
        </Toast>
      ))}
      <ToastViewport />
    </>
  );
}

export function Toaster() {
  return (
    <RadixProvider>
      <Toasts />
    </RadixProvider>
  );
}
