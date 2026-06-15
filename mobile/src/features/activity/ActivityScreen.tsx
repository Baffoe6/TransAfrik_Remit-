import { useMemo, useState } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import {
  Button,
  EmptyState,
  FilterChips,
  FintechCard,
  ListItem,
  SearchBar,
  SkeletonList,
  StatusPill,
} from "../../components";
import { transfersApi } from "../../api";
import { offlineCache } from "../../services/offlineCache";
import { formatDate, formatZAR } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { Transfer } from "../../types";

const FILTERS = [
  { value: "all" as const, label: "All" },
  { value: "pending_payment" as const, label: "Pending" },
  { value: "processing" as const, label: "Processing" },
  { value: "completed" as const, label: "Completed" },
];

function statusVariant(status: string): "success" | "warning" | "error" | "info" | "neutral" {
  if (status === "completed") return "success";
  if (status === "failed") return "error";
  if (status === "pending_payment") return "warning";
  return "info";
}

export default function ActivityScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const [filter, setFilter] = useState<(typeof FILTERS)[number]["value"]>("all");
  const [search, setSearch] = useState("");

  const { data: transfers = [], refetch, isLoading } = useQuery({
    queryKey: ["transfers"],
    queryFn: async () => {
      try {
        const { data } = await transfersApi.list();
        await offlineCache.set("transfers", data);
        return data;
      } catch {
        return (await offlineCache.get<Transfer[]>("transfers")) ?? [];
      }
    },
  });

  const filtered = useMemo(() => {
    return transfers.filter((t) => {
      const matchFilter = filter === "all" || t.status === filter;
      const matchSearch = !search || t.reference.toLowerCase().includes(search.toLowerCase());
      return matchFilter && matchSearch;
    });
  }, [transfers, filter, search]);

  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <View style={{ padding: spacing.lg, paddingBottom: 0 }}>
        <Text style={[typography.h1, { color: theme.text, marginBottom: spacing.md }]}>Activity</Text>
        <SearchBar value={search} onChangeText={setSearch} placeholder="Search by reference" />
        <FilterChips options={FILTERS} selected={filter} onSelect={setFilter} />
      </View>

      {isLoading ? (
        <View style={{ padding: spacing.lg }}><SkeletonList /></View>
      ) : (
        <FlatList
          data={filtered}
          keyExtractor={(t) => String(t.id)}
          onRefresh={refetch}
          refreshing={false}
          contentContainerStyle={{ paddingBottom: spacing.xxxl, flexGrow: 1 }}
          ListEmptyComponent={
            <EmptyState
              icon="transfers"
              title="No transfers yet"
              message="When you send money, your transfers and receipts will appear here."
              actionLabel="Send money"
              onAction={() => navigation.navigate("SendFlow")}
            />
          }
          renderItem={({ item }) => (
            <FintechCard variant="default" padding="sm" style={{ marginHorizontal: spacing.lg, marginBottom: spacing.sm }}>
              <ListItem
                title={item.reference}
                subtitle={formatZAR(item.send_amount_zar)}
                meta={formatDate(item.created_at)}
                icon="swap-horizontal"
                onPress={() => navigation.navigate("TransferTracking", { id: item.id })}
                right={<StatusPill label={TRANSFER_STATUS_LABELS[item.status] ?? item.status} variant={statusVariant(item.status)} />}
                style={{ backgroundColor: "transparent" }}
              />
            </FintechCard>
          )}
        />
      )}
    </View>
  );
}
