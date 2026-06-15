import { ScrollView, Switch, Text, View } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import {
  Avatar,
  Button,
  FintechCard,
  ListItem,
  StatusPill,
} from "../../components";
import { profileApi, dashboardApi } from "../../api";
import { useAuthStore } from "../../store/authStore";
import { useSettingsStore } from "../../store/settingsStore";
import { useThemeStore } from "../../store/themeStore";
import { formatPhoneDisplay } from "../../utils/phone";
import { spacing, useAppTheme, radius } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { useSafeAreaInsets } from "react-native-safe-area-context";

const MENU = [
  { icon: "person-outline" as const, label: "Personal details", screen: "EditProfile" as const },
  { icon: "shield-checkmark-outline" as const, label: "Security", screen: "Security" as const },
  { icon: "finger-print-outline" as const, label: "Biometrics", screen: "EnableBiometrics" as const },
  { icon: "document-text-outline" as const, label: "KYC verification", screen: "Kyc" as const },
  { icon: "gift-outline" as const, label: "Refer & earn", screen: "Referral" as const },
  { icon: "notifications-outline" as const, label: "Notifications", screen: "Notifications" as const },
  { icon: "help-circle-outline" as const, label: "Help & support", screen: "Support" as const },
];

export default function ProfileScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const insets = useSafeAreaInsets();
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const biometricEnabled = useSettingsStore((s) => s.biometricEnabled);
  const themeMode = useThemeStore((s) => s.mode);
  const setThemeMode = useThemeStore((s) => s.setMode);

  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: async () => (await profileApi.get()).data });
  const { data: summary } = useQuery({ queryKey: ["dashboard"], queryFn: async () => (await dashboardApi.summary()).data });

  const kycStatus = summary?.kyc.status ?? "Draft";
  const name = `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim() || "User";
  const isDark = themeMode === "dark";

  return (
    <ScrollView style={{ flex: 1, backgroundColor: theme.bg }} contentContainerStyle={{ paddingBottom: insets.bottom + spacing.xxxl }}>
      <View style={{ alignItems: "center", paddingTop: insets.top + spacing.xl, paddingBottom: spacing.xl, paddingHorizontal: spacing.lg }}>
        <Avatar name={name} size={80} />
        <Text style={[typography.h2, { color: theme.text, marginTop: spacing.md }]}>{name}</Text>
        <Text style={[typography.body, { color: theme.textSecondary }]}>{formatPhoneDisplay(user?.mobile_number)}</Text>
        {user?.email ? <Text style={[typography.caption, { color: theme.textTertiary }]}>{user.email}</Text> : null}
        <View style={{ marginTop: spacing.md }}>
          <StatusPill label={`KYC: ${kycStatus}`} variant={kycStatus === "Approved" ? "success" : "warning"} size="md" />
        </View>
      </View>

      <View style={{ paddingHorizontal: spacing.lg }}>
        <FintechCard variant="elevated" padding="sm">
          {MENU.map((item, i) => (
            <View key={item.screen}>
              {i > 0 && <View style={{ height: 1, backgroundColor: theme.borderLight, marginLeft: 56 }} />}
              <ListItem
                title={item.label}
                icon={item.icon}
                onPress={() => navigation.navigate(item.screen)}
                style={{ backgroundColor: "transparent" }}
              />
            </View>
          ))}
        </FintechCard>

        <FintechCard variant="muted">
          <View style={{ flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
              <View style={{ width: 44, height: 44, borderRadius: radius.md, backgroundColor: theme.surface, alignItems: "center", justifyContent: "center" }}>
                <Ionicons name="moon-outline" size={22} color={theme.primary} />
              </View>
              <View>
                <Text style={[typography.bodyBold, { color: theme.text }]}>Dark mode</Text>
                <Text style={[typography.caption, { color: theme.textSecondary }]}>{themeMode === "system" ? "System" : themeMode}</Text>
              </View>
            </View>
            <Switch
              value={isDark}
              onValueChange={(v) => setThemeMode(v ? "dark" : "light")}
              trackColor={{ false: theme.border, true: theme.primary }}
            />
          </View>
        </FintechCard>

        {biometricEnabled && (
          <Text style={[typography.caption, { color: theme.success, textAlign: "center", marginBottom: spacing.md }]}>
            ✓ Biometric login enabled
          </Text>
        )}

        {profile?.address_line1 && (
          <FintechCard variant="outline">
            <Text style={[typography.label, { color: theme.textTertiary, marginBottom: spacing.sm }]}>Address</Text>
            <Text style={[typography.body, { color: theme.text }]}>{profile.address_line1}</Text>
            <Text style={[typography.caption, { color: theme.textSecondary }]}>{profile.city}, {profile.province} {profile.postal_code}</Text>
          </FintechCard>
        )}

        <Button title="Sign out" onPress={logout} variant="outline" style={{ marginTop: spacing.md, borderColor: theme.error }} />
        <Text style={[typography.caption, { color: theme.textTertiary, textAlign: "center", marginTop: spacing.lg }]}>
          TransAfrik Remit v1.0.0-preview
        </Text>
      </View>
    </ScrollView>
  );
}
