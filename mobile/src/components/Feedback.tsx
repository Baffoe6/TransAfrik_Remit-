import { ActivityIndicator, Text, View } from "react-native";
import { useAppTheme } from "../theme";
import { spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { Button } from "./Button";

export function Skeleton({ height = 16, width = "100%" as `${number}%` | number, style }: { height?: number; width?: number | `${number}%`; style?: object }) {
  const theme = useAppTheme();
  return (
    <View
      style={[
        { height, width, backgroundColor: theme.border, borderRadius: 8, marginBottom: spacing.sm },
        style,
      ]}
    />
  );
}

export function LoadingState({ message = "Loading..." }: { message?: string }) {
  const theme = useAppTheme();
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: spacing.xl }}>
      <ActivityIndicator size="large" color={theme.primary} />
      <Text style={[typography.body, { color: theme.textSecondary, marginTop: spacing.md }]}>{message}</Text>
    </View>
  );
}

export function EmptyState({ title, message, actionLabel, onAction }: { title: string; message: string; actionLabel?: string; onAction?: () => void }) {
  const theme = useAppTheme();
  return (
    <View style={{ alignItems: "center", padding: spacing.xxl }}>
      <Text style={{ fontSize: 48, marginBottom: spacing.md }}>📭</Text>
      <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.sm, textAlign: "center" }]}>{title}</Text>
      <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center", marginBottom: spacing.lg }]}>{message}</Text>
      {actionLabel && onAction ? <Button title={actionLabel} onPress={onAction} variant="outline" /> : null}
    </View>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const theme = useAppTheme();
  return (
    <View style={{ alignItems: "center", padding: spacing.xxl }}>
      <Text style={{ fontSize: 48, marginBottom: spacing.md }}>⚠️</Text>
      <Text style={[typography.h3, { color: theme.error, marginBottom: spacing.sm }]}>Something went wrong</Text>
      <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center", marginBottom: spacing.lg }]}>{message}</Text>
      {onRetry ? <Button title="Try Again" onPress={onRetry} variant="outline" /> : null}
    </View>
  );
}

export function OfflineBanner() {
  const theme = useAppTheme();
  return (
    <View style={{ backgroundColor: theme.warning, padding: spacing.sm, alignItems: "center" }}>
      <Text style={[typography.caption, { color: "#fff", fontWeight: "600" }]}>You're offline — showing cached data</Text>
    </View>
  );
}
