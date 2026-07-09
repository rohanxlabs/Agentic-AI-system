import { useQuery } from "@tanstack/react-query";
import { getSession } from "@/services/api";

export function useSession(id: string) {
  return useQuery({
    queryKey: ["session", id],
    queryFn: () => getSession(id),
    enabled: !!id,
  });
}