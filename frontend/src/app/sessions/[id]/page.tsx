"use client";

import { useSession } from "@/features/sessions/hooks/useSession";
import { useSessionList } from "@/features/sessions/hooks/useSessionList";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Server, Brain, Code, TrendingUp, Users, Clock, X } from "lucide-react";
import { useState, use } from "react";

export default function SessionDetail({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { data: session, isLoading, error } = useSession(id);
  const { deleteSession } = useSessionList();
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteSession = async () => {
    if (window.confirm("Are you sure you want to delete this session?")) {
      try {
        setIsDeleting(true);
        await deleteSession(id);
        router.push("/sessions");
      } catch (err) {
        setIsDeleting(false);
        window.alert((err as Error).message);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="p-6">
        <div className="flex h-64 items-center justify-center">
          <div className="text-muted-foreground">Loading session...</div>
        </div>
      </div>
    );
  }

  if (error || !session) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <h2 className="text-2xl font-bold mb-4">Session Not Found</h2>
          <p className="text-muted-foreground mb-6">
            The session you are looking for does not exist.
          </p>
          <Button
            variant="default"
            onClick={() => router.push("/sessions")}
            className="mt-4"
          >
            Back to Sessions
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground">
            Session Details
          </h1>
          <p className="text-muted-foreground mt-2">
            {session.goal || "No goal specified"}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            onClick={() => {
              router.push(`/workspace?session_id=${id}`);
            }}
          >
            Resume Session
          </Button>
          <Button
            variant="destructive"
            onClick={handleDeleteSession}
            disabled={isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete Session"}
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        <div className="col-span-2 lg:col-span-1">
          <Card className="h-full">
            <CardHeader>
              <h2 className="text-lg font-semibold text-foreground">
                Session Information
              </h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <Server className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Session ID</p>
                    <p className="text-muted-foreground truncate max-w-xs">
                      {session.id}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Brain className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Goal</p>
                    <p className="text-muted-foreground line-clamp-2">
                      {session.goal || "No goal specified"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Created At</p>
                    <p className="text-muted-foreground">
                      {new Date(session.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Clock className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium text-foreground">Last Used</p>
                    <p className="text-muted-foreground">
                      {new Date(session.last_used).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-2 lg:col-span-1">
          <Card className="h-full">
            <CardHeader>
              <h2 className="text-lg font-semibold text-foreground">
                Session Status
              </h2>
            </CardHeader>
            <CardContent className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="flex h-12 w-12 items-center justify-center rounded-md">
                  {session.status === "running" && (
                    <div className="bg-primary/20 text-primary flex items-center justify-center">
                      <Brain className="h-6 w-6 animate-spin" />
                    </div>
                  )}
                  {session.status === "completed" && (
                    <div className="bg-success/20 text-success flex items-center justify-center">
                      <span className="h-6 w-6 text-success">✓</span>
                    </div>
                  )}
                  {session.status === "error" && (
                    <div className="bg-destructive/20 text-destructive flex items-center justify-center">
                      <X className="h-6 w-6" />
                    </div>
                  )}
                  {session.status === "idle" && (
                    <div className="bg-muted/20 text-muted-foreground flex items-center justify-center">
                      <Server className="h-6 w-6" />
                    </div>
                  )}
                </div>
                <p className="mt-4 text-lg font-semibold text-foreground">
                  {session.status.charAt(0).toUpperCase() + session.status.slice(1)}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
