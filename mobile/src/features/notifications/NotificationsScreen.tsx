import { FlatList, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Body, Caption, EmptyState, H2, Screen } from "../../components";
import { notificationsApi } from "../../api";

export default function NotificationsScreen() {
  const { data: items = [] } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => notificationsApi.list(),
  });

  return (
    <Screen padded={false}>
      <View style={{ padding: 16 }}>
        <H2>Notifications</H2>
      </View>
      <FlatList
        data={items}
        keyExtractor={(n) => n.id}
        ListEmptyComponent={
          <EmptyState
            title="No notifications yet"
            message="Transfer updates, KYC results, and security alerts will appear here. Push notifications coming soon."
          />
        }
        renderItem={({ item }) => (
          <View style={{ padding: 16, borderBottomWidth: 1, borderBottomColor: "#E5E7EB" }}>
            <Body>{item.title}</Body>
            <Caption>{item.body}</Caption>
          </View>
        )}
      />
    </Screen>
  );
}
