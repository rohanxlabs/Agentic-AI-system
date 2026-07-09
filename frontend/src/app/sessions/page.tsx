"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useSessionList } from "@/features/sessions/hooks/useSessionList";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Users, TrendingUp, Bot, Loader2 } from "lucide-react";
import { useToasts } from "@/hooks/use-toast-notifier";

export default function Sessions() {
  const { sessions, isLoading, error, createSession, deleteSession } = useSessionList();
  const { success, error: toastError } = useToasts();
  const router = useRouter();

  const [newGoal, setNewGoal] = useState("");

  const handleNewSession = async () => {
    try {
      const session = await createSession(newGoal.trim() || undefined);
      router.push(`/sessions/${session.id}`);
    } catch (err) {
      toastError("Failed to create session", (err as Error).message);
    }
  };

  const handleCreateSession = async () => {
    if (!newGoal.trim()) return;
    try {
      await createSession(newGoal);
      setNewGoal("");
      success("Session created", "A new session has been created");
    } catch (err) {
      toastError("Failed to create session", (err as Error).message);
    }
  };

  const handleDeleteSession = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this session?")) {
      try {
        await deleteSession(id);
        success("Session deleted", "The session has been deleted");
      } catch (err) {
        toastError("Failed to delete session", (err as Error).message);
      }
    }
  };

  if (isLoading) return <div className="p-6 text-center">Loading...</div>;
  if (error) return <div className="p-6 text-center text-destructive">Error loading sessions</div>;

  return (
    <div className="p-6">
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between mb-6">
        <h1 className="text-2xl font-bold text-foreground">Session Management</h1>
        <div className="flex space-x-4">
          <Button variant="outline" onClick={handleNewSession}>
            New Session
          </Button>
          <Button
            variant="default"
            onClick={handleCreateSession}
            disabled={!newGoal.trim()}
            className="flex items-center gap-2"
          >
            {newGoal.length > 0 ? (
              <>
                <span className="mr-2">{newGoal.length}</span>/100
              </>
            ) : (
              <span>Quick Create</span>
            )}
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        <div className="border rounded-lg border-border bg-card/50 p-4">
          <div className="flex items-center space-x-3 mb-3">
            <input
              type="text"
              value={newGoal}
              onChange={(e) => setNewGoal(e.target.value)}
              placeholder="Enter goal for new session..."
              className="flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
            <Button
              variant="default"
              onClick={handleCreateSession}
              disabled={!newGoal.trim()}
              size="sm"
            >
              Create
            </Button>
          </div>
          {newGoal.length > 0 && (
            <div className="text-xs text-muted-foreground">
              {newGoal.length}/100 characters
            </div>
          )}
        </div>

        <div className="border rounded-lg border-border bg-card/50">
          <div className="px-4 py-3 border-b border-border">
            <h2 className="text-lg font-semibold text-foreground">Active Sessions</h2>
          </div>
          <div className="space-y-2">
            {sessions.length === 0 ? (
              <div className="p-6 text-center text-muted-foreground">
                No sessions found. Create a new session to get started.
              </div>
            ) : (
              sessions.map((session) => (
                <div key={session.id} className="border-b border-border py-3 last:border-b-0">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <h3 className="font-medium text-foreground">
                        {session.goal || "Unnamed Session"}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Created: {new Date(session.created_at).toLocaleString()} ·
                        Last used: {new Date(session.last_used).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className={`px-2 py-0.5 rounded-full text-xs ${
                        session.status === "running"
                          ? "bg-primary/20 text-primary"
                          : session.status === "completed"
                          ? "bg-success/20 text-success"
                          : session.status === "error"
                          ? "bg-destructive/20 text-destructive"
                          : "bg-muted/20 text-muted-foreground"
                      }`}>
                        {session.status}
                      </span>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => {
                          window.location.href = '/sessions/' + session.id;
                        }}
                      >
                        <Users className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="destructive"
                        size="icon"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteSession(session.id);
                        }}
                      >
                        <TrendingUp className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}