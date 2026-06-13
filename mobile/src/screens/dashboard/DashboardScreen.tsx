import { ScrollView, Text, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, Card, Title, Muted, Button } from "../../components/ui";
import { dashboardApi, walletApi } from "../../api";
import { offlineCache } from "../../services/offlineCache";
import type { DashboardSummary } from "../../types";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { useNavigation } from "@react-navigation/native";

export default function DashboardScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  const { data: summary, refetch, isFetching } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async (): Promise<DashboardSummary | null> => {
      try {
        const { data } = await dashboardApi.summary();
        await offlineCache.set("dashboard", data);
        return data;
      } catch {
        return offlineCache.get<DashboardSummary>("dashboard");
      }
    },
  });

  const { data: wallet } = useQuery({
    queryKey: ["wallet"],
    queryFn: async () => {
      try {
        const { data } = await walletApi.profile();
        return data;
      } catch {
        return null;
      }
    },
  });

  return (
    <Screen>
      <ScrollView refreshControl={<RefreshControl refreshing={isFetching} onRefresh={refetch} />}>
        <Title>Dashboard</Title>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600", fontSize: 16 }}>Mobile Identity</Text>
          <Muted>{summary?.mobile_identity.formatted_mobile || summary?.mobile_identity.mobile_number || "—"}</Muted>
          <Muted>{summary?.mobile_identity.verification_status}</Muted>
        </Card>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600" }}>Profile Completion</Text>
          <Text style={{ fontSize: 28, fontWeight: "700", color: "#1B5E3B" }}>{summary?.profile_completion.percent ?? 0}%</Text>
        </Card>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600" }}>KYC Status</Text>
          <Muted>{summary?.kyc.status ?? "Draft"} — {summary?.kyc.documents_uploaded ?? 0} docs</Muted>
          <Button title="Manage KYC" variant="outline" onPress={() => navigation.navigate("Kyc")} />
        </Card>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600" }}>Wallet Summary</Text>
          <Muted>Total sent: R{wallet?.total_sent_zar ?? "0.00"}</Muted>
          <Muted>{wallet?.total_transfers ?? 0} transfers</Muted>
          <Button title="View Wallet" variant="outline" onPress={() => navigation.navigate("Wallet")} />
        </Card>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600" }}>Transfers</Text>
          <Muted>{summary?.transfers.count ?? 0} total</Muted>
        </Card>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600" }}>Referrals</Text>
          <Muted>{summary?.referral_program.referrals_made ?? 0} friends invited</Muted>
          <Button title="Referral Program" variant="outline" onPress={() => navigation.navigate("Referral")} />
        </Card>
      </ScrollView>
    </Screen>
  );
}
