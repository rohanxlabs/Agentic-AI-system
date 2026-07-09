import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Brain, TrendingUp } from "lucide-react";

export default function Dashboard() {
  return (
    <div className="p-6 space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Agentic AI System</h1>
          <p className="text-muted-foreground">Dashboard</p>
        </div>
        <Link href="/workspace">
          <Button>
            <Brain className="mr-2 h-4 w-4" />
            Open Workspace
          </Button>
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader>
            <p className="text-sm text-muted-foreground">Sessions</p>
            <p className="text-2xl font-semibold">--</p>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <p className="text-sm text-muted-foreground">Tasks</p>
            <p className="text-2xl font-semibold">--</p>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <p className="text-sm text-muted-foreground">Memory</p>
            <p className="text-2xl font-semibold">--%</p>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader>
            <p className="text-sm text-muted-foreground">API</p>
            <p className="text-2xl font-semibold">OK</p>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">Getting Started</h2>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <Link href="/workspace" className="block rounded-lg border border-border p-4 hover:bg-muted/50">
              <TrendingUp className="mb-2 h-5 w-5" />
              <h3 className="font-medium">Workspace</h3>
              <p className="text-sm text-muted-foreground">Run autonomous goals</p>
            </Link>
            <Link href="/sessions" className="block rounded-lg border border-border p-4 hover:bg-muted/50">
              <Brain className="mb-2 h-5 w-5" />
              <h3 className="font-medium">Sessions</h3>
              <p className="text-sm text-muted-foreground">Manage sessions</p>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
