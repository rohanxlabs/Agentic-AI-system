"use client";

import { type LucideIcon } from "lucide-react";
import { type ComponentType } from "react";
import { cn } from "@/lib/utils";

interface NavItemProps {
  label: string;
  href: string;
  icon?: ComponentType<{ className?: string }>;
  isActive?: boolean;
  disabled?: boolean;
  collapsed?: boolean;
}

export function NavItem({
  label,
  href,
  icon: Icon,
  isActive,
  disabled,
  collapsed,
}: NavItemProps) {
  return (
    <a
      href={href}
      aria-current={isActive ? "page" : undefined}
      aria-disabled={disabled}
      className={cn(
        "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        isActive
          ? "bg-muted text-foreground"
          : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
        disabled && "cursor-not-allowed opacity-50",
        collapsed && "justify-center px-2"
      )}
    >
      {Icon && <Icon className="h-4 w-4 shrink-0" />}
      {!collapsed && <span className="truncate">{label}</span>}
    </a>
  );
}
