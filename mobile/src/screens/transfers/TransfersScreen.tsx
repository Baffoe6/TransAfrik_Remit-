import { FlatList, Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, Button, Muted } from "../../components/ui";
import { transfersApi } from "../../api";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "../../navigation/MainNavigator";

export default function TransfersScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  const { data: transfers = [] } = useQuery({
    queryKey: ["transfers"],
    queryFn: async () => (await transfersApi.list()).data,
  });

  return (
    <Screen>
      <Button title="New Transfer" onPress={() => navigation.navigate("CreateTransfer")} />
      <Muted>Transfer History</Muted>
      <FlatList
        data={transfers}
        keyExtractor={(t) => String(t.id)}
        ListEmptyComponent={<Muted>No transfers yet</Muted>}
        renderItem={({ item }) => (
          <Button
            title={`${item.reference} — R${item.send_amount_zar}`}
            variant="outline"
            onPress={() => navigation.navigate("TransferDetail", { id: item.id })}
          />
        )}
      />
    </Screen>
  );
}
