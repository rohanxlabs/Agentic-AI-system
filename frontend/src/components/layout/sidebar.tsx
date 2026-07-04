"use client";

import * as React from "react";
import { ChevronLeft, ChevronRight, Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement> {
  collapsed: boolean;
  onToggle: () => void;
  children: React.ReactNode;
}

export function Sidebar({
  collapsed,
  onToggle,
  children,
  className,
  ...props
}: SidebarProps) {
  return (
    <aside
      className={cn(
        "hidden border-r border-border bg-card transition-all duration-300 md:flex md:flex-col md:fixed md:inset-y-0 md:z-40",
        collapsed ? "md:w-16" : "md:w-64",
        className
      )}
      {...props}
    >
      <div className="flex h-16 items-center justify-between border-b border-border px-4">
        {!collapsed && (
          <span className="text-sm font-semibold tracking-tight">
            Agentic AI
          </span>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className={cn(
            "h-7 w-7 text-muted-foreground hover:text-foreground",
            collapsed && "mx-auto"
          )}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>
      <div
        className={cn(
          "flex-1 overflow-y-auto scrollbar-thin py-4",
          collapsed ? "px-2" : "px-3"
        )}
      >
        {children}
      </div>
    </aside>
  );
}
