import { useState } from "react";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import {
  AlertBanner,
  Button,
  Input,
  Screen,
} from "../../components";
import { useAuthStore } from "../../store/authStore";
import { authApi } from "../../api/auth";
import { normalizePhone } from "../../utils/phone";
import { isValidEmail, isValidPassword } from "../../utils/validation";
import { COMPLIANCE } from "../../utils/compliance";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "Login">;
type Mode = "mobile" | "email";

export default function LoginScreen({ navigation }: Props) {
  const { login, loading } = useAuthStore();
  const theme = useAppTheme();
  const [mode, setMode] = useState<Mode>("mobile");
  const [mobile, setMobile] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    const identifier = mode === "mobile" ? normalizePhone(mobile) : email.trim();
    if (mode === "mobile" && !mobile.trim()) return setError("Enter your mobile number");
    if (mode === "email" && !isValidEmail(email)) return setError("Enter a valid email");
    if (!isValidPassword(password)) return setError("Password must be at least 8 characters");
    try {
      const result = await login(identifier, password);
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

      <View style={{ flexDirection: "row", marginBottom: spacing.lg, backgroundColor: theme.surfaceMuted, borderRadius: 12, padding: 4 }}>
        {(["mobile", "email"] as Mode[]).map((m) => (
          <TouchableOpacity key={m} onPress={() => setMode(m)} style={{ flex: 1, paddingVertical: 10, borderRadius: 10, backgroundColor: mode === m ? theme.surface : "transparent", alignItems: "center" }}>
            <Text style={{ fontWeight: "600", color: mode === m ? theme.primary : theme.textSecondary }}>{m === "mobile" ? "Mobile" : "Email"}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {error ? <AlertBanner type="error" message={error} /> : null}

      {mode === "mobile" ? (
        <Input label="Mobile number" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" placeholder="+27 82 123 4567" />
      ) : (
        <Input label="Email" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
      )}
      <Input label="Password" value={password} onChangeText={setPassword} secureTextEntry />

      <Button title="Sign in" onPress={submit} loading={loading} />
      <Button title="Sign in with OTP" onPress={() => navigation.navigate("OtpLogin", {})} variant="outline" />
      <Button title="Create account" onPress={() => navigation.navigate("Register")} variant="secondary" />
      <Button title="Forgot password?" onPress={() => navigation.navigate("ForgotPassword")} variant="ghost" />

      <Text style={[typography.caption, { color: theme.textTertiary, textAlign: "center", marginTop: spacing.lg }]}>
        {COMPLIANCE.platformDisclaimer}
      </Text>
    </Screen>
  );
}
