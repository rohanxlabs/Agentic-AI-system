"use client";

import { Home, FlaskConical, BarChart3, Bot } from "lucide-react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const bottomNavItems = [
  { label: "Home", href: "/", icon: Home },
  { label: "Workspace", href: "/workspace", icon: FlaskConical, disabled: true },
  { label: "Analytics", href: "/analytics", icon: BarChart3, disabled: true },
  { label: "Agents", href: "/agents", icon: Bot, disabled: true },
];

export function MobileBottomNav() {
  const pathname = usePathname();

  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-50 flex h-16 items-center justify-around border-t border-border bg-background/95 backdrop-blur md:hidden"
      aria-label="Main navigation"
    >
      {bottomNavItems.map((item) => {
        const Icon = item.icon;
        const isActive = pathname === item.href;
        return (
          <a
            key={item.href}
            href={item.href}
            aria-current={isActive ? "page" : undefined}
            aria-disabled={item.disabled}
            className={cn(
              "flex flex-col items-center gap-0.5 py-2 text-xs transition-colors",
              isActive
                ? "text-foreground"
                : "text-muted-foreground hover:text-foreground",
              item.disabled && "cursor-not-allowed opacity-50"
            )}
          >
            {Icon && <Icon className="h-5 w-5" />}
            {item.label}
          </a>
        );
      })}
    </nav>
  );
}