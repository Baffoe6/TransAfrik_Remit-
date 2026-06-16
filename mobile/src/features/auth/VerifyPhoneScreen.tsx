import { useEffect, useState } from "react";
import { Text, TouchableOpacity, View } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { AlertBanner, Button, Input, Screen } from "../../components";
import { authApi } from "../../api/auth";
import { profileApi } from "../../api/dashboard";
import { useAuthStore } from "../../store/authStore";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

const COOLDOWN_SEC = 60;

type Props = Partial<NativeStackScreenProps<AuthStackParamList, "VerifyPhone">>;

export default function VerifyPhoneScreen({ navigation }: Props = {}) {
  const theme = useAppTheme();
  const refreshUser = useAuthStore((s) => s.refreshUser);
  const user = useAuthStore((s) => s.user);
  const [code, setCode] = useState("");
  const [channel, setChannel] = useState<"sms" | "whatsapp">("sms");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);

  const mobile = user?.mobile_number ?? "";

  useEffect(() => {
    if (cooldown <= 0) return;
    const t = setTimeout(() => setCooldown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [cooldown]);

  const send = async () => {
    if (!mobile || cooldown > 0) return;
    setError("");
    setLoading(true);
    try {
      await authApi.sendOtp(mobile, channel, "verify_phone");
      setSent(true);
      setCooldown(COOLDOWN_SEC);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not send OTP");
    } finally {
      setLoading(false);
    }
  };

  const verify = async () => {
    setError("");
    setLoading(true);
    try {
      await authApi.verifyPhone(code, channel);
      await profileApi.get(); // refresh profile state
      await refreshUser();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Invalid or expired code");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen scroll>
      <View style={{ alignItems: "center", marginBottom: spacing.xl }}>
        <View style={{ width: 64, height: 64, borderRadius: 32, backgroundColor: theme.primaryMuted, alignItems: "center", justifyContent: "center" }}>
          <Ionicons name="phone-portrait-outline" size={32} color={theme.primary} />
        </View>
        <Text style={[typography.h1, { color: theme.text, marginTop: spacing.md }]}>Verify your mobile</Text>
        <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center", marginTop: spacing.sm }]}>
          We sent a one-time code to {mobile || "your number"}. This is required before you can send money.
        </Text>
      </View>

      {error ? <AlertBanner type="error" message={error} /> : null}
      {sent && !error ? <AlertBanner type="info" message="OTP sent. Check your SMS or WhatsApp." /> : null}

      <View style={{ flexDirection: "row", gap: spacing.sm, marginBottom: spacing.md }}>
        {(["sms", "whatsapp"] as const).map((ch) => (
          <TouchableOpacity
            key={ch}
            onPress={() => setChannel(ch)}
            style={{
              flex: 1,
              padding: spacing.sm,
              borderRadius: 8,
              backgroundColor: channel === ch ? theme.primary : theme.surfaceMuted,
              alignItems: "center",
            }}
          >
            <Text style={{ color: channel === ch ? "#fff" : theme.text, fontWeight: "600", textTransform: "uppercase" }}>{ch}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Button title={cooldown > 0 ? `Resend in ${cooldown}s` : sent ? "Resend OTP" : "Send OTP"} onPress={send} variant="outline" loading={loading} disabled={cooldown > 0} />
      <Input label="Enter OTP code" value={code} onChangeText={setCode} keyboardType="number-pad" maxLength={8} />
      <Button title="Verify mobile number" onPress={verify} loading={loading} disabled={code.length < 4} />
      <Button title="Change mobile number" onPress={() => navigation?.navigate?.("EditProfile" as never)} variant="ghost" />
    </Screen>
  );
}
