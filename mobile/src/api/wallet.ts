import { apiClient } from "./client";
import type { ReferralDashboard, WalletProfile } from "../types";

export const walletApi = {
  profile: () => apiClient.get<WalletProfile>("/wallet/profile"),
};

export const referralApi = {
  dashboard: () => apiClient.get<ReferralDashboard>("/referrals/dashboard"),
};
