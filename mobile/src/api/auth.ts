import { apiClient } from "./client";

import type { TokenResponse, User } from "../types";

import { getDevicePayload } from "../services/device";



export interface RegisterPayload {

  mobile_number: string;

  pin: string;

  first_name: string;

  last_name: string;

  email?: string;

  accept_popia: boolean;

  accept_terms: boolean;

}



export interface TrustedDevice {

  id: number;

  device_name: string;

  device_fingerprint?: string;

  trusted: boolean;

  last_seen_at: string;

  ip_address?: string;

  is_current?: boolean;

}



interface DevicesResponse {

  devices: Array<{

    id: number;

    device_label?: string;

    device_name?: string;

    is_trusted?: boolean;

    trusted?: boolean;

    last_seen_at: string;

    ip_address?: string;

    is_current?: boolean;

  }>;

}



function mapDevices(data: DevicesResponse | TrustedDevice[]): TrustedDevice[] {

  const list = Array.isArray(data) ? data : data.devices ?? [];

  return list.map((d) => {

    const raw = d as DevicesResponse["devices"][number];

    return {

      id: raw.id,

      device_name: raw.device_label ?? raw.device_name ?? "Unknown device",

      trusted: raw.is_trusted ?? raw.trusted ?? false,

      last_seen_at: raw.last_seen_at,

      ip_address: raw.ip_address,

      is_current: raw.is_current,

    };

  });

}



export const authApi = {

  login: (identifier: string, password: string, mfaCode?: string) =>

    apiClient.post<TokenResponse>("/auth/login", {

      identifier,

      password,

      mfa_code: mfaCode,

      ...getDevicePayload(),

    }),



  loginPin: (mobile_number: string, pin: string) =>

    apiClient.post<TokenResponse>("/auth/login/pin", {

      mobile_number,

      pin,

      ...getDevicePayload(),

    }),



  register: (data: RegisterPayload) => apiClient.post<TokenResponse>("/auth/register", data),



  loginOtp: (mobile_number: string, code: string) =>

    apiClient.post<TokenResponse>("/auth/login/otp", {

      mobile_number,

      code,

      trust_device: true,

      ...getDevicePayload(),

    }),



  sendOtp: (mobile_number: string, channel: "sms" | "whatsapp", purpose: string) =>

    apiClient.post("/auth/otp/send", { mobile_number, channel, purpose }),



  stepUp: (mobile_number: string, code: string) =>

    apiClient.post<TokenResponse>("/auth/login/step-up", {

      mobile_number,

      code,

      trust_device: true,

      ...getDevicePayload(),

    }),



  forgotPin: (mobile_number: string) => apiClient.post("/auth/pin/forgot", { mobile_number }),



  resetPin: (mobile_number: string, code: string, new_pin: string) =>

    apiClient.post("/auth/pin/reset", { mobile_number, code, new_pin }),



  /** @deprecated Legacy password reset for email accounts */

  forgotPassword: (mobile_number: string) => apiClient.post("/auth/password/forgot", { mobile_number }),



  /** @deprecated Legacy password reset for email accounts */

  resetPassword: (mobile_number: string, code: string, new_password: string) =>

    apiClient.post("/auth/password/reset", { mobile_number, code, new_password }),



  setPin: (pin: string, current_password?: string) =>

    apiClient.post("/auth/pin/set", { pin, current_password }),



  me: () => apiClient.get<User>("/auth/me"),



  logout: (refresh_token: string) => apiClient.post("/auth/logout", { refresh_token }),



  verifyPhone: (code: string, channel: "sms" | "whatsapp" = "sms") =>

    apiClient.post("/auth/otp/verify-phone", { code, channel }),



  devices: async () => {

    const { data } = await apiClient.get<DevicesResponse | TrustedDevice[]>("/auth/devices");

    return { data: mapDevices(data) };

  },



  trustDevice: (device_id: number, trusted: boolean) =>

    apiClient.post("/auth/devices/trust", { device_id, trusted }),

};

