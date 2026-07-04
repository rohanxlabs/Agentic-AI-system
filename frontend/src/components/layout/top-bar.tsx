"use client";

import { useThemeStore } from "@/store/theme-store";
import { useAppStore } from "@/store/app-store";
import {
  Monitor,
  Moon,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Sun,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface TopBarProps {
  className?: string;
}

export function TopBar({ className }: TopBarProps) {
  const { sidebarOpen, setSidebarOpen, setCommandPaletteOpen } = useAppStore();
  const { theme, toggleTheme, setTheme } = useThemeStore();

  return (
    <header
      className={cn(
        "sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/60",
        className
      )}
    >
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        className="hidden md:flex"
        aria-label="Toggle sidebar"
      >
        {sidebarOpen ? (
          <PanelLeftClose className="h-4 w-4" />
        ) : (
          <PanelLeftOpen className="h-4 w-4" />
        )}
      </Button>

      <div className="flex items-center gap-2">
        <span className="text-base font-semibold tracking-tight md:hidden">
          Agentic AI
        </span>
      </div>

      <div className="flex-1" />

      <Dialog open={false} onOpenChange={useAppStore.getState().setCommandPaletteOpen}>
        <DialogTrigger asChild>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setCommandPaletteOpen(true)}
            className="hidden md:flex w-64 justify-between text-muted-foreground"
          >
            <span className="flex items-center gap-2 text-sm">
              <Search className="h-4 w-4" />
              Search...
            </span>
            <span className="rounded border border-border px-1.5 py-0.5 text-xs">
              ⌘K
            </span>
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Command Palette</DialogTitle>
          </DialogHeader>
          <div className="py-8 text-center text-sm text-muted-foreground">
            Command palette coming soon
          </div>
        </DialogContent>
      </Dialog>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" aria-label="Toggle theme">
            {theme === "light" && <Sun className="h-4 w-4" />}
            {theme === "dark" && <Moon className="h-4 w-4" />}
            {theme === "system" && <Monitor className="h-4 w-4" />}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setTheme("light")}>
            <Sun className="mr-2 h-4 w-4" />
            Light
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("dark")}>
            <Moon className="mr-2 h-4 w-4" />
            Dark
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("system")}>
            <Monitor className="mr-2 h-4 w-4" />
            System
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
