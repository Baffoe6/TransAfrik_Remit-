import { Text, View } from "react-native";
import { useAppTheme, radius } from "../../theme";
import { typography } from "../../theme/typography";

type StatusVariant = "success" | "warning" | "error" | "info" | "neutral" | "gold";

interface StatusPillProps {
  label: string;
  variant?: StatusVariant;
  size?: "sm" | "md";
}

export function StatusPill({ label, variant = "neutral", size = "sm" }: StatusPillProps) {
  const theme = useAppTheme();
  const map: Record<StatusVariant, { bg: string; fg: string }> = {
    success: { bg: theme.successBg, fg: theme.success },
    warning: { bg: theme.warningBg, fg: theme.warning },
    error: { bg: theme.errorBg, fg: theme.error },
    info: { bg: theme.infoBg, fg: theme.info },
    neutral: { bg: theme.surfaceMuted, fg: theme.textSecondary },
    gold: { bg: theme.accentMuted, fg: theme.accent },
  };
  const c = map[variant];
  return (
    <View style={{ backgroundColor: c.bg, paddingHorizontal: size === "sm" ? 10 : 14, paddingVertical: size === "sm" ? 4 : 6, borderRadius: radius.full }}>
      <Text style={[size === "sm" ? typography.caption : typography.bodySm, { color: c.fg, fontWeight: "600" }]}>{label}</Text>
    </View>
  );
}

export function TrustBadge({ items }: { items: string[] }) {
  return (
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 12 }}>
      {items.map((item) => (
        <View
          key={item}
          style={{
            flexDirection: "row",
            alignItems: "center",
            backgroundColor: "rgba(255,255,255,0.12)",
            paddingHorizontal: 10,
            paddingVertical: 6,
            borderRadius: radius.full,
          }}
        >
          <Text style={{ fontSize: 12, color: "rgba(255,255,255,0.95)", fontWeight: "500" }}>✓ {item}</Text>
        </View>
      ))}
    </View>
  );
}
