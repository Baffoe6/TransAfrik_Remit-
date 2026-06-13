import { Body, Button, Caption, Card, H2, Screen } from "../../components";
import { useSettingsStore } from "../../store/settingsStore";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../../navigation/MainNavigator";

type Props = NativeStackScreenProps<RootStackParamList, "Security">;

export default function SecurityScreen({ navigation }: Props) {
  const biometricEnabled = useSettingsStore((s) => s.biometricEnabled);

  return (
    <Screen scroll>
      <H2>Security Settings</H2>
      <Card>
        <Caption>Biometric Unlock</Caption>
        <Body>{biometricEnabled ? "Enabled" : "Not enabled"}</Body>
        <Button title="Configure Biometrics" onPress={() => navigation.navigate("EnableBiometrics")} variant="outline" />
      </Card>
      <Card>
        <Caption>PIN Fallback</Caption>
        <Body>Use your 4-digit PIN if biometrics unavailable</Body>
      </Card>
      <Card>
        <Caption>Active Sessions</Caption>
        <Body>Device session management — coming soon</Body>
      </Card>
      <Card>
        <Caption>Trusted Devices</Caption>
        <Body>View and manage trusted devices — coming soon</Body>
      </Card>
      <Button title="Change PIN / Password" onPress={() => {}} variant="outline" />
    </Screen>
  );
}
