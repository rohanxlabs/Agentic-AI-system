import { useQuery } from "@tanstack/react-query";
import { getTools } from "@/services/api";

export function useTools() {
  return useQuery({
    queryKey: ["tools"],
    queryFn: getTools,
  });
}