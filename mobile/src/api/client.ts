import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import Constants from "expo-constants";
import { secureStorage } from "../services/secureStorage";

const API_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  Constants.expoConfig?.extra?.apiUrl ||
  "https://api.ipaygo.co.za";

export const apiClient = axios.create({
  baseURL: `${API_URL}/api/v1`,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const token = await secureStorage.getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshing: Promise<string | null> | null = null;

async function refreshToken(): Promise<string | null> {
  const refresh = await secureStorage.getRefreshToken();
  if (!refresh) return null;
  try {
    const { data } = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
      refresh_token: refresh,
    });
    await secureStorage.setTokens(data.access_token, data.refresh_token);
    return data.access_token;
  } catch {
    await secureStorage.clearTokens();
    return null;
  }
}

apiClient.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && original && !original._retry) {
      original._retry = true;
      refreshing = refreshing ?? refreshToken();
      const token = await refreshing;
      refreshing = null;
      if (token && original.headers) {
        original.headers.Authorization = `Bearer ${token}`;
        return apiClient(original);
      }
    }
    const detail = (error.response?.data as { detail?: string })?.detail;
    throw new Error(typeof detail === "string" ? detail : error.message);
  },
);

export function getApiBaseUrl() {
  return API_URL;
}
