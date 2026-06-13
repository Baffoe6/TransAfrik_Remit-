import { apiClient } from "./client";
import type { Beneficiary } from "../types";

export const beneficiariesApi = {
  list: () => apiClient.get<Beneficiary[]>("/beneficiaries"),
  get: (id: number) => apiClient.get<Beneficiary>(`/beneficiaries/${id}`),
  create: (data: Record<string, unknown>) => apiClient.post<Beneficiary>("/beneficiaries", data),
  update: (id: number, data: Record<string, unknown>) =>
    apiClient.patch<Beneficiary>(`/beneficiaries/${id}`, data),
  remove: (id: number) => apiClient.delete(`/beneficiaries/${id}`),
};
