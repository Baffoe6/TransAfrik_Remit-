import { RefreshControl, ScrollView, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { LinearGradient } from "expo-linear-gradient";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { useState } from "react";
import { Badge, Body, Button, Card, Caption, H2, OfflineBanner, Skeleton, TrustRow } from "../../components";
import { dashboardApi, beneficiariesApi } from "../../api";
import { useAuthStore } from "../../store/authStore";
import { offlineCache } from "../../services/offlineCache";
import { formatZAR, greetingName } from "../../utils/format";
import { spacing } from "../../theme/spacing";
import { typography } from "../../theme/typography";
import type { DashboardSummary } from "../../types";
import { RootStackParamList } from "../../navigation/MainNavigator";

export default function HomeScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
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

  const kycVariant = summary?.kyc.status === "Approved" ? "success" : summary?.kyc.status === "Rejected" ? "error" : "warning";

  return (
    <ScrollView refreshControl={<RefreshControl refreshing={isFetching} onRefresh={refetch} />} style={{ flex: 1, backgroundColor: "#F8FAF9" }}>
      {offline && <OfflineBanner />}
      <LinearGradient colors={["#1B5E3B", "#0D3D24"]} style={{ padding: spacing.xl, paddingTop: spacing.xxl, borderBottomLeftRadius: 24, borderBottomRightRadius: 24 }}>
        <Text style={[typography.caption, { color: "rgba(255,255,255,0.8)" }]}>{greetingName(user?.first_name)}</Text>
        <Text style={[typography.h1, { color: "#fff", marginBottom: spacing.md }]}>TransAfrik Remit</Text>
        <TrustRow items={["Secure transfer", "Partner processed", "Compliance checked"]} />
      </LinearGradient>

      <View style={{ padding: spacing.lg }}>
        <Button title="Quick Send" onPress={() => navigation.navigate("SendFlow")} variant="gold" style={{ marginBottom: spacing.lg }} />

        {isLoading ? (
          <>
            <Skeleton height={100} />
            <Skeleton height={80} />
          </>
        ) : (
          <>
            <Card elevated>
              <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                <Body>KYC Status</Body>
                <Badge label={summary?.kyc.status ?? "Draft"} variant={kycVariant as "success"} />
              </View>
              <Caption>{summary?.profile_completion.percent ?? 0}% profile complete · {summary?.kyc.documents_uploaded ?? 0} docs uploaded</Caption>
              {(summary?.kyc.status !== "Approved") && (
                <Button title="Complete KYC" onPress={() => navigation.navigate("Kyc")} variant="outline" style={{ marginTop: spacing.sm }} />
              )}
            </Card>

            <Card elevated accent={false}>
              <Caption>Exchange Rate</Caption>
              <H2>1 ZAR ≈ live rate</H2>
              <Caption>ZA → Ghana corridor · Fees from R15</Caption>
            </Card>

            <Card>
              <H2>Recent Transfers</H2>
              {(summary?.transfers.recent ?? []).slice(0, 3).map((t) => (
                <TouchableOpacity key={t.id} onPress={() => navigation.navigate("TransferTracking", { id: t.id })} style={{ paddingVertical: spacing.sm, borderBottomWidth: 1, borderBottomColor: "#E5E7EB" }}>
                  <Text style={typography.bodyBold}>{t.reference}</Text>
                  <Caption>{formatZAR(t.send_amount_zar)} · {t.status}</Caption>
                </TouchableOpacity>
              ))}
              {!summary?.transfers.recent?.length && <Caption>No transfers yet</Caption>}
            </Card>

            <Card>
              <H2>Saved Beneficiaries</H2>
              {beneficiaries.slice(0, 3).map((b) => (
                <Text key={b.id} style={[typography.body, { paddingVertical: 4 }]}>{b.full_name} · {b.country}</Text>
              ))}
              <Button title="View All" onPress={() => navigation.navigate("Tabs", { screen: "Beneficiaries" } as never)} variant="ghost" />
            </Card>

            <Card>
              <H2>Refer & Earn</H2>
              <Caption>{summary?.referral_program.referrals_made ?? 0} friends invited</Caption>
              <Button title="Invite Friends" onPress={() => navigation.navigate("Referral")} variant="outline" />
            </Card>

            <Card>
              <H2>Need Help?</H2>
              <Button title="Contact Support" onPress={() => navigation.navigate("Support")} variant="secondary" />
            </Card>
          </>
        )}
      </View>
    </ScrollView>
  );
}
