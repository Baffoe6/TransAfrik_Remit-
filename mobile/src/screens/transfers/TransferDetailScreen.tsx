import { ScrollView, Text } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { useQuery } from "@tanstack/react-query";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { Screen, Card, Title, Muted } from "../../components/ui";
import { transfersApi } from "../../api";

type Props = NativeStackScreenProps<RootStackParamList, "TransferDetail">;

export default function TransferDetailScreen({ route }: Props) {
  const { id } = route.params;

  const { data: transfer } = useQuery({
    queryKey: ["transfer", id],
    queryFn: async () => (await transfersApi.get(id)).data,
  });

  const { data: timeline } = useQuery({
    queryKey: ["transfer-timeline", id],
    queryFn: async () => (await transfersApi.timeline(id)).data as { status: string; created_at: string }[],
  });

  return (
    <Screen>
      <ScrollView>
        <Title>{transfer?.reference}</Title>
        <Card style={{ marginBottom: 12 }}>
          <Muted>Status: {transfer?.status}</Muted>
          <Text>Send: R{transfer?.send_amount_zar}</Text>
          <Text>Fee: R{transfer?.fee_zar}</Text>
          <Text>Receive: {transfer?.receive_amount_ghs} GHS</Text>
          <Text>Rate: {transfer?.exchange_rate}</Text>
        </Card>
        {transfer?.payment_reference && (
          <Card style={{ marginBottom: 12 }}>
            <Text style={{ fontWeight: "600" }}>Payment Receipt</Text>
            <Muted>Ref: {transfer.payment_reference.reference_number}</Muted>
            {transfer.payment_reference.voucher_number && (
              <Muted>Voucher: {transfer.payment_reference.voucher_number}</Muted>
            )}
          </Card>
        )}
        <Card>
          <Text style={{ fontWeight: "600", marginBottom: 8 }}>Tracking</Text>
          {(timeline || []).map((t, i) => (
            <Muted key={i}>{t.status} — {new Date(t.created_at).toLocaleString()}</Muted>
          ))}
        </Card>
      </ScrollView>
    </Screen>
  );
}
