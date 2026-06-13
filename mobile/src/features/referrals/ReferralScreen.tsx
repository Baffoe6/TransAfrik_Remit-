import { Linking, Share } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Body, Button, Caption, Card, H2, Screen } from "../../components";
import { referralApi } from "../../api";
import { formatZAR } from "../../utils/format";

export default function ReferralScreen() {
  const { data } = useQuery({ queryKey: ["referrals"], queryFn: async () => (await referralApi.dashboard()).data });

  const share = async (channel: "whatsapp" | "sms") => {
    const msg = `Join TransAfrik Remit with my code ${data?.referral_code ?? ""} and send money to Africa securely!`;
    if (channel === "whatsapp") {
      Linking.openURL(`whatsapp://send?text=${encodeURIComponent(msg)}`);
    } else {
      await Share.share({ message: msg });
    }
  };

  return (
    <Screen scroll>
      <H2>Refer & Earn</H2>
      <Card elevated accent={false}>
        <Caption>Your Code</Caption>
        <H2>{data?.referral_code ?? "—"}</H2>
      </Card>
      <Card>
        <Body>Friends invited: {data?.referrals_made ?? 0}</Body>
        <Body>Total earned: {formatZAR(data?.total_earnings_zar)}</Body>
        <Body>Pending: {formatZAR(data?.pending_rewards_zar)}</Body>
      </Card>
      <Button title="Share via WhatsApp" onPress={() => share("whatsapp")} variant="primary" />
      <Button title="Share via SMS" onPress={() => share("sms")} variant="outline" />
      <Caption>Terms and conditions apply. Rewards credited after friend's first completed transfer.</Caption>
    </Screen>
  );
}
