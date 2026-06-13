import { create } from "zustand";

export type ThemeMode = "light" | "dark" | "system";

interface ThemeState {
  mode: ThemeMode;
  setMode: (mode: ThemeMode) => void;
}

export const useThemeStore = create<ThemeState>((set) => ({
  mode: "system",
  setMode: (mode) => set({ mode }),
}));

export const colors = {
  light: {
    bg: "#F8FAF9",
    card: "#FFFFFF",
    text: "#1a1a1a",
    textMuted: "#6b7280",
    primary: "#1B5E3B",
    accent: "#C9A227",
    border: "#E5E7EB",
    danger: "#DC2626",
    success: "#16A34A",
  },
  dark: {
    bg: "#0f1f17",
    card: "#1a2e24",
    text: "#f3f4f6",
    textMuted: "#9ca3af",
    primary: "#2d8f5c",
    accent: "#C9A227",
    border: "#374151",
    danger: "#F87171",
    success: "#4ADE80",
  },
};

export function useThemeColors(isDark: boolean) {
  return isDark ? colors.dark : colors.light;
}
