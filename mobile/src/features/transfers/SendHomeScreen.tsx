import { View } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { Button, FintechCard, HeroHeader, TrustBadge } from "../../components";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { Text } from "react-native";
import { RootStackParamList } from "../../navigation/MainNavigator";

const STEPS = [
  { icon: "globe-outline" as const, title: "Choose corridor", desc: "South Africa to Ghana" },
  { icon: "calculator-outline" as const, title: "Enter amount", desc: "See live rate & fees" },
  { icon: "person-outline" as const, title: "Pick recipient", desc: "Mobile money or bank" },
  { icon: "card-outline" as const, title: "Pay securely", desc: "Pay@, EFT & more" },
  { icon: "checkmark-circle-outline" as const, title: "Track delivery", desc: "Real-time updates" },
];

export default function SendHomeScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();

  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <HeroHeader title="Send money" subtitle="To Ghana in minutes — transparent fees, no surprises" compact>
        <TrustBadge items={["Best rates", "Secure payment", "Track live"]} />
      </HeroHeader>

      <View style={{ padding: spacing.lg, marginTop: -spacing.md }}>
        <Button title="Start new transfer" onPress={() => navigation.navigate("SendFlow")} variant="gold" />

        <Text style={[typography.label, { color: theme.textTertiary, marginTop: spacing.xl, marginBottom: spacing.md }]}>How it works</Text>
        {STEPS.map((s, i) => (
          <FintechCard key={s.title} variant="muted" padding="md" style={{ marginBottom: spacing.sm }}>
            <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
              <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
                <Ionicons name={s.icon} size={20} color={theme.primary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ fontWeight: "600", color: theme.text }}>{i + 1}. {s.title}</Text>
                <Text style={{ color: theme.textSecondary, fontSize: 13 }}>{s.desc}</Text>
              </View>
            </View>
          </FintechCard>
        ))}

        <Button title="View transfer history" onPress={() => navigation.navigate("Tabs", { screen: "Activity" } as never)} variant="outline" style={{ marginTop: spacing.md }} />
      </View>
    </View>
  );
}
