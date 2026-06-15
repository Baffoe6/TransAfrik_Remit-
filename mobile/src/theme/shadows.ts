import { Platform, ViewStyle } from "react-native";

type ShadowLevel = "none" | "sm" | "md" | "lg" | "xl";

const ios = (y: number, opacity: number, radius: number): ViewStyle => ({
  shadowColor: "#0D3D24",
  shadowOffset: { width: 0, height: y },
  shadowOpacity: opacity,
  shadowRadius: radius,
});

export function shadow(level: ShadowLevel, isDark = false): ViewStyle {
  const color = isDark ? "#000" : "#0D3D24";
  const map: Record<ShadowLevel, ViewStyle> = {
    none: {},
    sm: Platform.select({
      ios: { ...ios(1, isDark ? 0.35 : 0.06, 4), shadowColor: color },
      android: { elevation: 2 },
      default: {},
    }) ?? {},
    md: Platform.select({
      ios: { ...ios(4, isDark ? 0.4 : 0.08, 12), shadowColor: color },
      android: { elevation: 4 },
      default: {},
    }) ?? {},
    lg: Platform.select({
      ios: { ...ios(8, isDark ? 0.45 : 0.12, 24), shadowColor: color },
      android: { elevation: 8 },
      default: {},
    }) ?? {},
    xl: Platform.select({
      ios: { ...ios(12, isDark ? 0.5 : 0.15, 32), shadowColor: color },
      android: { elevation: 12 },
      default: {},
    }) ?? {},
  };
  return map[level];
}
