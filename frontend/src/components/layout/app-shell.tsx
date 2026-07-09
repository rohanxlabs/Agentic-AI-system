"use client";

import { type ReactNode } from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { TopBar } from "@/components/layout/top-bar";
import { MobileBottomNav } from "@/components/layout/mobile-bottom-nav";
import { useAppStore } from "@/store/app-store";
import { Home, FlaskConical, BarChart3, Bot, Settings, User, HelpCircle, Brain } from "lucide-react";

const sidebarNavItems = [
  { label: "Dashboard", href: "/", icon: Home },
  { label: "Workspace", href: "/workspace", icon: FlaskConical },
  { label: "Memory", href: "/memory", icon: Brain },
  { label: "Analytics", href: "/analytics", icon: BarChart3 },
  { label: "Agents", href: "/agents", icon: Bot },
  { label: "Settings", href: "/settings", icon: Settings },
  { label: "Profile", href: "/profile", icon: User },
  { label: "Help", href: "/help", icon: HelpCircle },
];

interface ShellProps {
  children: ReactNode;
}

export function AppShell({ children }: ShellProps) {
  const sidebarOpen = useAppStore((s) => s.sidebarOpen);
  const setSidebarOpen = useAppStore((s) => s.setSidebarOpen);

  return (
    <div className="min-h-screen flex bg-background text-foreground">
      <Sidebar
        collapsed={!sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      >
        <nav aria-label="Sidebar">
          {sidebarNavItems.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.href} className="mb-1">
                <a
                  href={item.href}
                  aria-current={false}
                  aria-disabled={false}
                  className={`
                    flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors
                    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
                    text-muted-foreground hover:bg-muted/50 hover:text-foreground
                    ${!sidebarOpen ? "justify-center px-2" : ""}
                  `}
                >
                  {Icon && <Icon className="h-4 w-4 shrink-0" />}
                  {sidebarOpen && (
                    <span className="truncate text-sm font-medium">
                      {item.label}
                    </span>
                  )}
                </a>
              </div>
            );
          })}
        </nav>
      </Sidebar>
      <div
        className={`flex flex-1 flex-col transition-all duration-300 ${
          sidebarOpen ? "md:pl-64" : "md:pl-16"
        }`}
      >
        <TopBar />
        <main className="flex-1 overflow-y-auto pb-16 md:pb-0">
          {children}
        </main>
      </div>
      <MobileBottomNav />
    </div>
  );
}