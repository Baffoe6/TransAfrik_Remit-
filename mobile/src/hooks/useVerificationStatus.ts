import { useEffect } from "react";
import { AppState } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { dashboardApi, profileApi } from "../api";
import { useAuthStore } from "../store/authStore";

function isKycApproved(raw?: string | null) {
  return raw === "approved";
}

/** Shared verification state — refetches when app returns to foreground. */
export function useVerificationStatus() {
  const user = useAuthStore((s) => s.user);
  const refreshUser = useAuthStore((s) => s.refreshUser);
  const queryClient = useQueryClient();

  const { data: profile, isLoading: profileLoading, refetch: refetchProfile } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => (await profileApi.get()).data,
    enabled: !!user,
    staleTime: 15_000,
  });

  const { data: summary, isLoading: summaryLoading, refetch: refetchSummary } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await dashboardApi.summary()).data,
    enabled: !!user,
    staleTime: 15_000,
  });

  const sync = async () => {
    await refreshUser();
    await Promise.all([refetchProfile(), refetchSummary()]);
    await queryClient.invalidateQueries({ queryKey: ["profile"] });
    await queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  useEffect(() => {
    if (!user) return;
    const sub = AppState.addEventListener("change", (state) => {
      if (state === "active") void sync();
    });
    return () => sub.remove();
  }, [user?.id]);

  const kycRaw = summary?.kyc?.raw_status ?? profile?.kyc_status ?? "not_submitted";
  const kycDisplay = summary?.kyc?.status ?? profile?.kyc_status ?? "Draft";
  const kycApproved = isKycApproved(kycRaw);
  const phoneVerified = summary?.mobile_identity?.verified ?? user?.phone_verified ?? false;

  return {
    kycRaw,
    kycDisplay,
    kycApproved,
    phoneVerified,
    identityVerified: kycApproved || phoneVerified,
    profile,
    summary,
    isLoading: profileLoading || summaryLoading,
    sync,
  };
}
