"use client";

import { useAgentStatuses } from "@/features/agents/hooks/useAgentStatuses";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Code, TrendingUp, Users, Clock, Activity, Zap, Server } from "lucide-react";

export default function Agents() {
  const { data: agentStatuses = [], isLoading, error } = useAgentStatuses();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">Loading agent statuses...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Error Loading Agents</h2>
          <p className="text-muted-foreground mb-6">
            {error instanceof Error ? error.message : "An unknown error occurred"}
          </p>
          <Button
            variant="default"
            onClick={() => window.location.reload()}
            className="mt-4"
          >
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Agent Monitor</h1>
      <p className="text-muted-foreground mb-6">
        Real-time status of all AI agents in the system
      </p>

      <div className="grid gap-6">
        {agentStatuses.map((agent) => (
          <Card key={agent.name} className="h-full">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-foreground">
                  {agent.name}
                </h2>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      agent.status === "busy"
                        ? "default"
                        : agent.status === "error"
                        ? "destructive"
                        : "secondary"
                    }
                  >
                    {agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  </Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Brain className="h-4 w-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Current Task
                    </p>
                    <p className="text-xs text-foreground truncate max-w-xs">
                      {agent.current_task || "Idle"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Activity className="h-4 w-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Last Activity
                    </p>
                    <p className="text-xs text-foreground">
                      {new Date(agent.last_activity).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Zap className="h-4 w-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Avg Response Time
                    </p>
                    <p className="text-xs text-foreground">
                      {agent.avg_response_time.toFixed(2)}s
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Server className="h-4 w-4 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Tasks Processed
                    </p>
                    <p className="text-xs text-foreground">
                      {agent.task_count}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
