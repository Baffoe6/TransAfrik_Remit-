import { useCallback } from "react";
import { FlatList, Text, TouchableOpacity, View } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { Button, EmptyState, FintechCard, Screen } from "../../components";
import { notificationsApi, type AppNotification } from "../../api/notifications";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { formatRelativeDate } from "../../utils/format";
import { hapticLight } from "../../services/haptics";
import { RootStackParamList } from "../../navigation/MainNavigator";

type Nav = NativeStackNavigationProp<RootStackParamList>;

export default function NotificationsScreen() {
  const theme = useAppTheme();
  const navigation = useNavigation<Nav>();
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsApi.list(),
  });

  const items = data?.items ?? [];

  const handlePress = useCallback(
    async (item: AppNotification) => {
      hapticLight();
      if (item.read_status === "unread") {
        await notificationsApi.markRead(item.id);
        await queryClient.invalidateQueries({ queryKey: ["notifications"] });
        await queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
      }
      if (item.transfer_id) {
        navigation.navigate("TransferTracking", { id: item.transfer_id });
      }
    },
    [navigation, queryClient],
  );

  const markAll = async () => {
    await notificationsApi.markAllRead();
    await queryClient.invalidateQueries({ queryKey: ["notifications"] });
    await queryClient.invalidateQueries({ queryKey: ["notifications-unread"] });
  };

  return (
    <Screen padded={false}>
      <View style={{ padding: spacing.lg, flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
        <View>
          <Text style={[typography.h1, { color: theme.text }]}>Notifications</Text>
          <Text style={[typography.caption, { color: theme.textSecondary }]}>Transfer updates and alerts</Text>
        </View>
        {(data?.unread_count ?? 0) > 0 && <Button title="Mark all read" onPress={markAll} variant="ghost" size="md" />}
      </View>

      <FlatList
        data={items}
        keyExtractor={(n) => String(n.id)}
        refreshing={isLoading}
        onRefresh={() => queryClient.invalidateQueries({ queryKey: ["notifications"] })}
        contentContainerStyle={{ paddingHorizontal: spacing.lg, paddingBottom: spacing.xxxl, flexGrow: 1 }}
        ListEmptyComponent={
          !isLoading ? (
            <EmptyState title="No notifications yet" message="Transfer status updates will appear here as your money moves." />
          ) : null
        }
        renderItem={({ item }) => (
          <TouchableOpacity onPress={() => handlePress(item)} activeOpacity={0.8}>
            <FintechCard variant={item.read_status === "read" ? "muted" : "accent"} padding="md" style={{ marginBottom: spacing.sm }}>
              <View style={{ flexDirection: "row", gap: spacing.md }}>
                <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
                  <Ionicons name="swap-horizontal" size={20} color={theme.primary} />
                </View>
                <View style={{ flex: 1 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
                    <Text style={[typography.bodyBold, { color: theme.text, flex: 1 }]}>{item.title}</Text>
                    {item.read_status === "unread" && <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: theme.accent, marginLeft: 8 }} />}
                  </View>
                  <Text style={[typography.bodySm, { color: theme.textSecondary, marginTop: 2 }]}>{item.message}</Text>
                  {item.transfer_reference ? (
                    <Text style={[typography.caption, { color: theme.primary, marginTop: 4 }]}>{item.transfer_reference}</Text>
                  ) : null}
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
