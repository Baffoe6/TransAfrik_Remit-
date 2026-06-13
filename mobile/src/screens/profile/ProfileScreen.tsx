import { ScrollView, Text } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { Screen, Card, Title, Muted, Button } from "../../components/ui";
import { useAuthStore } from "../../store/authStore";
import { useThemeStore } from "../../store/themeStore";
import { profileApi } from "../../api";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { RootStackParamList } from "../../navigation/MainNavigator";

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const { mode, setMode } = useThemeStore();
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  const { data: profile } = useQuery({
    queryKey: ["profile"],
    queryFn: async () => (await profileApi.get()).data,
  });

  return (
    <Screen>
      <ScrollView>
        <Title>Profile</Title>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600" }}>{profile?.first_name} {profile?.last_name}</Text>
          <Muted>{user?.mobile_number}</Muted>
          <Muted>{user?.email || "No email"}</Muted>
          <Muted>Verified: {user?.phone_verified ? "Yes" : "Pending"}</Muted>
        </Card>
        <Card style={{ marginBottom: 12 }}>
          <Text style={{ fontWeight: "600" }}>Appearance</Text>
          <Button title={`Theme: ${mode}`} variant="outline" onPress={() => setMode(mode === "dark" ? "light" : mode === "light" ? "system" : "dark")} />
        </Card>
        <Button title="KYC Documents" variant="outline" onPress={() => navigation.navigate("Kyc")} />
        <Button title="Wallet" variant="outline" onPress={() => navigation.navigate("Wallet")} />
        <Button title="Referrals" variant="outline" onPress={() => navigation.navigate("Referral")} />
        <Button title="Sign Out" variant="danger" onPress={logout} />
      </ScrollView>
    </Screen>
  );
}
