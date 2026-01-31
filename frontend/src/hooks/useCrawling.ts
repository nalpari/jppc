"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { crawlingApi } from "@/lib/api";
import { ScheduleConfig } from "@/types";

// Query keys
export const crawlingKeys = {
  all: ["crawling"] as const,
  status: () => [...crawlingKeys.all, "status"] as const,
  schedule: () => [...crawlingKeys.all, "schedule"] as const,
  logs: () => [...crawlingKeys.all, "logs"] as const,
  logList: (params: Record<string, unknown>) => [...crawlingKeys.logs(), params] as const,
  logDetail: (id: number) => [...crawlingKeys.logs(), "detail", id] as const,
};

// Fetch crawling status
export function useCrawlingStatus(refetchInterval?: number) {
  return useQuery({
    queryKey: crawlingKeys.status(),
    queryFn: () => crawlingApi.getStatus(),
    refetchInterval: refetchInterval,
  });
}

// Fetch schedule config
export function useCrawlingSchedule() {
  return useQuery({
    queryKey: crawlingKeys.schedule(),
    queryFn: () => crawlingApi.getSchedule(),
  });
}

// Fetch crawl logs
export function useCrawlLogs(params?: {
  page?: number;
  page_size?: number;
  company_id?: number;
  status?: string;
}) {
  return useQuery({
    queryKey: crawlingKeys.logList(params || {}),
    queryFn: () => crawlingApi.getLogs(params),
  });
}

// Fetch single crawl log
export function useCrawlLog(id: number) {
  return useQuery({
    queryKey: crawlingKeys.logDetail(id),
    queryFn: () => crawlingApi.getLog(id),
    enabled: !!id,
  });
}

// Start crawling mutation
export function useStartCrawling() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ companyIds, force }: { companyIds?: number[]; force?: boolean }) =>
      crawlingApi.start(companyIds, force),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crawlingKeys.status() });
      queryClient.invalidateQueries({ queryKey: crawlingKeys.logs() });
    },
  });
}

// Stop crawling mutation
export function useStopCrawling() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => crawlingApi.stop(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crawlingKeys.status() });
    },
  });
}

// Update schedule mutation
export function useUpdateSchedule() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (config: ScheduleConfig) => crawlingApi.updateSchedule(config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: crawlingKeys.schedule() });
      queryClient.invalidateQueries({ queryKey: crawlingKeys.status() });
    },
  });
}
