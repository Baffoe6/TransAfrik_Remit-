import { useEffect, useRef } from "react";
import { ActivityIndicator, Animated, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useAppTheme, radius, spacing } from "../theme";
import { typography } from "../theme/typography";
import { Button } from "./Button";
import { FintechCard } from "./fintech/FintechCard";

export function Skeleton({ height = 16, width = "100%" as `${number}%` | number, style, rounded }: { height?: number; width?: number | `${number}%`; style?: object; rounded?: boolean }) {
  const theme = useAppTheme();
  const opacity = useRef(new Animated.Value(0.4)).current;

  useEffect(() => {
    const anim = Animated.loop(
      Animated.sequence([
        Animated.timing(opacity, { toValue: 1, duration: 700, useNativeDriver: true }),
        Animated.timing(opacity, { toValue: 0.4, duration: 700, useNativeDriver: true }),
      ]),
    );
    anim.start();
    return () => anim.stop();
  }, [opacity]);

  return (
    <Animated.View
      style={[
        { height, width, backgroundColor: theme.border, borderRadius: rounded ? radius.lg : radius.sm, marginBottom: spacing.sm, opacity },
        style,
      ]}
    />
  );
}

export function SkeletonCard() {
  return (
    <FintechCard variant="elevated">
      <Skeleton height={14} width="40%" />
      <Skeleton height={32} width="70%" />
      <Skeleton height={12} width="55%" />
    </FintechCard>
  );
}

export function SkeletonList({ count = 4 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <View key={i} style={{ flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.md }}>
          <Skeleton height={44} width={44} rounded />
          <View style={{ flex: 1 }}>
            <Skeleton height={14} width="60%" />
            <Skeleton height={12} width="40%" />
          </View>
        </View>
      ))}
    </>
  );
}

export function LoadingState({ message = "Loading..." }: { message?: string }) {
  const theme = useAppTheme();
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", padding: spacing.xxl, backgroundColor: theme.bg }}>
      <View style={{ width: 64, height: 64, borderRadius: 32, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center", marginBottom: spacing.lg }}>
        <ActivityIndicator size="large" color={theme.primary} />
      </View>
      <Text style={[typography.body, { color: theme.textSecondary }]}>{message}</Text>
    </View>
  );
}

const EMPTY_ICONS: Record<string, keyof typeof Ionicons.glyphMap> = {
  transfers: "swap-horizontal-outline",
  beneficiaries: "people-outline",
  default: "folder-open-outline",
};

export function EmptyState({
  title,
  message,
  actionLabel,
  onAction,
  icon = "default",
}: {
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: keyof typeof EMPTY_ICONS | string;
}) {
  const theme = useAppTheme();
  const iconName = EMPTY_ICONS[icon] ?? EMPTY_ICONS.default;
  return (
    <View style={{ alignItems: "center", padding: spacing.xxl, paddingTop: spacing.xxxl }}>
      <View style={{ width: 80, height: 80, borderRadius: 40, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center", marginBottom: spacing.lg }}>
        <Ionicons name={iconName} size={36} color={theme.primary} />
      </View>
      <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.sm, textAlign: "center" }]}>{title}</Text>
      <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center", marginBottom: spacing.xl, maxWidth: 280 }]}>{message}</Text>
      {actionLabel && onAction ? <Button title={actionLabel} onPress={onAction} variant="primary" /> : null}
    </View>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const theme = useAppTheme();
  return (
    <View style={{ alignItems: "center", padding: spacing.xxl }}>
      <View style={{ width: 80, height: 80, borderRadius: 40, backgroundColor: theme.errorBg, alignItems: "center", justifyContent: "center", marginBottom: spacing.lg }}>
        <Ionicons name="alert-circle-outline" size={40} color={theme.error} />
      </View>
      <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.sm }]}>Something went wrong</Text>
      <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center", marginBottom: spacing.xl, maxWidth: 280 }]}>{message}</Text>
      {onRetry ? <Button title="Try again" onPress={onRetry} variant="outline" /> : null}
    </View>
  );
}

export function OfflineBanner() {
  const theme = useAppTheme();
  return (
    <View style={{ backgroundColor: theme.warning, paddingVertical: spacing.sm, paddingHorizontal: spacing.lg, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8 }}>
      <Ionicons name="cloud-offline-outline" size={16} color="#fff" />
      <Text style={[typography.caption, { color: "#fff", fontWeight: "600" }]}>Offline — showing saved data</Text>
    </View>
  );
}
