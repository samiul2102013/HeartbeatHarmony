import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listUsers, deleteUser, type AdminUser, type UserQuery } from "./users";

export function useUsers(query?: UserQuery) {
  return useQuery({
    queryKey: ["admin", "users", query],
    queryFn: () => listUsers(query),
    select: (res: any) => {
      const items = res?.data ?? res?.results ?? res?.result ?? res ?? [];
      return {
        users: (Array.isArray(items) ? items : (items?.results ?? [])) as AdminUser[],
        metadata: res?.metadata ?? null,
      };
    },
  });
}

export function useDeleteUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteUser(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin", "users"] });
    },
  });
}
