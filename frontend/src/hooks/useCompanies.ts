"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { companiesApi, statsApi } from "@/lib/api";
import { Company, CompanyCreate, CompanyUpdate } from "@/types";

// Query keys
export const companyKeys = {
  all: ["companies"] as const,
  lists: () => [...companyKeys.all, "list"] as const,
  list: (params: Record<string, unknown>) => [...companyKeys.lists(), params] as const,
  details: () => [...companyKeys.all, "detail"] as const,
  detail: (id: number) => [...companyKeys.details(), id] as const,
  stats: (id: number) => [...companyKeys.all, "stats", id] as const,
};

// Fetch companies list
export function useCompanies(params?: {
  page?: number;
  page_size?: number;
  is_active?: boolean;
}) {
  return useQuery({
    queryKey: companyKeys.list(params || {}),
    queryFn: () => companiesApi.list(params),
  });
}

// Fetch single company
export function useCompany(id: number) {
  return useQuery({
    queryKey: companyKeys.detail(id),
    queryFn: () => companiesApi.get(id),
    enabled: !!id,
  });
}

// Fetch company stats
export function useCompanyStats(id: number) {
  return useQuery({
    queryKey: companyKeys.stats(id),
    queryFn: () => statsApi.getCompanyStats(id),
    enabled: !!id,
  });
}

// Create company mutation
export function useCreateCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (company: CompanyCreate) => companiesApi.create(company),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}

// Update company mutation
export function useUpdateCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: CompanyUpdate }) =>
      companiesApi.update(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
      queryClient.invalidateQueries({ queryKey: companyKeys.detail(variables.id) });
    },
  });
}

// Delete company mutation
export function useDeleteCompany() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => companiesApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: companyKeys.lists() });
    },
  });
}
