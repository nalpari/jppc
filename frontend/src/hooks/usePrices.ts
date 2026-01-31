"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { pricesApi } from "@/lib/api";

// Query keys
export const priceKeys = {
  all: ["prices"] as const,
  lists: () => [...priceKeys.all, "list"] as const,
  list: (params: Record<string, unknown>) => [...priceKeys.lists(), params] as const,
  details: () => [...priceKeys.all, "detail"] as const,
  detail: (id: number) => [...priceKeys.details(), id] as const,
  history: (id: number) => [...priceKeys.all, "history", id] as const,
  compare: () => [...priceKeys.all, "compare"] as const,
};

// Fetch price plans list
export function usePrices(params?: {
  page?: number;
  page_size?: number;
  company_id?: number;
  plan_type?: string;
  is_current?: boolean;
}) {
  return useQuery({
    queryKey: priceKeys.list(params || {}),
    queryFn: () => pricesApi.list(params),
  });
}

// Fetch single price plan
export function usePrice(id: number) {
  return useQuery({
    queryKey: priceKeys.detail(id),
    queryFn: () => pricesApi.get(id),
    enabled: !!id,
  });
}

// Fetch price history
export function usePriceHistory(id: number, limit?: number) {
  return useQuery({
    queryKey: priceKeys.history(id),
    queryFn: () => pricesApi.getHistory(id, limit),
    enabled: !!id,
  });
}

// Compare prices mutation
export function useComparePrices() {
  return useMutation({
    mutationFn: ({ planIds, usageKwh }: { planIds: number[]; usageKwh: number }) =>
      pricesApi.compare(planIds, usageKwh),
  });
}

// Compare prices query (for persistent comparison)
export function usePriceComparison(planIds: number[], usageKwh: number, enabled = true) {
  return useQuery({
    queryKey: [...priceKeys.compare(), planIds, usageKwh],
    queryFn: () => pricesApi.compare(planIds, usageKwh),
    enabled: enabled && planIds.length > 0 && usageKwh > 0,
  });
}
