import { useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Button, Caption, H1, Input, PinInput, Screen } from "../../components";
import { useAuthStore } from "../../store/authStore";
import { authApi } from "../../api/auth";
import { normalizePhone } from "../../utils/phone";
import { isValidEmail, isValidPin } from "../../utils/validation";
import { spacing } from "../../theme/spacing";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "Login">;
type Mode = "pin" | "email";

export default function LoginScreen({ navigation }: Props) {
  const { login, loading } = useAuthStore();
  const [mode, setMode] = useState<Mode>("pin");
  const [mobile, setMobile] = useState("");
  const [pin, setPin] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    const identifier = mode === "pin" ? normalizePhone(mobile) : email.trim();
    const secret = mode === "pin" ? pin : password;
    if (mode === "pin" && !isValidPin(pin)) {
      setError("Enter your 4–6 digit PIN");
      return;
    }
    try {
      const result = await login(identifier, secret);
      if (result.stepUp && result.stepUpMobile) {
        await authApi.sendOtp(result.stepUpMobile, "sms", "step_up");
        navigation.navigate("OtpLogin", { mobile: result.stepUpMobile });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
    }
  };

  return (
    <Screen scroll safe>
      <LinearGradient colors={["#1B5E3B", "#0D3D24"]} style={{ margin: -16, padding: spacing.xl, paddingTop: spacing.xxxl, marginBottom: spacing.xl, borderBottomLeftRadius: 24, borderBottomRightRadius: 24 }}>
        <H1 light>TransAfrik Remit</H1>
        <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: 13 }}>Secure money transfers to Africa</Text>
      </LinearGradient>

      <View style={{ flexDirection: "row", marginBottom: spacing.lg, backgroundColor: "#F3F4F6", borderRadius: 12, padding: 4 }}>
        {(["pin", "email"] as Mode[]).map((m) => (
          <TouchableOpacity key={m} onPress={() => setMode(m)} style={{ flex: 1, paddingVertical: 10, borderRadius: 10, backgroundColor: mode === m ? "#fff" : "transparent", alignItems: "center" }}>
            <Text style={{ fontWeight: "600", color: mode === m ? "#1B5E3B" : "#6B7280" }}>{m === "pin" ? "Mobile + PIN" : "Email + Password"}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {error ? <AlertBanner type="error" message={error} /> : null}

      {mode === "pin" ? (
        <>
          <Input label="Mobile Number" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" placeholder="+27 82 123 4567" />
          <PinInput label="PIN" value={pin} onChange={setPin} length={4} />
        </>
      ) : (
        <>
          <Input label="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
          <Input label="Password" value={password} onChangeText={setPassword} secureTextEntry />
        </>
      )}

      <Button title="Sign In" onPress={submit} loading={loading} />
      <Button title="Sign in with OTP" onPress={() => navigation.navigate("OtpLogin", {})} variant="outline" />
      <Button title="Create Account" onPress={() => navigation.navigate("Register")} variant="secondary" />
      <Button title="Forgot PIN / Password?" onPress={() => navigation.navigate("ForgotPassword")} variant="ghost" />
    </Screen>
  );
}
