import { Text, View, ViewStyle } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useAppTheme, shadow, radius, spacing } from "../../theme";
import { typography } from "../../theme/typography";

type Variant = "default" | "elevated" | "hero" | "muted" | "accent" | "outline";

interface FintechCardProps {
  children: React.ReactNode;
  variant?: Variant;
  style?: ViewStyle;
  padding?: keyof typeof spacing;
  onPress?: () => void;
}

export function FintechCard({ children, variant = "default", style, padding = "lg" }: FintechCardProps) {
  const theme = useAppTheme();

  if (variant === "hero") {
    return (
      <LinearGradient
        colors={[...theme.heroGradient]}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={[
          { borderRadius: radius.xl, padding: spacing[padding], marginBottom: spacing.md, overflow: "hidden" },
          shadow("lg", theme.isDark),
          style,
        ]}
      >
        {children}
      </LinearGradient>
    );
  }

  const styles: Record<Variant, ViewStyle> = {
    default: { backgroundColor: theme.surface, borderWidth: 0 },
    elevated: { backgroundColor: theme.surface, ...shadow("md", theme.isDark) },
    hero: {},
    muted: { backgroundColor: theme.surfaceMuted, borderWidth: 0 },
    accent: { backgroundColor: theme.primaryMuted, borderWidth: 1, borderColor: theme.primary + "30" },
    outline: { backgroundColor: "transparent", borderWidth: 1.5, borderColor: theme.border },
  };

  return (
    <View
      style={[
        {
          borderRadius: radius.lg,
          padding: spacing[padding],
          marginBottom: spacing.md,
          ...styles[variant],
        },
        style,
      ]}
    >
      {children}
    </View>
  );
}

export function SectionHeader({ title, action, onAction }: { title: string; action?: string; onAction?: () => void }) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.sm, marginTop: spacing.md }}>
      <Text style={[typography.h3, { color: theme.text }]}>{title}</Text>
      {action && onAction ? (
        <Text onPress={onAction} style={[typography.bodySm, { color: theme.primary, fontWeight: "600" }]}>
          {action}
        </Text>
      ) : null}
    </View>
  );
}
