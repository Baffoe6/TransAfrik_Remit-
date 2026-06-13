import { Text, View } from "react-native";
import { useAppTheme } from "../theme";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

type BadgeVariant = "success" | "warning" | "error" | "info" | "neutral" | "gold";

const variantMap: Record<BadgeVariant, { bg: string; fg: string }> = {
  success: { bg: "#DCFCE7", fg: "#166534" },
  warning: { bg: "#FEF3C7", fg: "#92400E" },
  error: { bg: "#FEE2E2", fg: "#991B1B" },
  info: { bg: "#DBEAFE", fg: "#1E40AF" },
  neutral: { bg: "#F3F4F6", fg: "#374151" },
  gold: { bg: "#FEF9C3", fg: "#854D0E" },
};

export function Badge({ label, variant = "neutral" }: { label: string; variant?: BadgeVariant }) {
  const colors = variantMap[variant];
  return (
    <View style={{ backgroundColor: colors.bg, paddingHorizontal: spacing.sm, paddingVertical: 4, borderRadius: radius.full, alignSelf: "flex-start" }}>
      <Text style={[typography.caption, { color: colors.fg, fontWeight: "600" }]}>{label}</Text>
    </View>
  );
}

export function StepIndicator({ step, total }: { step: number; total: number }) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", gap: spacing.sm, marginBottom: spacing.lg }}>
      {Array.from({ length: total }).map((_, i) => (
        <View
          key={i}
          style={{
            flex: 1,
            height: 4,
            borderRadius: 2,
            backgroundColor: i < step ? theme.primary : theme.border,
          }}
        />
      ))}
    </View>
  );
}

export function TrustRow({ items }: { items: string[] }) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: spacing.sm }}>
      {items.map((item) => (
        <View key={item} style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
          <Text style={{ color: theme.success }}>✓</Text>
          <Text style={[typography.caption, { color: theme.textSecondary }]}>{item}</Text>
        </View>
      ))}
    </View>
  );
}
