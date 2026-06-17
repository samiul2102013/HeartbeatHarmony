import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listUsers, deleteUser, type AdminUser } from "./users";

export function useUsers() {
  return useQuery({
    queryKey: ["admin", "users"],
    queryFn: () => listUsers(),
    select: (res: any) => {
      const source = res?.data ?? res?.results ?? res?.result ?? res ?? [];
      return Array.isArray(source) ? source : (source?.results ?? []);
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
