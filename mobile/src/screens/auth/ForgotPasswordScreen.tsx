import { useState } from "react";
import { Text, ScrollView } from "react-native";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AuthStackParamList } from "../../navigation/AuthNavigator";
import { Screen, Title, Muted, Input, Button } from "../../components/ui";
import { authApi } from "../../api/auth";

type Props = NativeStackScreenProps<AuthStackParamList, "ForgotPassword">;

export default function ForgotPasswordScreen({ navigation }: Props) {
  const [mobile, setMobile] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [sent, setSent] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const sendCode = async () => {
    setError("");
    setLoading(true);
    try {
      await authApi.forgotPassword(mobile);
      setSent(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send code");
    } finally {
      setLoading(false);
    }
  };

  const reset = async () => {
    setError("");
    setLoading(true);
    try {
      await authApi.resetPassword(mobile, code, password);
      setDone(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  if (done) {
    return (
      <Screen>
        <Title>Password Reset</Title>
        <Muted>Your password has been updated. You can sign in now.</Muted>
        <Button title="Back to Login" onPress={() => navigation.navigate("Login")} />
      </Screen>
    );
  }

  return (
    <Screen>
      <ScrollView>
        <Title>Reset Password</Title>
        <Muted>We'll send an SMS code to your registered mobile number</Muted>
        {error ? <Text style={{ color: "#DC2626" }}>{error}</Text> : null}
        <Input label="Mobile Number" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" />
        {!sent ? (
          <Button title="Send Reset Code" onPress={sendCode} loading={loading} />
        ) : (
          <>
            <Input label="Verification Code" value={code} onChangeText={setCode} keyboardType="number-pad" />
            <Input label="New Password" value={password} onChangeText={setPassword} secureTextEntry />
            <Button title="Reset Password" onPress={reset} loading={loading} />
          </>
        )}
        <Button title="Back" variant="outline" onPress={() => navigation.goBack()} />
      </ScrollView>
    </Screen>
  );
}
