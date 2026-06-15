import { Text, View } from "react-native";
import { useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { spacing } from "../../theme/spacing";

interface AmountDisplayProps {
  label?: string;
  amount: string;
  sublabel?: string;
  size?: "lg" | "sm";
  light?: boolean;
}

export function AmountDisplay({ label, amount, sublabel, size = "lg", light }: AmountDisplayProps) {
  const theme = useAppTheme();
  const color = light ? "#fff" : theme.text;
  const muted = light ? "rgba(255,255,255,0.75)" : theme.textSecondary;

  return (
    <View style={{ marginVertical: spacing.xs }}>
      {label ? <Text style={[typography.caption, { color: muted, marginBottom: 4 }]}>{label}</Text> : null}
      <Text style={[size === "lg" ? typography.amount : typography.amountSm, { color }]}>{amount}</Text>
      {sublabel ? <Text style={[typography.bodySm, { color: muted, marginTop: 4 }]}>{sublabel}</Text> : null}
    </View>
  );
}
