import { useMemo, useState } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { Button, EmptyState, FintechCard, ListItem, SearchBar, SkeletonList } from "../../components";
import { beneficiariesApi } from "../../api";
import { useSettingsStore } from "../../store/settingsStore";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";

export default function BeneficiariesScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const [search, setSearch] = useState("");
  const favoriteIds = useSettingsStore((s) => s.favoriteIds);
  const toggleFavorite = useSettingsStore((s) => s.toggleFavorite);

  const { data: list = [], refetch, isLoading } = useQuery({
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
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <View style={{ padding: spacing.lg, paddingBottom: 0 }}>
        <Text style={[typography.h1, { color: theme.text, marginBottom: spacing.xs }]}>Recipients</Text>
        <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.md }]}>People you send money to</Text>
        <SearchBar value={search} onChangeText={setSearch} placeholder="Search recipients" />
        <Button title="Add recipient" onPress={() => navigation.navigate("BeneficiaryForm", {})} variant="primary" style={{ marginBottom: spacing.md }} />
      </View>

      {isLoading ? (
        <View style={{ padding: spacing.lg }}><SkeletonList /></View>
      ) : (
        <FlatList
          data={sorted}
          keyExtractor={(b) => String(b.id)}
          onRefresh={refetch}
          refreshing={false}
          contentContainerStyle={{ paddingHorizontal: spacing.lg, paddingBottom: spacing.xxxl, flexGrow: 1 }}
          ListEmptyComponent={
            <EmptyState
              icon="beneficiaries"
              title="No recipients yet"
              message="Add someone in Ghana to start sending money securely."
              actionLabel="Add recipient"
              onAction={() => navigation.navigate("BeneficiaryForm", {})}
            />
          }
          renderItem={({ item }) => (
            <FintechCard variant="default" padding="sm" style={{ marginBottom: spacing.sm }}>
              <ListItem
                title={item.full_name}
                subtitle={`${item.beneficiary_type.replace("_", " ")} · ${item.country}`}
                meta={item.mobile_wallet_number ?? item.bank_account_number ?? item.mobile_money_provider ?? "—"}
                avatarName={item.full_name}
                onPress={() => navigation.navigate("BeneficiaryForm", { id: item.id })}
                right={
                  <TouchableOpacity onPress={() => toggleFavorite(item.id)} hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}>
                    <Ionicons name={favoriteIds.includes(item.id) ? "star" : "star-outline"} size={22} color={theme.accent} />
                  </TouchableOpacity>
                }
                style={{ backgroundColor: "transparent" }}
              />
            </FintechCard>
          )}
        />
      )}
    </View>
  );
}
