import { useEffect, useMemo, useState } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { Button, EmptyState, FintechCard, FilterChips, ListItem, SearchBar, SkeletonList, StatusPill } from "../../components";
import { beneficiariesApi } from "../../api";
import { useSettingsStore } from "../../store/settingsStore";
import { useSendFlowStore } from "../../store/sendFlowStore";
import { BENEFICIARY_CATEGORIES, NETWORK_LOGOS } from "../../utils/constants";
import { spacing, useAppTheme, radius } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { hapticLight } from "../../services/haptics";
import type { Beneficiary } from "../../types";

export default function BeneficiariesScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState<string>("all");
  const favoriteIds = useSettingsStore((s) => s.favoriteIds);
  const toggleFavorite = useSettingsStore((s) => s.toggleFavorite);
  const loadSettings = useSettingsStore((s) => s.load);
  const sendFlow = useSendFlowStore();

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const { data: list = [], refetch, isLoading } = useQuery({
    queryKey: ["beneficiaries"],
    queryFn: async () => (await beneficiariesApi.list()).data,
  });

  const filtered = useMemo(() => {
    return list.filter((b) => {
      const matchSearch = b.full_name.toLowerCase().includes(search.toLowerCase()) || b.country.toLowerCase().includes(search.toLowerCase());
      const matchCat = category === "all" || b.beneficiary_type === category;
      return matchSearch && matchCat;
    });
  }, [list, search, category]);

  const sorted = [...filtered].sort((a, b) => {
    const af = favoriteIds.includes(a.id) ? 0 : 1;
    const bf = favoriteIds.includes(b.id) ? 0 : 1;
    return af - bf;
  });

  const quickSend = (b: Beneficiary) => {
    if (b.status !== "approved") return;
    hapticLight();
    sendFlow.reset();
    sendFlow.setDestination(b.country, `ZA-${b.country}`, b.country === "GH" ? "GHS" : "USD");
    sendFlow.setBeneficiary(b);
    sendFlow.setStep(2);
    navigation.navigate("SendFlow");
  };

  const networkBadge = (b: Beneficiary) => {
    const provider = b.mobile_money_provider?.toLowerCase() ?? "";
    const net = NETWORK_LOGOS[provider];
    if (!net) return null;
    return (
      <View style={{ flexDirection: "row", alignItems: "center", gap: 4, marginTop: 4 }}>
        <View style={{ width: 20, height: 20, borderRadius: 10, backgroundColor: net.color, alignItems: "center", justifyContent: "center" }}>
          <Ionicons name={net.icon as keyof typeof Ionicons.glyphMap} size={10} color="#fff" />
        </View>
        <Text style={[typography.caption, { color: theme.textSecondary }]}>{net.label}</Text>
      </View>
    );
  };

  const verifyVariant = (status: string) =>
    status === "approved" ? "success" : status === "pending" ? "warning" : status === "rejected" ? "error" : "neutral";

  const statusLabel = (status: string) =>
    status === "approved" ? "Active" : status === "pending" ? "Under review" : status;

  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <View style={{ padding: spacing.lg, paddingBottom: 0 }}>
        <Text style={[typography.h1, { color: theme.text, marginBottom: spacing.xs }]}>Recipients</Text>
        <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.md }]}>Mobile money, bank & cash pickup</Text>
        <SearchBar value={search} onChangeText={setSearch} placeholder="Search recipients" />
        <FilterChips
          options={BENEFICIARY_CATEGORIES.map((c) => ({ value: c.value, label: c.label }))}
          selected={category}
          onSelect={setCategory}
        />
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
              message="Add someone to start sending money securely across Africa."
              actionLabel="Add recipient"
              onAction={() => navigation.navigate("BeneficiaryForm", {})}
            />
          }
          renderItem={({ item }) => (
            <FintechCard variant="default" padding="sm" style={{ marginBottom: spacing.sm }}>
              <ListItem
                title={item.full_name}
                subtitle={`${item.beneficiary_type.replace("_", " ")} · ${item.country}`}
                meta={item.mobile_wallet_number ?? item.bank_account_number ?? "—"}
                avatarName={item.full_name}
                onPress={() => navigation.navigate("BeneficiaryForm", { id: item.id })}
                right={
                  <View style={{ alignItems: "flex-end", gap: 6 }}>
                    <TouchableOpacity onPress={() => toggleFavorite(item.id)} hitSlop={{ top: 12, bottom: 12, left: 12, right: 12 }}>
                      <Ionicons name={favoriteIds.includes(item.id) ? "star" : "star-outline"} size={22} color={theme.accent} />
                    </TouchableOpacity>
                    <StatusPill label={statusLabel(item.status)} variant={verifyVariant(item.status) as "success"} size="sm" />
                  </View>
                }
                style={{ backgroundColor: "transparent" }}
              />
              {networkBadge(item)}
              <View style={{ flexDirection: "row", gap: spacing.sm, marginTop: spacing.sm, paddingHorizontal: spacing.sm }}>
                <TouchableOpacity onPress={() => quickSend(item)} style={{ flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 8, backgroundColor: theme.primaryMuted, borderRadius: radius.md }}>
                  <Ionicons name="send" size={16} color={theme.primary} />
                  <Text style={[typography.caption, { color: theme.primary, fontWeight: "700" }]}>Quick send</Text>
                </TouchableOpacity>
              </View>
            </FintechCard>
          )}
        />
      )}
    </View>
  );
}
