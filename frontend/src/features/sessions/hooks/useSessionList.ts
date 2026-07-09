import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getSessions, createSession, deleteSession } from "@/services/api";
import type { Session } from "@/types";

export function useSessionList() {
  const queryClient = useQueryClient();

  const {
    data: sessions = [],
    isLoading,
    error,
  } = useQuery({
    queryKey: ["sessions"],
    queryFn: getSessions,
  });

  const createSessionMutation = useMutation({
    mutationFn: createSession,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sessions"] });
    },
  });

  const deleteSessionMutation = useMutation({
    mutationFn: deleteSession,
    onSuccess: (_, sessionId) => {
      queryClient.setQueryData(["sessions"], (old: Session[] = []) =>
        old.filter((session) => session.id !== sessionId)
      );
    },
  });

  return {
    sessions,
    isLoading,
    error,
    createSession: createSessionMutation.mutateAsync,
    deleteSession: deleteSessionMutation.mutateAsync,
  };
}