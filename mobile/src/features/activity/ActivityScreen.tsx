import { useMemo, useState } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import {
  EmptyState,
  FilterChips,
  FintechCard,
  ListItem,
  SearchBar,
  SkeletonList,
  StatusPill,
  Timeline,
} from "../../components";
import { transfersApi } from "../../api";
import { offlineCache } from "../../services/offlineCache";
import { formatDate, formatZAR } from "../../utils/format";
import { ACTIVITY_STATUS_FILTERS, ACTIVITY_TIME_FILTERS, TRANSFER_STATUS_LABELS } from "../../utils/constants";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import type { Transfer } from "../../types";

const PROCESSING_STATUSES = new Set(["payment_received", "compliance_review", "submitted_to_partner", "processing"]);

function statusVariant(status: string): "success" | "warning" | "error" | "info" | "neutral" {
  if (status === "completed") return "success";
  if (status === "failed" || status === "rejected") return "error";
  if (status === "refunded") return "neutral";
  if (status === "pending_payment") return "warning";
  return "info";
}

function matchesStatusFilter(status: string, filter: string) {
  if (filter === "all") return true;
  if (filter === "processing") return PROCESSING_STATUSES.has(status);
  return status === filter;
}

function matchesTimeFilter(createdAt: string, filter: string) {
  if (filter === "all") return true;
  const d = new Date(createdAt);
  const now = new Date();
  if (filter === "today") return d.toDateString() === now.toDateString();
  if (filter === "week") return now.getTime() - d.getTime() < 7 * 86400000;
  if (filter === "month") return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  return true;
}

const PROGRESS: Record<string, number> = {
  pending_payment: 15,
  payment_received: 35,
  compliance_review: 50,
  submitted_to_partner: 65,
  processing: 80,
  completed: 100,
  failed: 0,
  refunded: 0,
};

export default function ActivityScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [timeFilter, setTimeFilter] = useState<string>("all");
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
      const matchStatus = matchesStatusFilter(t.status, statusFilter);
      const matchTime = matchesTimeFilter(t.created_at, timeFilter);
      const matchSearch = !search || t.reference.toLowerCase().includes(search.toLowerCase());
      return matchStatus && matchTime && matchSearch;
    });
  }, [transfers, statusFilter, timeFilter, search]);

  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <View style={{ padding: spacing.lg, paddingBottom: 0 }}>
        <Text style={[typography.h1, { color: theme.text, marginBottom: spacing.md }]}>Activity</Text>
        <SearchBar value={search} onChangeText={setSearch} placeholder="Search by reference" />
        <FilterChips
          options={ACTIVITY_TIME_FILTERS.map((f) => ({ value: f.value, label: f.label }))}
          selected={timeFilter}
          onSelect={setTimeFilter}
        />
        <FilterChips
          options={ACTIVITY_STATUS_FILTERS.map((f) => ({ value: f.value, label: f.label }))}
          selected={statusFilter}
          onSelect={setStatusFilter}
        />
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
          renderItem={({ item }) => {
            const progress = PROGRESS[item.status] ?? 20;
            return (
              <FintechCard variant="default" padding="md" style={{ marginHorizontal: spacing.lg, marginBottom: spacing.sm }}>
                <ListItem
                  title={item.reference}
                  subtitle={formatZAR(item.send_amount_zar)}
                  meta={formatDate(item.created_at)}
                  icon="swap-horizontal"
                  onPress={() => navigation.navigate("TransferTracking", { id: item.id })}
                  right={<StatusPill label={TRANSFER_STATUS_LABELS[item.status] ?? item.status} variant={statusVariant(item.status)} />}
                  style={{ backgroundColor: "transparent", paddingHorizontal: 0 }}
                />
                <View style={{ height: 4, backgroundColor: theme.border, borderRadius: 2, marginTop: spacing.sm, overflow: "hidden" }}>
                  <View style={{ width: `${progress}%`, height: 4, backgroundColor: item.status === "failed" ? theme.error : theme.primary }} />
                </View>
                <Timeline
                  steps={[
                    { title: "Created", completed: true },
                    { title: TRANSFER_STATUS_LABELS[item.status] ?? item.status, active: !["completed", "failed", "refunded"].includes(item.status) },
                    { title: "Delivered", completed: item.status === "completed" },
                  ]}
                />
                <View style={{ flexDirection: "row", gap: spacing.sm, marginTop: spacing.sm }}>
                  <TouchableOpacity
                    onPress={() => navigation.navigate("Receipt", { id: item.id })}
                    style={{ flexDirection: "row", alignItems: "center", gap: 4 }}
                  >
                    <Ionicons name="document-text-outline" size={16} color={theme.primary} />
                    <Text style={[typography.caption, { color: theme.primary, fontWeight: "600" }]}>Export receipt</Text>
                  </TouchableOpacity>
                </View>
              </FintechCard>
            );
          }}
        />
      )}
    </View>
  );
}
