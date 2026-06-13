import { Text, View, ViewStyle } from "react-native";
import { useAppTheme } from "../theme";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

interface CardProps {
  children: React.ReactNode;
  style?: ViewStyle;
  elevated?: boolean;
  accent?: boolean;
}

export function Card({ children, style, elevated, accent }: CardProps) {
  const theme = useAppTheme();
  return (
    <View
      style={[
        {
          backgroundColor: accent ? theme.primaryDark : theme.surface,
          borderRadius: radius.lg,
          padding: spacing.lg,
          borderWidth: elevated ? 0 : 1,
          borderColor: theme.border,
          marginBottom: spacing.md,
          shadowColor: "#000",
          shadowOffset: { width: 0, height: elevated ? 4 : 0 },
          shadowOpacity: elevated ? 0.08 : 0,
          shadowRadius: elevated ? 12 : 0,
          elevation: elevated ? 3 : 0,
        },
        style,
      ]}
    >
      {children}
    </View>
  );
}

export function H1({ children, light }: { children: React.ReactNode; light?: boolean }) {
  const theme = useAppTheme();
  return <Text style={[typography.h1, { color: light ? "#fff" : theme.text }]}>{children}</Text>;
}

export function H2({ children, light }: { children: React.ReactNode; light?: boolean }) {
  const theme = useAppTheme();
  return <Text style={[typography.h2, { color: light ? "#fff" : theme.text }]}>{children}</Text>;
}

export function Body({ children, muted }: { children: React.ReactNode; muted?: boolean }) {
  const theme = useAppTheme();
  return <Text style={[typography.body, { color: muted ? theme.textSecondary : theme.text }]}>{children}</Text>;
}

export function Caption({ children }: { children: React.ReactNode }) {
  const theme = useAppTheme();
  return <Text style={[typography.caption, { color: theme.textSecondary }]}>{children}</Text>;
}
