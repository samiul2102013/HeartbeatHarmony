import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listCheckins, deleteCheckin, type CheckinQuery, type AdminCheckIn } from "./checkins";

export function useCheckins(query?: CheckinQuery) {
  return useQuery({
    queryKey: ["admin", "checkins", query],
    queryFn: () => listCheckins(query),
    select: (res: any) => {
      const items = res?.data ?? res?.results ?? res?.result ?? res ?? [];
      return {
        checkins: (Array.isArray(items) ? items : (items?.results ?? [])) as AdminCheckIn[],
        metadata: res?.metadata ?? null,
      };
    },
  });
}

export function useDeleteCheckin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteCheckin(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "checkins"] });
    },
  });
}
