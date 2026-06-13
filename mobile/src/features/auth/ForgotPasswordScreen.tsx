import { useState } from "react";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Body, Button, Input, PinInput, Screen, H2 } from "../../components";
import { authApi } from "../../api/auth";
import { normalizePhone } from "../../utils/phone";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

type Props = NativeStackScreenProps<AuthStackParamList, "ForgotPassword">;

export default function ForgotPasswordScreen({ navigation }: Props) {
  const [mobile, setMobile] = useState("");
  const [code, setCode] = useState("");
  const [newPin, setNewPin] = useState("");
  const [step, setStep] = useState<"request" | "reset">("request");
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const request = async () => {
    setLoading(true);
    setError("");
    try {
      await authApi.forgotPassword(normalizePhone(mobile));
      setMsg("If your number is registered, an SMS code has been sent.");
      setStep("reset");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  const reset = async () => {
    setLoading(true);
    setError("");
    try {
      await authApi.resetPassword(normalizePhone(mobile), code, newPin);
      setMsg("PIN updated. You can sign in now.");
      navigation.navigate("Login");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Reset failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen scroll>
      <H2>Reset PIN</H2>
      <Body muted>We'll send an SMS code to your registered mobile number</Body>
      {error ? <AlertBanner type="error" message={error} /> : null}
      {msg ? <AlertBanner type="success" message={msg} /> : null}
      <Input label="Mobile Number" value={mobile} onChangeText={setMobile} keyboardType="phone-pad" />
      {step === "reset" && (
        <>
          <Input label="SMS Code" value={code} onChangeText={setCode} keyboardType="number-pad" />
          <PinInput label="New PIN" value={newPin} onChange={setNewPin} />
        </>
      )}
      <Button title={step === "request" ? "Send Code" : "Reset PIN"} onPress={step === "request" ? request : reset} loading={loading} />
      <Button title="Back to Login" onPress={() => navigation.goBack()} variant="ghost" />
    </Screen>
  );
}
