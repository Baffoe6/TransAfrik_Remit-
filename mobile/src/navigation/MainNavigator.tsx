import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Platform, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import HomeScreen from "../features/dashboard/HomeScreen";
import SendHomeScreen from "../features/transfers/SendHomeScreen";
import BeneficiariesScreen from "../features/beneficiaries/BeneficiariesScreen";
import ActivityScreen from "../features/activity/ActivityScreen";
import ProfileScreen from "../features/profile/ProfileScreen";
import BeneficiaryFormScreen from "../features/beneficiaries/BeneficiaryFormScreen";
import SendFlowScreen from "../features/transfers/SendFlowScreen";
import PaymentSuccessScreen from "../features/transfers/PaymentSuccessScreen";
import TransferTrackingScreen from "../features/transfers/TransferTrackingScreen";
import ReceiptScreen from "../features/transfers/ReceiptScreen";
import KycScreen from "../features/kyc/KycScreen";
import ReferralScreen from "../features/referrals/ReferralScreen";
import NotificationsScreen from "../features/notifications/NotificationsScreen";
import SupportScreen from "../features/support/SupportScreen";
import EditProfileScreen from "../features/profile/EditProfileScreen";
import SecurityScreen from "../features/profile/SecurityScreen";
import EnableBiometricsScreen from "../features/auth/EnableBiometricsScreen";
import { useAppTheme, tokens } from "../theme";
import { typography } from "../theme/typography";
import type { PaymentReference } from "../api/payments";

export type MainTabParamList = {
  Home: undefined;
  Send: undefined;
  Beneficiaries: undefined;
  Activity: undefined;
  Profile: undefined;
};

export type RootStackParamList = {
  Tabs: { screen?: keyof MainTabParamList } | undefined;
  SendFlow: undefined;
  PaymentSuccess: { transferId: number; reference: PaymentReference };
  TransferTracking: { id: number };
  Receipt: { id: number };
  BeneficiaryForm: { id?: number };
  Kyc: undefined;
  Referral: undefined;
  Notifications: undefined;
  Support: undefined;
  EditProfile: undefined;
  Security: undefined;
  EnableBiometrics: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();
const Stack = createNativeStackNavigator<RootStackParamList>();

const TAB_ICONS: Record<keyof MainTabParamList, { active: keyof typeof Ionicons.glyphMap; inactive: keyof typeof Ionicons.glyphMap }> = {
  Home: { active: "home", inactive: "home-outline" },
  Send: { active: "arrow-up-circle", inactive: "arrow-up-circle-outline" },
  Beneficiaries: { active: "people", inactive: "people-outline" },
  Activity: { active: "time", inactive: "time-outline" },
  Profile: { active: "person", inactive: "person-outline" },
};

function Tabs() {
  const theme = useAppTheme();
  const insets = useSafeAreaInsets();

  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarStyle: {
          backgroundColor: theme.tabBar,
          borderTopColor: theme.tabBarBorder,
          borderTopWidth: 1,
          height: tokens.tabBarHeight + insets.bottom,
          paddingBottom: insets.bottom + 4,
          paddingTop: 8,
          ...Platform.select({
            ios: { shadowColor: "#000", shadowOffset: { width: 0, height: -2 }, shadowOpacity: 0.06, shadowRadius: 8 },
            android: { elevation: 8 },
          }),
        },
        tabBarActiveTintColor: theme.primary,
        tabBarInactiveTintColor: theme.textTertiary,
        tabBarLabelStyle: typography.tab,
        tabBarIcon: ({ focused, color }) => {
          const icons = TAB_ICONS[route.name as keyof MainTabParamList];
          return (
            <View style={focused ? { backgroundColor: theme.primaryMuted, borderRadius: 12, padding: 4 } : undefined}>
              <Ionicons name={focused ? icons.active : icons.inactive} size={22} color={color} />
            </View>
          );
        },
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: "Home" }} />
      <Tab.Screen name="Send" component={SendHomeScreen} options={{ title: "Send" }} />
      <Tab.Screen name="Beneficiaries" component={BeneficiariesScreen} options={{ title: "Recipients" }} />
      <Tab.Screen name="Activity" component={ActivityScreen} options={{ title: "Activity" }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: "Profile" }} />
    </Tab.Navigator>
  );
}

export function MainNavigator() {
  const theme = useAppTheme();
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: theme.bgElevated },
        headerTintColor: theme.text,
        headerTitleStyle: { ...typography.h3, color: theme.text },
        headerShadowVisible: false,
        contentStyle: { backgroundColor: theme.bg },
        animation: "slide_from_right",
      }}
    >
      <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
      <Stack.Screen name="SendFlow" component={SendFlowScreen} options={{ title: "Send money" }} />
      <Stack.Screen name="PaymentSuccess" component={PaymentSuccessScreen} options={{ title: "Pay now", headerBackVisible: false }} />
      <Stack.Screen name="TransferTracking" component={TransferTrackingScreen} options={{ title: "Track transfer" }} />
      <Stack.Screen name="Receipt" component={ReceiptScreen} options={{ title: "Receipt" }} />
      <Stack.Screen name="BeneficiaryForm" component={BeneficiaryFormScreen} options={{ title: "Recipient" }} />
      <Stack.Screen name="Kyc" component={KycScreen} options={{ title: "Verify identity" }} />
      <Stack.Screen name="Referral" component={ReferralScreen} options={{ title: "Refer & earn" }} />
      <Stack.Screen name="Notifications" component={NotificationsScreen} options={{ title: "Notifications" }} />
      <Stack.Screen name="Support" component={SupportScreen} options={{ title: "Help" }} />
      <Stack.Screen name="EditProfile" component={EditProfileScreen} options={{ title: "Personal details" }} />
      <Stack.Screen name="Security" component={SecurityScreen} options={{ title: "Security" }} />
      <Stack.Screen name="EnableBiometrics" component={EnableBiometricsScreen} options={{ title: "Biometrics" }} />
    </Stack.Navigator>
  );
}
