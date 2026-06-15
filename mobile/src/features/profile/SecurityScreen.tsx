import { Text, View } from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { AlertBanner, Button, FintechCard, ListItem, LoadingState, Screen, StatusPill } from "../../components";
import { authApi, type TrustedDevice } from "../../api/auth";
import { useSettingsStore } from "../../store/settingsStore";
import { spacing, useAppTheme, radius } from "../../theme";
import { typography } from "../../theme/typography";
import { formatDate } from "../../utils/format";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { hapticLight } from "../../services/haptics";

type Props = NativeStackScreenProps<RootStackParamList, "Security">;

const LOGIN_HISTORY = [
  { id: "1", device: "This device", ip: "102.xxx.xxx.xxx", at: new Date().toISOString(), success: true },
  { id: "2", device: "Chrome · Windows", ip: "41.xxx.xxx.xxx", at: new Date(Date.now() - 86400000 * 2).toISOString(), success: true },
];

export default function SecurityScreen({ navigation }: Props) {
  const theme = useAppTheme();
  const qc = useQueryClient();
  const biometricEnabled = useSettingsStore((s) => s.biometricEnabled);
  const pinEnabled = useSettingsStore((s) => s.pinEnabled);

  const { data: devices = [], isLoading, isError } = useQuery({
    queryKey: ["trusted-devices"],
    queryFn: async () => {
      const { data } = await authApi.devices();
      return Array.isArray(data) ? data : [];
    },
    retry: 1,
  });

  const trustMutation = useMutation({
    mutationFn: ({ id, trusted }: { id: number; trusted: boolean }) => authApi.trustDevice(id, trusted),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["trusted-devices"] }),
  });

  const toggleTrust = (device: TrustedDevice) => {
    hapticLight();
    trustMutation.mutate({ id: device.id, trusted: !device.trusted });
  };

  if (isLoading) return <LoadingState message="Loading security settings…" />;

  return (
    <Screen scroll>
      <Text style={[typography.h1, { color: theme.text }]}>Security center</Text>
      <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.lg }]}>
        Manage devices, sessions, MFA and biometrics
      </Text>

      {isError && <AlertBanner type="info" message="Some security data is unavailable offline — showing local settings." />}

      <FintechCard variant="elevated">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>MFA & authentication</Text>
        <ListItem
          title="Biometric unlock"
          subtitle={biometricEnabled ? "Face ID / fingerprint enabled" : "Not configured"}
          icon="finger-print-outline"
          onPress={() => navigation.navigate("EnableBiometrics")}
          showChevron
          style={{ backgroundColor: "transparent", paddingHorizontal: 0 }}
        />
        <ListItem
          title="PIN fallback"
          subtitle={pinEnabled ? "4-digit PIN active" : "Use PIN when biometrics unavailable"}
          icon="keypad-outline"
          onPress={() => {}}
          right={<StatusPill label={pinEnabled ? "On" : "Off"} variant={pinEnabled ? "success" : "neutral"} size="sm" />}
          style={{ backgroundColor: "transparent", paddingHorizontal: 0 }}
        />
        <Button title="Change PIN / password" onPress={() => {}} variant="outline" style={{ marginTop: spacing.sm }} />
      </FintechCard>

      <FintechCard variant="default">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Trusted devices</Text>
        {devices.length === 0 ? (
          <Text style={[typography.body, { color: theme.textSecondary }]}>No trusted devices recorded yet.</Text>
        ) : (
          devices.map((d) => (
            <View key={d.id} style={{ marginBottom: spacing.sm }}>
              <ListItem
                title={d.device_name ?? "Unknown device"}
                subtitle={`Last seen ${formatDate(d.last_seen_at)}${d.ip_address ? ` · ${d.ip_address}` : ""}`}
                icon="phone-portrait-outline"
                onPress={() => toggleTrust(d)}
                right={<StatusPill label={d.trusted ? "Trusted" : "Revoke"} variant={d.trusted ? "success" : "warning"} size="sm" />}
                style={{ backgroundColor: "transparent", paddingHorizontal: 0 }}
              />
            </View>
          ))
        )}
      </FintechCard>

      <FintechCard variant="muted">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Active sessions</Text>
        <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md, padding: spacing.md, backgroundColor: theme.surface, borderRadius: radius.lg }}>
          <Ionicons name="radio-button-on" size={12} color={theme.success} />
          <View style={{ flex: 1 }}>
            <Text style={[typography.bodyBold, { color: theme.text }]}>Current session</Text>
            <Text style={[typography.caption, { color: theme.textSecondary }]}>This device · Active now</Text>
          </View>
        </View>
        <Button title="Revoke other sessions" onPress={() => hapticLight()} variant="outline" style={{ marginTop: spacing.md }} />
      </FintechCard>

      <FintechCard variant="outline">
        <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Login history</Text>
        {LOGIN_HISTORY.map((entry) => (
          <View key={entry.id} style={{ flexDirection: "row", alignItems: "center", gap: spacing.md, paddingVertical: spacing.sm, borderBottomWidth: 1, borderBottomColor: theme.borderLight }}>
            <Ionicons name={entry.success ? "checkmark-circle" : "close-circle"} size={20} color={entry.success ? theme.success : theme.error} />
            <View style={{ flex: 1 }}>
              <Text style={[typography.bodySm, { color: theme.text, fontWeight: "600" }]}>{entry.device}</Text>
              <Text style={[typography.caption, { color: theme.textSecondary }]}>{formatDate(entry.at)} · {entry.ip}</Text>
            </View>
          </View>
        ))}
      </FintechCard>
    </Screen>
  );
}
