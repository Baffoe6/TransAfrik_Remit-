import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Badge, Body, Button, Caption, Card, H2, Screen } from "../../components";
import { profileApi, dashboardApi } from "../../api";
import { useAuthStore } from "../../store/authStore";
import { useSettingsStore } from "../../store/settingsStore";
import { formatPhoneDisplay } from "../../utils/phone";
import { RootStackParamList } from "../../navigation/MainNavigator";

export default function ProfileScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const biometricEnabled = useSettingsStore((s) => s.biometricEnabled);

  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: async () => (await profileApi.get()).data });
  const { data: summary } = useQuery({ queryKey: ["dashboard"], queryFn: async () => (await dashboardApi.summary()).data });

  return (
    <Screen scroll>
      <H2>Profile</H2>
      <Card elevated>
        <Body>{user?.first_name} {user?.last_name}</Body>
        <Caption>{formatPhoneDisplay(user?.mobile_number)}</Caption>
        <Caption>{user?.email ?? "No email"}</Caption>
        <Badge label={summary?.kyc.status ?? "KYC Draft"} variant={summary?.kyc.status === "Approved" ? "success" : "warning"} />
      </Card>

      <Card>
        <Caption>Personal Details</Caption>
        <Body>{profile?.address_line1 ?? "—"}</Body>
        <Caption>{profile?.city}, {profile?.province} {profile?.postal_code}</Caption>
        <Button title="Edit Profile" onPress={() => navigation.navigate("EditProfile")} variant="outline" />
      </Card>

      <Card>
        <H2>Security</H2>
        <Caption>Biometrics: {biometricEnabled ? "Enabled" : "Disabled"}</Caption>
        <Button title="Security Settings" onPress={() => navigation.navigate("Security")} variant="outline" />
        <Button title="Enable Biometrics" onPress={() => navigation.navigate("EnableBiometrics")} variant="ghost" />
      </Card>

      <Button title="KYC Verification" onPress={() => navigation.navigate("Kyc")} variant="secondary" />
      <Button title="Referrals" onPress={() => navigation.navigate("Referral")} variant="secondary" />
      <Button title="Notifications" onPress={() => navigation.navigate("Notifications")} variant="secondary" />
      <Button title="Support" onPress={() => navigation.navigate("Support")} variant="secondary" />
      <Button title="Sign Out" onPress={logout} variant="danger" />
    </Screen>
  );
}
