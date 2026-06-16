import { useQuery } from "@tanstack/react-query";
import { dashboardApi, profileApi } from "../api";
import { useAuthStore } from "../store/authStore";

export interface TransferEligibility {
  canTransfer: boolean;
  blockers: string[];
  kycStatus: string;
  phoneVerified: boolean;
  profileComplete: number;
}

export function useTransferEligibility(): TransferEligibility & { isLoading: boolean } {
  const user = useAuthStore((s) => s.user);

  const { data: summary, isLoading: sLoading } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => (await dashboardApi.summary()).data,
    enabled: !!user,
  });

  const { data: profile, isLoading: pLoading } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => (await profileApi.get()).data,
    enabled: !!user,
  });

  const blockers: string[] = [];
  const phoneVerified = summary?.mobile_identity?.verified ?? user?.phone_verified ?? false;
  const kycStatus = summary?.kyc?.status ?? profile?.kyc_status ?? "not_submitted";
  const kycApproved = kycStatus === "Approved" || kycStatus === "approved";
  const profileComplete = summary?.profile_completion?.percent ?? 0;

  if (!phoneVerified) blockers.push("Verify your mobile number");
  if (!kycApproved) blockers.push("Complete identity verification (KYC)");
  if (profileComplete < 50) blockers.push("Complete your profile details");

  return {
    canTransfer: blockers.length === 0,
    blockers,
    kycStatus,
    phoneVerified,
    profileComplete,
    isLoading: sLoading || pLoading,
  };
}
