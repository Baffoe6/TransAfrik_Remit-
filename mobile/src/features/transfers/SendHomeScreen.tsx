import { View, Text } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useNavigation } from "@react-navigation/native";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { Button, Caption, H1, Screen } from "../../components";
import { spacing } from "../../theme/spacing";
import { typography } from "../../theme/typography";
import { RootStackParamList } from "../../navigation/MainNavigator";

export default function SendHomeScreen() {
  const navigation = useNavigation<NativeStackNavigationProp<RootStackParamList>>();

  return (
    <Screen scroll={false} padded={false}>
      <LinearGradient colors={["#1B5E3B", "#0D3D24"]} style={{ padding: spacing.xxl, paddingTop: spacing.xxxl }}>
        <H1 light>Send Money</H1>
        <Caption><Text style={{ color: "rgba(255,255,255,0.85)" }}>Fast, secure transfers to Africa</Text></Caption>
      </LinearGradient>
      <View style={{ padding: spacing.xl }}>
        <Text style={[typography.body, { marginBottom: spacing.lg, color: "#374151" }]}>
          Send from South Africa in 5 simple steps. Pay at retail, track in real time.
        </Text>
        <Button title="Start New Transfer" onPress={() => navigation.navigate("SendFlow")} variant="gold" />
        <Button title="View Activity" onPress={() => navigation.navigate("Tabs", { screen: "Activity" })} variant="outline" />
      </View>
    </Screen>
  );
}
