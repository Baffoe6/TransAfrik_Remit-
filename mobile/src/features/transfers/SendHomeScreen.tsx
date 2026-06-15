import { useEffect } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { Button, FintechCard, HeroHeader, TrustBadge } from "../../components";
import { CorridorSelector, LiveCalculator } from "../../components/worldclass";
import { useCalculatorStore } from "../../store/calculatorStore";
import { useSendFlowStore } from "../../store/sendFlowStore";
import { useTemplateStore } from "../../store/templateStore";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { hapticLight } from "../../services/haptics";

export default function SendHomeScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();
  const theme = useAppTheme();
  const calc = useCalculatorStore();
  const sendFlow = useSendFlowStore();
  const { templates, load, loaded } = useTemplateStore();

  useEffect(() => {
    if (!loaded) load();
  }, [load, loaded]);

  const startSend = () => {
    hapticLight();
    sendFlow.reset();
    sendFlow.setDestination(calc.destinationCountry, calc.corridorCode, calc.currency);
    sendFlow.setAmount(calc.sendAmount);
    navigation.navigate("SendFlow");
  };

  const useTemplate = (tpl: (typeof templates)[0]) => {
    hapticLight();
    sendFlow.reset();
    sendFlow.setDestination(tpl.destinationCountry, tpl.corridorCode, tpl.currency);
    sendFlow.setAmount(tpl.amount);
    sendFlow.setStep(3);
    navigation.navigate("SendFlow");
  };

  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <HeroHeader title="Send money" subtitle="Wise-style calculator — live fees, rates & delivery" compact>
        <TrustBadge items={["Best rates", "Secure payment", "Track live"]} />
      </HeroHeader>

      <ScrollView contentContainerStyle={{ padding: spacing.lg, paddingTop: spacing.md, paddingBottom: spacing.xxxl }}>
        <CorridorSelector
          selected={calc.corridorCode}
          onSelect={(code, country, currency) => calc.setCorridor(code, country, currency)}
        />

        <LiveCalculator
          amount={calc.sendAmount}
          onAmountChange={calc.setSendAmount}
          destinationCountry={calc.destinationCountry}
          currency={calc.currency}
          corridorCode={calc.corridorCode}
        />

        <Button title="Continue to recipient" onPress={startSend} variant="gold" />

        {templates.length > 0 && (
          <>
            <Text style={[typography.label, { color: theme.textTertiary, marginTop: spacing.xl, marginBottom: spacing.md }]}>
              Recent templates
            </Text>
            {templates.slice(0, 3).map((tpl) => (
              <TouchableOpacity key={tpl.id} onPress={() => useTemplate(tpl)} activeOpacity={0.8}>
                <FintechCard variant="muted" padding="md" style={{ marginBottom: spacing.sm }}>
                  <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
                    <View style={{ width: 40, height: 40, borderRadius: 20, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
                      <Ionicons name="bookmark" size={18} color={theme.primary} />
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={[typography.bodyBold, { color: theme.text }]}>{tpl.name}</Text>
                      <Text style={[typography.caption, { color: theme.textSecondary }]}>
                        {tpl.beneficiaryName} · R{tpl.amount}
                      </Text>
                    </View>
                    <Ionicons name="chevron-forward" size={18} color={theme.textTertiary} />
                  </View>
                </FintechCard>
              </TouchableOpacity>
            ))}
          </>
        )}

        <Button
          title="View transfer history"
          onPress={() => navigation.navigate("Tabs", { screen: "Activity" } as never)}
          variant="outline"
          style={{ marginTop: spacing.md }}
        />
      </ScrollView>
    </View>
  );
}
