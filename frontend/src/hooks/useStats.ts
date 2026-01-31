"use client";

import { useQuery } from "@tanstack/react-query";
import { statsApi } from "@/lib/api";

// Query keys
export const statsKeys = {
  all: ["stats"] as const,
  dashboard: () => [...statsKeys.all, "dashboard"] as const,
};

// Fetch dashboard stats
export function useDashboardStats() {
  return useQuery({
    queryKey: statsKeys.dashboard(),
    queryFn: () => statsApi.getDashboard(),
  });
}
