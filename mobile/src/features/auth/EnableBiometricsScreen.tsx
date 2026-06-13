import { Button, Body, H2, Screen } from "../../components";
import { biometricService } from "../../services/biometric";
import { useSettingsStore } from "../../store/settingsStore";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { RootStackParamList } from "../../navigation/MainNavigator";
import { useState } from "react";
import { AlertBanner } from "../../components";

type Props = NativeStackScreenProps<RootStackParamList, "EnableBiometrics">;

export default function EnableBiometricsScreen({ navigation }: Props) {
  const setBiometric = useSettingsStore((s) => s.setBiometric);
  const [error, setError] = useState("");

  const enable = async () => {
    const available = await biometricService.isAvailable();
    if (!available) {
      setError("Biometrics not available on this device");
      return;
    }
    const ok = await biometricService.authenticate("Enable biometric unlock for TransAfrik");
    if (ok) {
      await setBiometric(true);
      navigation.goBack();
    }
  };

  return (
    <Screen>
      <H2>Enable Biometrics</H2>
      <Body muted>Use fingerprint or Face ID for quick, secure access. PIN remains as fallback.</Body>
      {error ? <AlertBanner type="error" message={error} /> : null}
      <Button title="Enable Biometrics" onPress={enable} />
      <Button title="Skip for now" onPress={() => navigation.goBack()} variant="ghost" />
    </Screen>
  );
}
