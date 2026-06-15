import { View, ViewStyle } from "react-native";
import { useAppTheme, radius, shadow, spacing } from "../../theme";

interface GlassCardProps {
  children: React.ReactNode;
  style?: ViewStyle;
}

/** Translucent card with glass-like border — no native blur dependency */
export function GlassCard({ children, style }: GlassCardProps) {
  const theme = useAppTheme();
  return (
    <View
      style={[
        {
          backgroundColor: theme.isDark ? "rgba(18,32,24,0.88)" : "rgba(255,255,255,0.94)",
          borderRadius: radius.xl,
          padding: spacing.lg,
          marginBottom: spacing.md,
          borderWidth: 1,
          borderColor: theme.isDark ? "rgba(255,255,255,0.08)" : "rgba(27,94,59,0.12)",
          ...shadow("md", theme.isDark),
        },
        style,
      ]}
    >
      {children}
    </View>
  );
}
