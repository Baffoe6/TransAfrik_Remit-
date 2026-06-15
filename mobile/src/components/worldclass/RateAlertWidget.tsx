import { Text, TouchableOpacity, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { FintechCard } from "../fintech";
import { useAppTheme, spacing } from "../../theme";
import { typography } from "../../theme/typography";
import { useRateAlertStore } from "../../store/rateAlertStore";
import { CORRIDORS } from "../../utils/constants";

export function RateAlertWidget() {
  const theme = useAppTheme();
  const { alerts, toggleAlert } = useRateAlertStore();
  const active = alerts.filter((a) => a.enabled);

  if (!active.length) {
    return (
      <FintechCard variant="muted">
        <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
          <Ionicons name="notifications-outline" size={24} color={theme.primary} />
          <View style={{ flex: 1 }}>
            <Text style={[typography.bodyBold, { color: theme.text }]}>Rate alerts</Text>
            <Text style={[typography.caption, { color: theme.textSecondary }]}>Get notified when rates improve</Text>
          </View>
        </View>
      </FintechCard>
    );
  }

  return (
    <FintechCard variant="muted">
      <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.sm }]}>Rate alerts</Text>
      {active.slice(0, 2).map((a) => {
        const corridor = CORRIDORS.find((c) => c.code === a.corridorCode);
        return (
          <TouchableOpacity key={a.id} onPress={() => toggleAlert(a.id)} style={{ flexDirection: "row", justifyContent: "space-between", paddingVertical: 6 }}>
            <Text style={[typography.bodySm, { color: theme.text }]}>{corridor?.flag} Alert at {a.targetRate} {a.currency}</Text>
            <Ionicons name="notifications" size={18} color={theme.accent} />
          </TouchableOpacity>
        );
      })}
    </FintechCard>
  );
}
