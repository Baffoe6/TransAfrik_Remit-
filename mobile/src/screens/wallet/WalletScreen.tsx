import { ScrollView, Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, Card, Title, Muted } from "../../components/ui";
import { walletApi } from "../../api";

export default function WalletScreen() {
  const { data } = useQuery({
    queryKey: ["wallet"],
    queryFn: async () => (await walletApi.profile()).data,
  });

  return (
    <Screen>
      <ScrollView>
        <Title>Wallet Summary</Title>
        <Card>
          <Text style={{ fontSize: 28, fontWeight: "700", color: "#1B5E3B" }}>R{data?.total_sent_zar ?? "0.00"}</Text>
          <Muted>Total sent</Muted>
        </Card>
        <Card style={{ marginTop: 12 }}>
          <Text>{data?.total_transfers ?? 0} completed transfers</Text>
          {data?.last_transfer_at && <Muted>Last: {new Date(data.last_transfer_at).toLocaleDateString()}</Muted>}
        </Card>
      </ScrollView>
    </Screen>
  );
}
