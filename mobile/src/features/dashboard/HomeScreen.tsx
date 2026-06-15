import { RefreshControl, ScrollView, Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useState } from "react";
import { Ionicons } from "@expo/vector-icons";
import {
  AmountDisplay,
  Button,
  FintechCard,
  HeroHeader,
  OfflineBanner,
  QuickActionGrid,
  SectionHeader,
  SkeletonCard,
  StatusPill,
  TrustBadge,
  ListItem,
  ListDivider,
} from "../../components";
import { dashboardApi, beneficiariesApi } from "../../api";
import { useAuthStore } from "../../store/authStore";
import { offlineCache } from "../../services/offlineCache";
import { formatZAR, greetingName } from "../../utils/format";
import { spacing } from "../../theme";
import { useAppTheme } from "../../theme";
import type { DashboardSummary } from "../../types";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";

export default function HomeScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const user = useAuthStore((s) => s.user);
  const [offline, setOffline] = useState(false);

  const { data: summary, isLoading, refetch, isFetching } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async (): Promise<DashboardSummary | null> => {
      try {
        const { data } = await dashboardApi.summary();
        await offlineCache.set("dashboard", data);
        setOffline(false);
        return data;
      } catch {
        setOffline(true);
        return offlineCache.get<DashboardSummary>("dashboard");
      }
    },
  });

  const { data: beneficiaries = [] } = useQuery({
    queryKey: ["beneficiaries"],
    queryFn: async () => {
      try {
        const { data } = await beneficiariesApi.list();
        await offlineCache.set("beneficiaries", data);
        return data;
      } catch {
        return (await offlineCache.get<Awaited<ReturnType<typeof beneficiariesApi.list>>["data"]>("beneficiaries")) ?? [];
      }
    },
  });

  const kycStatus = summary?.kyc.status ?? "Draft";
  const kycVariant = kycStatus === "Approved" ? "success" : kycStatus === "Rejected" ? "error" : "warning";

  const quickActions = [
    { id: "send", label: "Send", icon: "arrow-up-circle" as const, onPress: () => navigation.navigate("SendFlow"), accent: true },
    { id: "beneficiaries", label: "Recipients", icon: "people" as const, onPress: () => navigation.navigate("Tabs", { screen: "Beneficiaries" } as never) },
    { id: "kyc", label: "Verify", icon: "shield-checkmark" as const, onPress: () => navigation.navigate("Kyc") },
    { id: "activity", label: "Activity", icon: "time" as const, onPress: () => navigation.navigate("Tabs", { screen: "Activity" } as never) },
    { id: "support", label: "Help", icon: "chatbubble-ellipses" as const, onPress: () => navigation.navigate("Support") },
  ];

  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      {offline && <OfflineBanner />}
      <ScrollView
        refreshControl={<RefreshControl refreshing={isFetching} onRefresh={refetch} tintColor={theme.primary} />}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={{ paddingBottom: spacing.xxxl }}
      >
        <HeroHeader
          greeting={greetingName(user?.first_name)}
          title="TransAfrik"
          subtitle="Send money to Ghana — fast & secure"
          rightAction={{ icon: "notifications-outline", onPress: () => navigation.navigate("Notifications") }}
        >
          <TrustBadge items={["Licensed partners", "Encrypted", "FICA compliant"]} />
        </HeroHeader>

        <View style={{ paddingHorizontal: spacing.lg, marginTop: -spacing.lg }}>
          <FintechCard variant="elevated" style={{ marginTop: 0 }}>
            <QuickActionGrid actions={quickActions} />
          </FintechCard>

          {isLoading ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : (
            <>
              <FintechCard variant={kycStatus === "Approved" ? "muted" : "accent"}>
                <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                  <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
                    <Ionicons name="shield-checkmark" size={22} color={theme.primary} />
                    <Text style={{ fontWeight: "600", fontSize: 16, color: theme.text }}>Identity verification</Text>
                  </View>
                  <StatusPill label={kycStatus} variant={kycVariant as "success"} />
                </View>
                <Text style={{ color: theme.textSecondary, fontSize: 13, marginTop: 8 }}>
                  {summary?.profile_completion.percent ?? 0}% complete · {summary?.kyc.documents_uploaded ?? 0} documents
                </Text>
                {kycStatus !== "Approved" && (
                  <Button title="Complete verification" onPress={() => navigation.navigate("Kyc")} variant="primary" style={{ marginTop: spacing.md }} />
                )}
              </FintechCard>

              <FintechCard variant="elevated">
                <Text style={{ color: theme.textSecondary, fontSize: 12, fontWeight: "600", letterSpacing: 0.5, textTransform: "uppercase" }}>ZA → Ghana</Text>
                <AmountDisplay label="Live corridor rate" amount="1 ZAR ≈ live" sublabel="Fees from R15 · Arrives in minutes" size="sm" />
              </FintechCard>

              <SectionHeader title="Recent transfers" action="See all" onAction={() => navigation.navigate("Tabs", { screen: "Activity" } as never)} />
              <FintechCard variant="default" padding="sm">
                {(summary?.transfers.recent ?? []).slice(0, 3).map((t, i) => (
                  <View key={t.id}>
                    {i > 0 && <ListDivider />}
                    <ListItem
                      title={t.reference}
                      subtitle={formatZAR(t.send_amount_zar)}
                      meta={TRANSFER_STATUS_LABELS[t.status] ?? t.status}
                      icon="swap-horizontal"
                      showChevron
                      onPress={() => navigation.navigate("TransferTracking", { id: t.id })}
                      right={<StatusPill label={TRANSFER_STATUS_LABELS[t.status] ?? t.status} variant={t.status === "completed" ? "success" : "info"} />}
                      style={{ backgroundColor: "transparent", paddingHorizontal: spacing.sm }}
                    />
                  </View>
                ))}
                {!summary?.transfers.recent?.length && (
                  <View style={{ padding: spacing.lg, alignItems: "center" }}>
                    <Text style={{ color: theme.textSecondary, marginBottom: spacing.md }}>No transfers yet</Text>
                    <Button title="Send your first transfer" onPress={() => navigation.navigate("SendFlow")} variant="gold" />
                  </View>
                )}
              </FintechCard>

              <SectionHeader title="Saved recipients" action="View all" onAction={() => navigation.navigate("Tabs", { screen: "Beneficiaries" } as never)} />
              <FintechCard variant="default" padding="sm">
                {beneficiaries.slice(0, 3).map((b, i) => (
                  <View key={b.id}>
                    {i > 0 && <ListDivider />}
                    <ListItem
                      title={b.full_name}
                      subtitle={b.country}
                      avatarName={b.full_name}
                      onPress={() => navigation.navigate("BeneficiaryForm", { id: b.id })}
                      style={{ backgroundColor: "transparent", paddingHorizontal: spacing.sm }}
                    />
                  </View>
                ))}
                {!beneficiaries.length && (
                  <View style={{ padding: spacing.lg }}>
                    <Button title="Add recipient" onPress={() => navigation.navigate("BeneficiaryForm", {})} variant="outline" />
                  </View>
                )}
              </FintechCard>

              <FintechCard variant="muted">
                <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
                  <View style={{ width: 48, height: 48, borderRadius: 24, backgroundColor: theme.accentMuted, alignItems: "center", justifyContent: "center" }}>
                    <Ionicons name="gift" size={24} color={theme.accent} />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={{ fontWeight: "700", fontSize: 16, color: theme.text }}>Refer & earn</Text>
                    <Text style={{ color: theme.textSecondary, fontSize: 13 }}>{summary?.referral_program.referrals_made ?? 0} friends invited</Text>
                  </View>
                  <Button title="Invite" onPress={() => navigation.navigate("Referral")} variant="ghost" size="md" />
                </View>
              </FintechCard>
            </>
          )}
        </View>
      </ScrollView>
    </View>
  );
}
