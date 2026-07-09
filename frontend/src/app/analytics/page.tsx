"use client";

import { useMetrics } from "@/features/analytics/hooks/useMetrics";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { TrendingUp, Activity, Zap, Server } from "lucide-react";

export default function Analytics() {
  const { data: metrics, isLoading, error } = useMetrics();

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">Loading analytics...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Error Loading Analytics</h2>
          <p className="text-muted-foreground mb-6">
            {error instanceof Error ? error.message : "An unknown error occurred"}
          </p>
          <Button variant="default" onClick={() => window.location.reload()} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-foreground mb-6">Analytics Dashboard</h1>
      <p className="text-muted-foreground mb-6">
        Monitor system performance and usage metrics
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        <div className="space-y-6">
          <Card className="border">
            <CardHeader className="pb-4">
              <h2 className="text-lg font-semibold text-foreground">
                <Activity className="mr-2 h-4 w-4" /> Request Statistics
              </h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <div className="flex items-center justify-center h-12 w-12 bg-primary/20 rounded-lg">
                  <TrendingUp className="h-5 w-5 text-primary" />
                </div>
                <p className="mt-2 text-sm font-medium text-foreground">
                  {metrics?.total_requests || 0}
                </p>
                <p className="text-xs text-muted-foreground">Total Requests</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border">
            <CardHeader className="pb-4">
              <h2 className="text-lg font-semibold text-foreground">
                <Zap className="mr-2 h-4 w-4" /> Performance
              </h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Avg Response Time</span>
                  <span className="text-sm font-medium text-foreground">
                    {(metrics?.avg_response_time || 0).toFixed(2)}s
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Success Rate</span>
                  <span className="text-sm font-medium text-foreground">
                    {(metrics && metrics.total_requests > 0) ? ((metrics.successful_requests || 0) / metrics.total_requests * 100).toFixed(1) + "%" : "0%"}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="border">
            <CardHeader className="pb-4">
              <h2 className="text-lg font-semibold text-foreground">
                <Server className="mr-2 h-4 w-4" /> System
              </h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Uptime</span>
                  <span className="text-sm font-medium text-foreground">
                    {metrics?.uptime || "N/A"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Active Sessions</span>
                  <span className="text-sm font-medium text-foreground">
                    {metrics?.active_sessions || 0}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}