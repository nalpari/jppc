"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { alertsApi } from "@/lib/api";

// Query keys
export const alertKeys = {
  all: ["alerts"] as const,
  list: () => [...alertKeys.all, "list"] as const,
  detail: (type: string) => [...alertKeys.all, "detail", type] as const,
};

// Fetch all alert settings
export function useAlerts() {
  return useQuery({
    queryKey: alertKeys.list(),
    queryFn: () => alertsApi.list(),
  });
}

// Fetch single alert setting
export function useAlert(alertType: string) {
  return useQuery({
    queryKey: alertKeys.detail(alertType),
    queryFn: () => alertsApi.get(alertType),
    enabled: !!alertType,
  });
}

// Update alert enabled status
export function useUpdateAlert() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ alertType, isEnabled }: { alertType: string; isEnabled: boolean }) =>
      alertsApi.update(alertType, isEnabled),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.list() });
      queryClient.invalidateQueries({ queryKey: alertKeys.detail(variables.alertType) });
    },
  });
}

// Add recipient
export function useAddRecipient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      alertType,
      email,
      name,
    }: {
      alertType: string;
      email: string;
      name?: string;
    }) => alertsApi.addRecipient(alertType, email, name),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.list() });
      queryClient.invalidateQueries({ queryKey: alertKeys.detail(variables.alertType) });
    },
  });
}

// Remove recipient
export function useRemoveRecipient() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      alertType,
      recipientId,
    }: {
      alertType: string;
      recipientId: number;
    }) => alertsApi.removeRecipient(alertType, recipientId),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: alertKeys.list() });
      queryClient.invalidateQueries({ queryKey: alertKeys.detail(variables.alertType) });
    },
  });
}
