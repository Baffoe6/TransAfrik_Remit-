import { ScrollView, Text, Share } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, Card, Title, Muted, Button } from "../../components/ui";
import { referralApi } from "../../api";

export default function ReferralScreen() {
  const { data } = useQuery({
    queryKey: ["referral"],
    queryFn: async () => (await referralApi.dashboard()).data,
  });

  const invite = async () => {
    if (!data?.referral_code) return;
    await Share.share({
      message: `Join TransAfrik Remit with my code ${data.referral_code} and send money to Africa!`,
    });
  };

  return (
    <Screen>
      <ScrollView>
        <Title>Referral Program</Title>
        <Card style={{ marginBottom: 12 }}>
          <Muted>Your referral code</Muted>
          <Text style={{ fontSize: 24, fontWeight: "700", color: "#1B5E3B" }}>{data?.referral_code || "—"}</Text>
        </Card>
        <Card style={{ marginBottom: 12 }}>
          <Text>Referrals: {data?.referrals_made ?? 0}</Text>
          <Text>Total earnings: R{data?.total_earnings_zar ?? "0.00"}</Text>
          <Text>Pending: R{data?.pending_rewards_zar ?? "0.00"}</Text>
        </Card>
        <Button title="Invite Friends" onPress={invite} />
      </ScrollView>
    </Screen>
  );
}
