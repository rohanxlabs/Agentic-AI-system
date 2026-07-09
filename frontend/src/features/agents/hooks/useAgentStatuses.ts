import { useQuery } from "@tanstack/react-query";
import { getAgentStatuses } from "@/services/api";

export function useAgentStatuses() {
  return useQuery({
    queryKey: ["agentStatuses"],
    queryFn: getAgentStatuses,
    refetchInterval: 10000, // Update every 10 seconds
  });
}