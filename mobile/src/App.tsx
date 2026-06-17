import { NavigationContainer, DarkTheme, DefaultTheme } from "@react-navigation/native";
import { useColorScheme, ActivityIndicator, View } from "react-native";
import { useEffect } from "react";
import { StatusBar } from "expo-status-bar";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useAuthStore } from "./store/authStore";
import { useOnboardingStore } from "./store/onboardingStore";
import { useSettingsStore } from "./store/settingsStore";
import { AuthNavigator } from "./navigation/AuthNavigator";
import { MainNavigator } from "./navigation/MainNavigator";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { useAppTheme } from "./theme";
import { PhoneVerificationGate } from "./features/auth/PhoneVerificationGate";
import { useVerificationStatus } from "./hooks/useVerificationStatus";
import { notificationService } from "./services/notifications";
import { notificationsApi } from "./api/notifications";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 2, refetchOnReconnect: true, refetchOnWindowFocus: true },
  },
});

function RootNav() {
  const scheme = useColorScheme();
  const theme = useAppTheme();
  const { user, initialized, bootstrap } = useAuthStore();
  const onboardingComplete = useOnboardingStore((s) => s.complete);
  const loadOnboarding = useOnboardingStore((s) => s.load);
  const loadSettings = useSettingsStore((s) => s.load);
  const { identityVerified, isLoading: verificationLoading, sync } = useVerificationStatus();

  useEffect(() => {
    bootstrap();
    loadOnboarding();
    loadSettings();
  }, [bootstrap, loadOnboarding, loadSettings]);

  useEffect(() => {
    if (user) void sync();
  }, [user?.id, user?.phone_verified]);

  useEffect(() => {
    if (!user) return;
    (async () => {
      const token = await notificationService.registerForPush();
      if (token) {
        try {
          await notificationsApi.registerPushToken(token);
        } catch {
          /* non-blocking */
        }
      }
    })();
  }, [user?.id]);

  if (!initialized || onboardingComplete === null) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: theme.primaryDark }}>
        <ActivityIndicator size="large" color="#C9A227" />
      </View>
    );
  }

  const navTheme = scheme === "dark" ? DarkTheme : DefaultTheme;
  navTheme.colors.primary = theme.primary;

  const needsPhoneVerify = user && !verificationLoading && !identityVerified;
  return (
    <NavigationContainer theme={navTheme}>
      <StatusBar style={scheme === "dark" ? "light" : "dark"} />
      {!user ? (
        <AuthNavigator showOnboarding={!onboardingComplete} />
      ) : needsPhoneVerify ? (
        <PhoneVerificationGate />
      ) : (
        <MainNavigator />
      )}
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <RootNav />
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
