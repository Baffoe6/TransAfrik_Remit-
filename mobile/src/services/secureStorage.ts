import * as SecureStore from "expo-secure-store";

const ACCESS_KEY = "transafrik_access_token";
const REFRESH_KEY = "transafrik_refresh_token";
const DEVICE_KEY = "transafrik_device_id";

export const secureStorage = {
  async setTokens(access: string, refresh: string) {
    await SecureStore.setItemAsync(ACCESS_KEY, access);
    await SecureStore.setItemAsync(REFRESH_KEY, refresh);
  },
  async getAccessToken() {
    return SecureStore.getItemAsync(ACCESS_KEY);
  },
  async getRefreshToken() {
    return SecureStore.getItemAsync(REFRESH_KEY);
  },
  async clearTokens() {
    await SecureStore.deleteItemAsync(ACCESS_KEY);
    await SecureStore.deleteItemAsync(REFRESH_KEY);
  },
  async getOrCreateDeviceId() {
    let id = await SecureStore.getItemAsync(DEVICE_KEY);
    if (!id) {
      id = `mobile-${Date.now()}-${Math.random().toString(36).slice(2)}`;
      await SecureStore.setItemAsync(DEVICE_KEY, id);
    }
    return id;
  },
};
