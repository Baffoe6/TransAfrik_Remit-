import { RefreshControl, ScrollView, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useEffect, useMemo, useState } from "react";
import { Ionicons } from "@expo/vector-icons";
import {
  Button,
  FintechCard,
  HeroHeader,
  OfflineBanner,
  QuickActionGrid,
  SectionHeader,
  SkeletonCard,
  StatusPill,
  TrustBadge,
} from "../../components";
import {
  ActiveTransferWidget,
  CorridorSelector,
  FavoriteRecipientsCarousel,
  LiveCalculator,
  RateAlertWidget,
} from "../../components/worldclass";
import { dashboardApi, beneficiariesApi } from "../../api";
import { useAuthStore } from "../../store/authStore";
import { useCalculatorStore } from "../../store/calculatorStore";
import { useRateAlertStore } from "../../store/rateAlertStore";
import { useSettingsStore } from "../../store/settingsStore";
import { useSendFlowStore } from "../../store/sendFlowStore";
import { offlineCache } from "../../services/offlineCache";
import { greetingName } from "../../utils/format";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import type { DashboardSummary, Transfer } from "../../types";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { CORRIDORS } from "../../utils/constants";
import { hapticLight } from "../../services/haptics";

const ACTIVE_STATUSES = new Set(["pending_payment", "payment_received", "compliance_review", "submitted_to_partner", "processing"]);

export default function HomeScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const user = useAuthStore((s) => s.user);
  const [offline, setOffline] = useState(false);

  const calc = useCalculatorStore();
  const favoriteIds = useSettingsStore((s) => s.favoriteIds);
  const loadSettings = useSettingsStore((s) => s.load);
  const loadAlerts = useRateAlertStore((s) => s.load);
  const sendFlow = useSendFlowStore();

  useEffect(() => {
    loadSettings();
    loadAlerts();
  }, [loadSettings, loadAlerts]);

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
  const corridor = CORRIDORS.find((c) => c.code === calc.corridorCode);

  const activeTransfer = useMemo(
    () => (summary?.transfers.recent ?? []).find((t: Transfer) => ACTIVE_STATUSES.has(t.status)) ?? null,
    [summary?.transfers.recent],
  );

  const startSend = () => {
    hapticLight();
    sendFlow.reset();
    sendFlow.setDestination(calc.destinationCountry, calc.corridorCode, calc.currency);
    sendFlow.setAmount(calc.sendAmount);
    navigation.navigate("SendFlow");
  };

  const quickActions = [
    { id: "send", label: "Send", icon: "arrow-up-circle" as const, onPress: startSend, accent: true },
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
          subtitle={`Send to ${corridor?.name ?? "Africa"} — live rates & tracking`}
          rightAction={{ icon: "notifications-outline", onPress: () => navigation.navigate("Notifications") }}
        >
          <TrustBadge items={["Secure verification", "Partner payouts", "Encrypted"]} />
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
              <SectionHeader title="Corridor" />
              <CorridorSelector
                selected={calc.corridorCode}
                onSelect={(code, country, currency) => calc.setCorridor(code, country, currency)}
                compact
              />

              <LiveCalculator
                amount={calc.sendAmount}
                onAmountChange={calc.setSendAmount}
                destinationCountry={calc.destinationCountry}
                currency={calc.currency}
                corridorCode={calc.corridorCode}
                compact
              />
              <Button title="Send now" onPress={startSend} variant="gold" style={{ marginBottom: spacing.md }} />

              <ActiveTransferWidget
                transfer={activeTransfer}
                onPress={() => activeTransfer && navigation.navigate("TransferTracking", { id: activeTransfer.id })}
              />

              <FavoriteRecipientsCarousel
                beneficiaries={beneficiaries}
                favoriteIds={favoriteIds}
                onSelect={(b) => {
                  sendFlow.reset();
                  sendFlow.setDestination(calc.destinationCountry, calc.corridorCode, calc.currency);
                  sendFlow.setAmount(calc.sendAmount);
                  sendFlow.setBeneficiary(b);
                  sendFlow.setStep(2);
                  navigation.navigate("SendFlow");
                }}
                onAdd={() => navigation.navigate("BeneficiaryForm", {})}
              />

              <RateAlertWidget />

              <FintechCard variant={kycStatus === "Approved" ? "muted" : "accent"}>
                <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                  <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.sm }}>
                    <Ionicons name="shield-checkmark" size={22} color={theme.primary} />
                    <Text style={[typography.bodyBold, { color: theme.text }]}>Identity verification</Text>
                  </View>
                  <StatusPill label={kycStatus} variant={kycVariant as "success"} />
                </View>
                <Text style={[typography.caption, { color: theme.textSecondary, marginTop: 8 }]}>
                  {summary?.profile_completion.percent ?? 0}% complete · {summary?.kyc.documents_uploaded ?? 0} documents
                </Text>
                {kycStatus !== "Approved" && (
                  <Button title="Complete verification" onPress={() => navigation.navigate("Kyc")} variant="primary" style={{ marginTop: spacing.md }} />
                )}
              </FintechCard>

              <TouchableOpacity onPress={() => navigation.navigate("Referral")} activeOpacity={0.85}>
                <FintechCard variant="muted">
                  <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
                    <View style={{ width: 48, height: 48, borderRadius: 24, backgroundColor: theme.accentMuted, alignItems: "center", justifyContent: "center" }}>
                      <Ionicons name="gift" size={24} color={theme.accent} />
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={[typography.bodyBold, { color: theme.text }]}>Refer & earn R50</Text>
                      <Text style={[typography.caption, { color: theme.textSecondary }]}>
                        {summary?.referral_program.referrals_made ?? 0} friends invited · Limited promo
                      </Text>
                    </View>
                    <Ionicons name="chevron-forward" size={20} color={theme.textTertiary} />
                  </View>
                </FintechCard>
              </TouchableOpacity>
            </>
          )}
        </View>
      </ScrollView>
    </View>
  );
}
