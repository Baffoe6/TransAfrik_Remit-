import * as LocalAuthentication from "expo-local-authentication";

/** Future-ready biometric login wrapper (Face ID / fingerprint). */
export const biometricService = {
  async isAvailable() {
    const compatible = await LocalAuthentication.hasHardwareAsync();
    const enrolled = await LocalAuthentication.isEnrolledAsync();
    return compatible && enrolled;
  },
  async authenticate(reason = "Unlock TransAfrik Remit") {
    const result = await LocalAuthentication.authenticateAsync({
      promptMessage: reason,
      fallbackLabel: "Use passcode",
    });
    return result.success;
  },
};
