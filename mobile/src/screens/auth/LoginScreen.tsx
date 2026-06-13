import { useState } from "react";
import { Text, ScrollView } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AuthStackParamList } from "../../navigation/AuthNavigator";
import { Screen, Title, Muted, Input, Button } from "../../components/ui";
import { useAuthStore } from "../../store/authStore";
import { authApi } from "../../api/auth";

type Props = NativeStackScreenProps<AuthStackParamList, "Login">;

export default function LoginScreen({ navigation }: Props) {
  const { login, loading } = useAuthStore();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    try {
      const result = await login(identifier, password);
      if (result.stepUp && result.stepUpMobile) {
        await authApi.sendOtp(result.stepUpMobile, "sms", "step_up");
        navigation.navigate("OtpLogin");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
    }
  };

  return (
    <Screen>
      <ScrollView>
        <Title>TransAfrik Remit</Title>
        <Muted>Sign in with mobile number or email</Muted>
        {error ? <Text style={{ color: "#DC2626", marginVertical: 8 }}>{error}</Text> : null}
        <Input label="Mobile or Email" value={identifier} onChangeText={setIdentifier} autoCapitalize="none" />
        <Input label="Password" value={password} onChangeText={setPassword} secureTextEntry />
        <Button title="Sign In" onPress={submit} loading={loading} />
        <Button title="OTP Login" variant="outline" onPress={() => navigation.navigate("OtpLogin")} />
        <Button title="Create Account" variant="outline" onPress={() => navigation.navigate("Register")} />
        <Button title="Forgot Password?" variant="outline" onPress={() => navigation.navigate("ForgotPassword")} />
      </ScrollView>
    </Screen>
  );
}
