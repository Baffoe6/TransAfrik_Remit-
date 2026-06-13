import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";

const KEY = "onboarding_complete";

interface OnboardingState {
  complete: boolean | null;
  load: () => Promise<void>;
  markComplete: () => Promise<void>;
}

export const useOnboardingStore = create<OnboardingState>((set) => ({
  complete: null,
  load: async () => {
    const v = await AsyncStorage.getItem(KEY);
    set({ complete: v === "1" });
  },
  markComplete: async () => {
    await AsyncStorage.setItem(KEY, "1");
    set({ complete: true });
  },
}));
