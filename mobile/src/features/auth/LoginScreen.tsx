import { useState } from "react";
import { Text, TouchableOpacity, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Button, Input, PinInput, Screen } from "../../components";
import { useAuthStore } from "../../store/authStore";
import { authApi } from "../../api/auth";
import { normalizePhone } from "../../utils/phone";
import { isValidEmail, isValidMobile, isValidPassword, isValidPin } from "../../utils/validation";
import { COMPLIANCE } from "../../utils/compliance";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "Login">;

export default function LoginScreen({ navigation }: Props) {
  const { loginPin, login, loading } = useAuthStore();
  const theme = useAppTheme();
  const [showEmailLogin, setShowEmailLogin] = useState(false);
  const [mobile, setMobile] = useState("");
  const [pin, setPin] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submitPin = async () => {
    setError("");
    if (!isValidMobile(mobile)) return setError("Enter a valid mobile number");
    if (!isValidPin(pin)) return setError("Enter your 4-digit PIN");
    try {
      const result = await loginPin(normalizePhone(mobile), pin);
      if (result.stepUp && result.stepUpMobile) {
        await authApi.sendOtp(result.stepUpMobile, "sms", "step_up");
        navigation.navigate("OtpLogin", { mobile: result.stepUpMobile });
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
    }
  };

  const submitEmail = async () => {
    setError("");
    if (!isValidEmail(email)) return setError("Enter a valid email");
    if (!isValidPassword(password)) return setError("Password must be at least 8 characters");
    try {
      const result = await login(email.trim(), password);
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
        <Text style={[typography.h1, { color: "#fff" }]}>TransAfrik Remit</Text>
        <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: 13 }}>Send money across Africa — securely</Text>
      </LinearGradient>

      {error ? <AlertBanner type="error" message={error} /> : null}

      {!showEmailLogin ? (
        <>
          <Input label="Mobile number" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" placeholder="+27 82 123 4567" />
          <PinInput label="4-digit PIN" value={pin} onChange={setPin} length={4} />
          <Button title="Sign in" onPress={submitPin} loading={loading} />
          <TouchableOpacity onPress={() => setShowEmailLogin(true)} style={{ alignItems: "center", marginVertical: spacing.md }}>
            <Text style={{ color: theme.primary, fontWeight: "600" }}>Sign in with email</Text>
          </TouchableOpacity>
        </>
      ) : (
        <>
          <Input label="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
          <Input label="Password" value={password} onChangeText={setPassword} secureTextEntry />
          <Button title="Sign in with email" onPress={submitEmail} loading={loading} />
          <TouchableOpacity onPress={() => setShowEmailLogin(false)} style={{ alignItems: "center", marginVertical: spacing.md }}>
            <Text style={{ color: theme.primary, fontWeight: "600" }}>Use mobile number + PIN</Text>
          </TouchableOpacity>
        </>
      )}

      <Button title="Sign in with OTP" onPress={() => navigation.navigate("OtpLogin", {})} variant="outline" />
      <Button title="Create account" onPress={() => navigation.navigate("Register")} variant="secondary" />
      <Button title="Forgot PIN?" onPress={() => navigation.navigate("ForgotPassword")} variant="ghost" />

      <Text style={[typography.caption, { color: theme.textTertiary, textAlign: "center", marginTop: spacing.lg }]}>
        {COMPLIANCE.platformDisclaimer}
      </Text>
    </Screen>
  );
}
