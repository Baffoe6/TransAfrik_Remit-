import { apiClient } from "./client";

export interface PilotDashboard {
  pilot_mode_enabled: boolean;
  invite_only_registration: boolean;
  allowed_corridors: string[];
  daily_limit_zar: string | null;
  monthly_limit_zar: string | null;
}

export const pilotApi = {
  dashboard: () => apiClient.get<PilotDashboard>("/pilot/dashboard"),
};
