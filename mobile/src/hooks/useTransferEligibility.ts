import { useVerificationStatus } from "./useVerificationStatus";

export interface TransferEligibility {
  canTransfer: boolean;
  blockers: string[];
  kycStatus: string;
  phoneVerified: boolean;
  profileComplete: number;
}

export function useTransferEligibility(): TransferEligibility & { isLoading: boolean } {
  const { kycApproved, kycDisplay, phoneVerified, identityVerified, summary, isLoading } = useVerificationStatus();

  const blockers: string[] = [];
  const profileComplete = summary?.profile_completion?.percent ?? 0;

  if (!kycApproved) blockers.push("Complete identity verification (KYC)");
  else if (!identityVerified) blockers.push("Verify your mobile number");

  return {
    canTransfer: blockers.length === 0,
    blockers,
    kycStatus: kycDisplay,
    phoneVerified,
    profileComplete,
    isLoading,
  };
}
