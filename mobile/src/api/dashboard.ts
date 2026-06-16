import { apiClient, getApiBaseUrl } from "./client";
import type { DashboardSummary, KycDocument, Profile } from "../types";
import { secureStorage } from "../services/secureStorage";

export const dashboardApi = {
  summary: () => apiClient.get<DashboardSummary>("/dashboard/summary"),
};

export const profileApi = {
  get: () => apiClient.get<Profile>("/profile"),
  update: (data: Partial<Profile>) => apiClient.patch<Profile>("/profile", data),
};

export const kycApi = {
  documents: () => apiClient.get<KycDocument[]>("/kyc/documents"),
  upload: async (formData: FormData) => {
    const token = await secureStorage.getAccessToken();
    const res = await fetch(`${getApiBaseUrl()}/api/v1/kyc/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : {},
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const detail = (err as { detail?: string }).detail;
      throw new Error(detail || "Upload failed");
    }
    const data = (await res.json()) as KycDocument;
    return { data };
  },
};
