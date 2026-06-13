import { useColorScheme } from "react-native";
import { useThemeStore } from "../store/themeStore";
import { darkTheme, lightTheme, palette } from "./colors";
import { spacing, radius } from "./spacing";
import { typography } from "./typography";

export { palette, lightTheme, darkTheme, typography, spacing, radius };

export type AppTheme = typeof lightTheme;

export function useAppTheme(): AppTheme & { isDark: boolean } {
  const scheme = useColorScheme();
  const mode = useThemeStore((s) => s.mode);
  const isDark = mode === "dark" || (mode === "system" && scheme === "dark");
  const base = isDark ? darkTheme : lightTheme;
  return Object.assign({}, base, { isDark }) as AppTheme & { isDark: boolean };
}
