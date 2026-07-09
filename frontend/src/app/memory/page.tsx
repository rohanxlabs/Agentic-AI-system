"use client";

import { useMemoryStats } from "@/features/memory/hooks/useMemoryStats";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Brain, Database, Clock, Filter, TrendingUp, Server, Search } from "lucide-react";

export default function Memory() {
  const { data: memoryStats, isLoading, error } = useMemoryStats();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">Loading memory statistics...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Error Loading Memory</h2>
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
      <h1 className="text-2xl font-bold text-foreground mb-6">Memory Explorer</h1>
      <p className="text-muted-foreground mb-6">
        Monitor and browse the agent&apos;s memory systems
      </p>

      <div className="grid gap-6">
        <div className="col-span-2 lg:col-span-1">
          <Card className="h-full">
            <CardHeader className="pb-4">
              <h2 className="text-lg font-semibold text-foreground">
                Memory Statistics
              </h2>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="border rounded-lg border-border bg-card p-4">
                  <h3 className="font-medium text-foreground mb-3">Short-Term Memory</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Count</span>
                      <span className="text-sm font-medium text-foreground">
                        {memoryStats?.short_term.count || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Max Size</span>
                      <span className="text-sm font-medium text-foreground">
                        {memoryStats?.short_term.max_size || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Usage</span>
                      <div className="flex-1">
                        <div className="w-full bg-muted/50 h-2 rounded">
                          <div
                            className="h-2 bg-primary rounded"
                            style={{
                              width:
                                (memoryStats?.short_term.usage_percent || 0) /
                                100 *
                                100,
                            }}
                          ></div>
                        </div>
                        <span className="ml-2 text-xs text-muted-foreground">
                          {(memoryStats?.short_term.usage_percent || 0).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="border rounded-lg border-border bg-card p-4">
                  <h3 className="font-medium text-foreground mb-3">Long-Term Memory</h3>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Count</span>
                      <span className="text-sm font-medium text-foreground">
                        {memoryStats?.long_term.count || 0}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Growth Rate</span>
                      <span className="text-sm font-medium text-foreground">
                        {memoryStats?.long_term.growth_rate || 0}/day
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-2 lg:col-span-1">
          <Card className="h-full">
            <CardHeader className="pb-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-foreground">
                  Memory Browser
                </h2>
                <Button variant="outline" size="icon">
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-muted-foreground block">
                    Search memories
                  </label>
                  <input
                    type="text"
                    placeholder="Search memories..."
                    className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                  />
                </div>
                <div className="space-y-3">
                  {/* Placeholder for memory entries */}
                  <div className="h-40 flex items-center justify-center text-muted-foreground">
                    Memory browsing interface coming soon
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}