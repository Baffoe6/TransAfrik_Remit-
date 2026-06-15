import { ActivityIndicator, Text, TouchableOpacity, View, ViewStyle } from "react-native";
import { useAppTheme } from "../theme";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

type Variant = "primary" | "secondary" | "outline" | "ghost" | "gold" | "danger";

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: Variant;
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  style?: ViewStyle;
  size?: "md" | "lg";
}

export function Button({ title, onPress, variant = "primary", loading, disabled, icon, style, size = "lg" }: ButtonProps) {
  const theme = useAppTheme();
  const py = size === "lg" ? 16 : 12;

  const styles: Record<Variant, ViewStyle> = {
    primary: { backgroundColor: theme.primary, borderWidth: 0 },
    secondary: { backgroundColor: theme.surface, borderWidth: 1, borderColor: theme.border },
    outline: { backgroundColor: "transparent", borderWidth: 1.5, borderColor: theme.primary },
    ghost: { backgroundColor: "transparent", borderWidth: 0 },
    gold: { backgroundColor: theme.accent, borderWidth: 0 },
    danger: { backgroundColor: theme.error, borderWidth: 0 },
  };

  const textColors: Record<Variant, string> = {
    primary: "#fff",
    secondary: theme.text,
    outline: theme.primary,
    ghost: theme.primary,
    gold: theme.charcoal900,
    danger: "#fff",
  };

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.85}
      style={[
        {
          ...styles[variant],
          borderRadius: radius.lg,
          paddingVertical: py,
          paddingHorizontal: spacing.xl,
          flexDirection: "row",
          alignItems: "center",
          justifyContent: "center",
          gap: spacing.sm,
          opacity: disabled || loading ? 0.55 : 1,
        },
        style,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={textColors[variant]} />
      ) : (
        <>
          {icon}
          <Text style={[typography.button, { color: textColors[variant] }]}>{title}</Text>
        </>
      )}
    </TouchableOpacity>
  );
}
