import { createNativeStackNavigator } from "@react-navigation/native-stack";
import OnboardingScreen from "../features/onboarding/OnboardingScreen";
import LoginScreen from "../features/auth/LoginScreen";
import RegisterScreen from "../features/auth/RegisterScreen";
import ForgotPasswordScreen from "../features/auth/ForgotPasswordScreen";
import OtpLoginScreen from "../features/auth/OtpLoginScreen";
import VerifyPhoneScreen from "../features/auth/VerifyPhoneScreen";

export type AuthStackParamList = {
  Onboarding: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
  OtpLogin: { mobile?: string };
  VerifyPhone: undefined;
};

const Stack = createNativeStackNavigator<AuthStackParamList>();

export function AuthNavigator({ showOnboarding }: { showOnboarding: boolean }) {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }} initialRouteName={showOnboarding ? "Onboarding" : "Login"}>
      <Stack.Screen name="Onboarding" component={OnboardingScreen} />
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
      <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
      <Stack.Screen name="OtpLogin" component={OtpLoginScreen} />
      <Stack.Screen name="VerifyPhone" component={VerifyPhoneScreen} />
    </Stack.Navigator>
  );
}
