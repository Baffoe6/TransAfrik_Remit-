import { useState } from "react";
import { FlatList, Text, View } from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Screen, Input, Button, Muted } from "../../components/ui";
import { beneficiariesApi } from "../../api";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { useNavigation } from "@react-navigation/native";

export default function BeneficiariesScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [search, setSearch] = useState("");
  const qc = useQueryClient();

  const { data: list = [] } = useQuery({
    queryKey: ["beneficiaries"],
    queryFn: async () => (await beneficiariesApi.list()).data,
  });

  const remove = useMutation({
    mutationFn: (id: number) => beneficiariesApi.remove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["beneficiaries"] }),
  });

  const filtered = list.filter(
    (b) =>
      b.full_name.toLowerCase().includes(search.toLowerCase()) ||
      (b.mobile_wallet_number || "").includes(search),
  );

  return (
    <Screen>
      <Input label="Search" value={search} onChangeText={setSearch} placeholder="Name or mobile..." />
      <Button title="Add Beneficiary" onPress={() => navigation.navigate("BeneficiaryForm", {})} />
      <FlatList
        data={filtered}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <View style={{ paddingVertical: 12, borderBottomWidth: 1, borderColor: "#eee" }}>
            <Text style={{ fontWeight: "600" }}>{item.full_name}</Text>
            <Muted>{item.mobile_money_provider} · {item.mobile_wallet_number}</Muted>
            <Muted>{item.country} · {item.status}</Muted>
            <View style={{ flexDirection: "row", gap: 8, marginTop: 8 }}>
              <Button title="Edit" variant="outline" onPress={() => navigation.navigate("BeneficiaryForm", { id: item.id })} />
              <Button title="Delete" variant="danger" onPress={() => remove.mutate(item.id)} />
            </View>
          </View>
        )}
        ListEmptyComponent={<Muted>No beneficiaries yet</Muted>}
      />
    </Screen>
  );
}
