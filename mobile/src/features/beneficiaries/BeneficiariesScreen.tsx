import { useMemo, useState } from "react";
import { FlatList, TextInput, TouchableOpacity, Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Button, Caption, EmptyState, H2, Screen } from "../../components";
import { beneficiariesApi } from "../../api";
import { useSettingsStore } from "../../store/settingsStore";
import { typography } from "../../theme/typography";
import { spacing } from "../../theme/spacing";
import { RootStackParamList } from "../../navigation/MainNavigator";

export default function BeneficiariesScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [search, setSearch] = useState("");
  const favoriteIds = useSettingsStore((s) => s.favoriteIds);
  const toggleFavorite = useSettingsStore((s) => s.toggleFavorite);

  const { data: list = [], refetch } = useQuery({
    queryKey: ["beneficiaries"],
    queryFn: async () => (await beneficiariesApi.list()).data,
  });

  const filtered = useMemo(
    () => list.filter((b) => b.full_name.toLowerCase().includes(search.toLowerCase()) || b.country.toLowerCase().includes(search.toLowerCase())),
    [list, search],
  );

  const sorted = [...filtered].sort((a, b) => {
    const af = favoriteIds.includes(a.id) ? 0 : 1;
    const bf = favoriteIds.includes(b.id) ? 0 : 1;
    return af - bf;
  });

  return (
    <Screen padded={false}>
      <View style={{ padding: spacing.lg }}>
        <H2>Beneficiaries</H2>
        <TextInput placeholder="Search..." value={search} onChangeText={setSearch} style={{ borderWidth: 1, borderColor: "#E5E7EB", borderRadius: 12, padding: 12, marginVertical: spacing.md }} />
        <Button title="Add Beneficiary" onPress={() => navigation.navigate("BeneficiaryForm", {})} />
      </View>
      <FlatList
        data={sorted}
        keyExtractor={(b) => String(b.id)}
        onRefresh={refetch}
        refreshing={false}
        ListEmptyComponent={<EmptyState title="No beneficiaries" message="Add someone to send money to" actionLabel="Add Beneficiary" onAction={() => navigation.navigate("BeneficiaryForm", {})} />}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => navigation.navigate("BeneficiaryForm", { id: item.id })} style={{ padding: spacing.lg, borderBottomWidth: 1, borderBottomColor: "#E5E7EB", backgroundColor: "#fff" }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
              <Text style={typography.bodyBold}>{item.full_name}</Text>
              <TouchableOpacity onPress={() => toggleFavorite(item.id)}>
                <Text>{favoriteIds.includes(item.id) ? "★" : "☆"}</Text>
              </TouchableOpacity>
            </View>
            <Caption>{item.beneficiary_type.replace("_", " ")} · {item.country}</Caption>
            <Caption>{item.mobile_wallet_number ?? item.bank_account_number ?? item.mobile_money_provider ?? "—"}</Caption>
          </TouchableOpacity>
        )}
      />
    </Screen>
  );
}
