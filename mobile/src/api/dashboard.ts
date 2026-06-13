import { apiClient } from "./client";
import type { DashboardSummary, KycDocument, Profile } from "../types";

export const dashboardApi = {
  summary: () => apiClient.get<DashboardSummary>("/dashboard/summary"),
};

export const profileApi = {
  get: () => apiClient.get<Profile>("/profile"),
  update: (data: Partial<Profile>) => apiClient.patch<Profile>("/profile", data),
};

export const kycApi = {
  documents: () => apiClient.get<KycDocument[]>("/kyc/documents"),
  upload: (formData: FormData) =>
    apiClient.post<KycDocument>("/kyc/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
};
