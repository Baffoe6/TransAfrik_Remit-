import VerifyPhoneScreen from "./VerifyPhoneScreen";
import { View } from "react-native";
import { useAppTheme } from "../../theme";

/** Standalone gate when user is logged in but phone is not verified */
export function PhoneVerificationGate() {
  const theme = useAppTheme();
  return (
    <View style={{ flex: 1, backgroundColor: theme.bg }}>
      <VerifyPhoneScreen />
    </View>
  );
}
