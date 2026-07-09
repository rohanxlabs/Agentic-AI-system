import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { HelpCircle, BookOpen, Code, Terminal, Server, Bot, Brain, Users } from "lucide-react";

export default function Help() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Help & Documentation</h1>
      <p className="text-muted-foreground mb-6">
        Get started with the Agentic AI System
      </p>

      <div className="space-y-8">
        <div className="border rounded-lg border-border bg-card/50">
          <div className="flex items-center space-x-3 mb-4">
            <HelpCircle className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground">Getting Started</h2>
          </div>
          <div className="space-y-4">
            <p className="text-muted-foreground">
              Welcome to the Agentic AI System! This guide will help you get started with creating and managing AI agents.
            </p>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <span className="w-3 h-3 bg-primary rounded" />
                </div>
                <div>
                  <h3 className="font-medium text-foreground">1. Create Your First Agent</h3>
                  <p className="text-sm">
                    Navigate to the Workspace and enter your goal to begin.
                  </p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <div className="flex-shrink-0">
                  <span className="w-3 h-3 bg-primary rounded" />
                </div>
                <div>
                  <h3 className="font-medium text-foreground">2. Monitor Agent Progress</h3>
                  <p className="text-sm">
                    Use the Agent Monitor to see how your agents are performing.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="border rounded-lg border-border bg-card/50">
          <div className="flex items-center space-x-3 mb-4">
            <BookOpen className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground">Core Features</h2>
          </div>
          <div className="grid gap-4">
            <div className="border rounded-lg border-border bg-card p-4">
              <h3 className="font-medium text-foreground">Workspace</h3>
              <p className="text-sm">
                Create and run AI agents with goals and watch their thought process.
              </p>
              <Link href="/workspace" className="text-sm font-medium text-primary hover:underline">
                Learn more →
              </Link>
            </div>
            <div className="border rounded-lg border-border bg-card p-4">
              <h3 className="font-medium text-foreground">Memory Explorer</h3>
              <p className="text-sm">
                Browse and search through agent memories.
              </p>
              <Link href="/memory" className="text-sm font-medium text-primary hover:underline">
                Learn more →
              </Link>
            </div>
            <div className="border rounded-lg border-border bg-card p-4">
              <h3 className="font-medium text-foreground">Agent Monitor</h3>
              <p className="text-sm">
                Watch your agents in real-time.
              </p>
              <Link href="/agents" className="text-sm font-medium text-primary hover:underline">
                Learn more →
              </Link>
            </div>
          </div>
        </div>

        <div className="border rounded-lg border-border bg-card/50">
          <div className="flex items-center space-x-3 mb-4">
            <Code className="h-5 w-5 text-primary" />
            <h2 className="text-lg font-semibold text-foreground">API Reference</h2>
          </div>
          <div className="space-y-4">
            <div className="grid gap-4">
              <div className="border rounded-lg border-border bg-card p-4">
                <h3 className="font-medium text-foreground">Run Agent</h3>
                <p className="text-muted-foreground mb-2">
                  POST /run
                </p>
                <pre className="bg-muted/50 p-3 rounded overflow-auto text-xs">
{`{ "goal": "Your goal here", "enableTools": true }`}
                </pre>
              </div>
              <div className="border rounded-lg border-border bg-card p-4">
                <h3 className="font-medium text-foreground">Stream Agent</h3>
                <p className="text-muted-foreground mb-2">
                  POST /run/stream
                </p>
                <p className="text-xs text-muted-foreground">
                  Returns a stream of events as the agent processes your request
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}