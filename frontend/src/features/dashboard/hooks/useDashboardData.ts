import { useQuery } from "@tanstack/react-query";
import { getMetrics, getSessions, getMemoryStats, getAgentStatuses, getTools } from "@/services/api";

export function useDashboardData() {
  const {
    data: metrics,
    isLoading: metricsLoading,
    error: metricsError,
  } = useQuery({
    queryKey: ["metrics"],
    queryFn: getMetrics,
    refetchInterval: 30000,
  });

  const {
    data: sessions = [],
    isLoading: sessionsLoading,
    error: sessionsError,
  } = useQuery({
    queryKey: ["sessions"],
    queryFn: getSessions,
  });

  const {
    data: memoryStats,
    isLoading: memoryLoading,
    error: memoryError,
  } = useQuery({
    queryKey: ["memoryStats"],
    queryFn: getMemoryStats,
  });

  const {
    data: agentStatuses = [],
    isLoading: agentsLoading,
    error: agentsError,
  } = useQuery({
    queryKey: ["agentStatuses"],
    queryFn: getAgentStatuses,
  });

  const {
    data: tools = [],
    isLoading: toolsLoading,
    error: toolsError,
  } = useQuery({
    queryKey: ["tools"],
    queryFn: getTools,
  });

  return {
    metrics,
    sessions,
    memoryStats,
    agentStatuses,
    tools,
    isLoading:
      metricsLoading ||
      sessionsLoading ||
      memoryLoading ||
      agentsLoading ||
      toolsLoading,
    error:
      metricsError ||
      sessionsError ||
      memoryError ||
      agentsError ||
      toolsError,
  };
}