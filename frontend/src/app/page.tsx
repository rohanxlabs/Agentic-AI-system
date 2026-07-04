"use client";

import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/feedback/empty-state";
import { Activity, Inbox, Rocket } from "lucide-react";

const stats = [
  { label: "Active Agents", value: "12", change: "+2" },
  { label: "Tasks Completed", value: "1,284", change: "+18%" },
  { label: "Success Rate", value: "98.5%", change: "+0.3%" },
  { label: "Avg Latency", value: "240ms", change: "-12%" },
];

const gettingStartedItems = [
  { title: "Workspace", description: "Interactive agent workspace", icon: Inbox },
  { title: "Analytics", description: "Real-time performance metrics", icon: Activity },
  { title: "Agents", description: "Manage and configure agents", icon: Rocket },
];

export default function DashboardPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-8"
    >
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Welcome to Agentic AI System
        </h1>
        <p className="text-muted-foreground mt-1">
          Monitor your autonomous agents and system performance
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.label}>
            <Card.Header>
              <Card.Title className="text-sm font-medium text-muted-foreground">
                {stat.label}
              </Card.Title>
            </Card.Header>
            <Card.Content>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                {stat.change} from last hour
              </p>
            </Card.Content>
          </Card>
        ))}
      </div>

      <Card>
        <Card.Header>
          <Card.Title>Recent Activities</Card.Title>
        </Card.Header>
        <Card.Content>
          <EmptyState
            icon={<Activity className="h-5 w-5" />}
            title="No recent activity"
            description="Activities will appear here as your agents work."
          />
        </Card.Content>
      </Card>

      <div>
        <h2 className="text-xl font-semibold mb-4">Getting Started</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {gettingStartedItems.map((item) => {
            const Icon = item.icon;
            return (
              <Card key={item.title} variant="muted" className="opacity-60">
                <Card.Header>
                  <div className="flex items-center gap-3">
                    <Icon className="h-5 w-5 text-muted-foreground" />
                    <Card.Title>{item.title}</Card.Title>
                  </div>
                </Card.Header>
                <Card.Content>
                  <p className="text-sm text-muted-foreground">{item.description}</p>
                  <Button variant="outline" size="sm" className="mt-4 w-full" disabled>
                    Coming Soon
                  </Button>
                </Card.Content>
              </Card>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
