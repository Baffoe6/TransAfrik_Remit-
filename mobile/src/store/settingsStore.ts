import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";

const FAV_KEY = "favorite_beneficiaries";
const BIO_KEY = "biometric_enabled";
const PIN_KEY = "pin_enabled";

interface SettingsState {
  favoriteIds: number[];
  biometricEnabled: boolean;
  pinEnabled: boolean;
  load: () => Promise<void>;
  toggleFavorite: (id: number) => Promise<void>;
  setBiometric: (v: boolean) => Promise<void>;
  setPinEnabled: (v: boolean) => Promise<void>;
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  favoriteIds: [],
  biometricEnabled: false,
  pinEnabled: false,
  load: async () => {
    const [fav, bio, pin] = await Promise.all([
      AsyncStorage.getItem(FAV_KEY),
      AsyncStorage.getItem(BIO_KEY),
      AsyncStorage.getItem(PIN_KEY),
    ]);
    set({
      favoriteIds: fav ? JSON.parse(fav) : [],
      biometricEnabled: bio === "1",
      pinEnabled: pin === "1",
    });
  },
  toggleFavorite: async (id) => {
    const current = get().favoriteIds;
    const next = current.includes(id) ? current.filter((x) => x !== id) : [...current, id];
    await AsyncStorage.setItem(FAV_KEY, JSON.stringify(next));
    set({ favoriteIds: next });
  },
  setBiometric: async (v) => {
    await AsyncStorage.setItem(BIO_KEY, v ? "1" : "0");
    set({ biometricEnabled: v });
  },
  setPinEnabled: async (v) => {
    await AsyncStorage.setItem(PIN_KEY, v ? "1" : "0");
    set({ pinEnabled: v });
  },
}));
