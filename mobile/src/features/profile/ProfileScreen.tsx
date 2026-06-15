import { ScrollView, Switch, Text, TouchableOpacity, View } from "react-native";
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
import { USER_TIERS } from "../../utils/constants";
import { spacing, useAppTheme, radius } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { useSafeAreaInsets } from "react-native-safe-area-context";

const MENU = [
  { icon: "person-outline" as const, label: "Personal details", screen: "EditProfile" as const },
  { icon: "lock-closed-outline" as const, label: "Security center", screen: "Security" as const },
  { icon: "finger-print-outline" as const, label: "Biometrics", screen: "EnableBiometrics" as const },
  { icon: "document-text-outline" as const, label: "KYC verification", screen: "Kyc" as const },
  { icon: "gift-outline" as const, label: "Refer & earn", screen: "Referral" as const },
  { icon: "notifications-outline" as const, label: "Notifications", screen: "Notifications" as const },
  { icon: "help-circle-outline" as const, label: "Help & support", screen: "Support" as const },
];

function tierForKyc(kycStatus: string) {
  if (kycStatus === "Approved") return USER_TIERS[2];
  if (kycStatus === "Submitted" || kycStatus === "Reviewing") return USER_TIERS[1];
  return USER_TIERS[0];
}

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
  const tier = tierForKyc(kycStatus);
  const name = `${user?.first_name ?? ""} ${user?.last_name ?? ""}`.trim() || "User";
  const isDark = themeMode === "dark";

  return (
    <ScrollView style={{ flex: 1, backgroundColor: theme.bg }} contentContainerStyle={{ paddingBottom: insets.bottom + spacing.xxxl }}>
      <View style={{ alignItems: "center", paddingTop: insets.top + spacing.xl, paddingBottom: spacing.xl, paddingHorizontal: spacing.lg }}>
        <Avatar name={name} size={80} />
        <Text style={[typography.h2, { color: theme.text, marginTop: spacing.md }]}>{name}</Text>
        <Text style={[typography.body, { color: theme.textSecondary }]}>{formatPhoneDisplay(user?.mobile_number)}</Text>
        {user?.email ? <Text style={[typography.caption, { color: theme.textTertiary }]}>{user.email}</Text> : null}
        <View style={{ flexDirection: "row", gap: spacing.sm, marginTop: spacing.md }}>
          <StatusPill label={tier.label} variant="gold" size="md" />
          <StatusPill label={`KYC: ${kycStatus}`} variant={kycStatus === "Approved" ? "success" : "warning"} size="md" />
        </View>
      </View>

      <View style={{ paddingHorizontal: spacing.lg }}>
        <FintechCard variant="hero" padding="lg">
          <Text style={{ color: "rgba(255,255,255,0.75)", fontSize: 12, fontWeight: "600", letterSpacing: 0.5, textTransform: "uppercase" }}>Transfer limits</Text>
          <Text style={{ color: "#fff", fontSize: 28, fontWeight: "800", marginTop: 4 }}>{tier.limit}</Text>
          <Text style={{ color: "rgba(255,255,255,0.7)", fontSize: 13, marginTop: 4 }}>Upgrade tier by completing KYC verification</Text>
        </FintechCard>

        <FintechCard variant="muted">
          <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.sm }}>
            <Text style={[typography.bodyBold, { color: theme.text }]}>Account status</Text>
            <StatusPill label={user?.status ?? "active"} variant="success" size="sm" />
          </View>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
            <Text style={[typography.bodyBold, { color: theme.text }]}>Compliance</Text>
            <StatusPill label={kycStatus} variant={kycStatus === "Approved" ? "success" : "warning"} size="sm" />
          </View>
        </FintechCard>

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

        <TouchableOpacity onPress={() => navigation.navigate("Referral")} activeOpacity={0.85} style={{ marginBottom: spacing.md }}>
          <FintechCard variant="accent">
            <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
              <Ionicons name="people" size={24} color={theme.primary} />
              <View style={{ flex: 1 }}>
                <Text style={[typography.bodyBold, { color: theme.text }]}>Referral program</Text>
                <Text style={[typography.caption, { color: theme.textSecondary }]}>{summary?.referral_program.referrals_made ?? 0} friends invited · Earn R50 each</Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={theme.textTertiary} />
            </View>
          </FintechCard>
        </TouchableOpacity>

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
          TransAfrik Remit v1.0.0 · Phase 16
        </Text>
      </View>
    </ScrollView>
  );
}