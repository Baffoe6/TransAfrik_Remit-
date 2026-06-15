import { useEffect } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";
import { Button, EmptyState, FintechCard, Screen } from "../../components";
import { notificationsApi, type AppNotification } from "../../api/notifications";
import { useNotificationInboxStore } from "../../store/notificationInboxStore";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { formatRelativeDate } from "../../utils/format";
import { hapticLight } from "../../services/haptics";

const TYPE_ICONS: Record<AppNotification["type"], keyof typeof Ionicons.glyphMap> = {
  transfer: "swap-horizontal",
  kyc: "shield-checkmark",
  promo: "gift",
  security: "lock-closed",
  rate: "trending-up",
};

export default function NotificationsScreen() {
  const theme = useAppTheme();
  const inbox = useNotificationInboxStore();
  const { load, markRead, markAllRead, items } = inbox;

  const { data: apiItems = [] } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsApi.list(),
  });

  useEffect(() => {
    load();
  }, [load]);

  const merged = [...items, ...apiItems.filter((a) => !items.some((i) => i.id === a.id))];

  const handleRead = async (id: string) => {
    hapticLight();
    await markRead(id);
    await notificationsApi.markRead(id);
  };

  return (
    <Screen padded={false}>
      <View style={{ padding: spacing.lg, flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <View>
          <Text style={[typography.h1, { color: theme.text }]}>Notifications</Text>
          <Text style={[typography.caption, { color: theme.textSecondary }]}>Rate alerts · transfers · KYC · promos</Text>
        </View>
        {merged.some((n) => !n.read) && (
          <Button title="Mark all read" onPress={markAllRead} variant="ghost" size="md" />
        )}
      </View>

      <FlatList
        data={merged}
        keyExtractor={(n) => n.id}
        contentContainerStyle={{ paddingHorizontal: spacing.lg, paddingBottom: spacing.xxxl, flexGrow: 1 }}
        ListEmptyComponent={
          <EmptyState
            title="No notifications yet"
            message="Transfer updates, rate alerts, KYC results, and security alerts will appear here."
          />
        }
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => handleRead(item.id)} activeOpacity={0.8}>
            <FintechCard variant={item.read ? "muted" : "accent"} padding="md" style={{ marginBottom: spacing.sm }}>
              <View style={{ flexDirection: "row", gap: spacing.md }}>
                <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
                  <Ionicons name={TYPE_ICONS[item.type]} size={20} color={theme.primary} />
                </View>
                <View style={{ flex: 1 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
                    <Text style={[typography.bodyBold, { color: theme.text }]}>{item.title}</Text>
                    {!item.read && <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: theme.accent }} />}
                  </View>
                  <Text style={[typography.bodySm, { color: theme.textSecondary, marginTop: 2 }]}>{item.body}</Text>
                  <Text style={[typography.caption, { color: theme.textTertiary, marginTop: 4 }]}>{formatRelativeDate(item.created_at)}</Text>
                </View>
              </View>
            </FintechCard>
          </TouchableOpacity>
        )}
      />
    </Screen>
  );
}
