import AsyncStorage from "@react-native-async-storage/async-storage";

const PREFIX = "cache:";

export const offlineCache = {
  async set<T>(key: string, data: T, ttlMs = 3600000) {
    await AsyncStorage.setItem(
      `${PREFIX}${key}`,
      JSON.stringify({ data, expires: Date.now() + ttlMs }),
    );
  },
  async get<T>(key: string): Promise<T | null> {
    const raw = await AsyncStorage.getItem(`${PREFIX}${key}`);
    if (!raw) return null;
    try {
      const parsed = JSON.parse(raw) as { data: T; expires: number };
      if (Date.now() > parsed.expires) {
        await AsyncStorage.removeItem(`${PREFIX}${key}`);
        return null;
      }
      return parsed.data;
    } catch {
      return null;
    }
  },
  async remove(key: string) {
    await AsyncStorage.removeItem(`${PREFIX}${key}`);
  },
};
