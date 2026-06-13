import { useMemo, useState } from "react";
import { FlatList, TextInput, TouchableOpacity, Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Badge, Caption, EmptyState, Screen, H2 } from "../../components";
import { transfersApi } from "../../api";
import { offlineCache } from "../../services/offlineCache";
import { formatDate, formatZAR } from "../../utils/format";
import { TRANSFER_STATUS_LABELS } from "../../utils/constants";
import { typography } from "../../theme/typography";
import { spacing } from "../../theme/spacing";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { Transfer } from "../../types";

const FILTERS = ["all", "pending_payment", "processing", "completed"] as const;

export default function ActivityScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const [filter, setFilter] = useState<(typeof FILTERS)[number]>("all");
  const [search, setSearch] = useState("");

  const { data: transfers = [], refetch } = useQuery({
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
    <Screen padded={false}>
      <View style={{ padding: spacing.lg }}>
        <H2>Activity</H2>
        <TextInput
          placeholder="Search by reference..."
          value={search}
          onChangeText={setSearch}
          style={{ borderWidth: 1, borderColor: "#E5E7EB", borderRadius: 12, padding: 12, marginVertical: spacing.md, backgroundColor: "#fff" }}
        />
        <FlatList
          horizontal
          data={FILTERS}
          keyExtractor={(i) => i}
          showsHorizontalScrollIndicator={false}
          renderItem={({ item }) => (
            <TouchableOpacity onPress={() => setFilter(item)} style={{ paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, backgroundColor: filter === item ? "#1B5E3B" : "#F3F4F6", marginRight: 8 }}>
              <Text style={{ color: filter === item ? "#fff" : "#374151", fontWeight: "600", textTransform: "capitalize" }}>{item.replace("_", " ")}</Text>
            </TouchableOpacity>
          )}
          style={{ marginBottom: spacing.md }}
        />
      </View>
      <FlatList
        data={filtered}
        keyExtractor={(t) => String(t.id)}
        onRefresh={refetch}
        refreshing={false}
        ListEmptyComponent={<EmptyState title="No transfers" message="Your transfer history will appear here" actionLabel="Send Money" onAction={() => navigation.navigate("SendFlow")} />}
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => navigation.navigate("TransferTracking", { id: item.id })} style={{ padding: spacing.lg, borderBottomWidth: 1, borderBottomColor: "#E5E7EB", backgroundColor: "#fff" }}>
            <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
              <Text style={typography.bodyBold}>{item.reference}</Text>
              <Badge label={TRANSFER_STATUS_LABELS[item.status] ?? item.status} variant={item.status === "completed" ? "success" : "neutral"} />
            </View>
            <Caption>{formatZAR(item.send_amount_zar)} · {formatDate(item.created_at)}</Caption>
          </TouchableOpacity>
        )}
      />
    </Screen>
  );
}
