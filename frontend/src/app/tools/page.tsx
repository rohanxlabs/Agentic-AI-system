"use client";

import { useTools } from "@/features/tools/hooks/useTools";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Bot, Settings, Code, Activity, TrendingUp, Server } from "lucide-react";

export default function Tools() {
  const { data: tools, isLoading, error } = useTools();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">Loading tools...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Error Loading Tools</h2>
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
      <h1 className="text-2xl font-bold text-foreground mb-6">Tool Center</h1>
      <p className="text-muted-foreground mb-6">
        Browse and manage available AI tools
      </p>

      <div className="space-y-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-foreground">Available Tools</h2>
          <Button variant="outline" onClick={() => {}}>
            <Settings className="mr-2 h-4 w-4" /> Configure
          </Button>
        </div>

        <div className="space-y-4">
          {(tools ?? []).length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No tools available</p>
            </div>
          ) : (
            <>
              {tools!.map((tool) => (
                <Card key={tool.name} className="border border-border">
                  <CardHeader className="pb-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="font-medium text-foreground">
                          {tool.name}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {tool.description}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          variant={tool.is_enabled ? "secondary" : "outline"}
                        >
                          {tool.is_enabled ? "Enabled" : "Disabled"}
                        </Badge>
                        <Badge variant="secondary">
                          Used {tool.usage_count} times
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span>Parameters</span>
                        <span className="text-muted-foreground">
                          {Object.keys(tool.parameters).length} parameters
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </>
          )}
        </div>
      </div>
    </div>
  );
}