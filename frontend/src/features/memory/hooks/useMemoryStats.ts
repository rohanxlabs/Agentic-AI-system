import { useQuery } from "@tanstack/react-query";
import { getMemoryStats } from "@/services/api";

export function useMemoryStats() {
  return useQuery({
    queryKey: ["memoryStats"],
    queryFn: getMemoryStats,
    refetchInterval: 15000, // Update every 15 seconds
  });
}