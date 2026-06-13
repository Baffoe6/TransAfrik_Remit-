import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { Text } from "react-native";
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
import { useAppTheme } from "../theme";
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

const TAB_ICONS: Record<keyof MainTabParamList, string> = {
  Home: "🏠",
  Send: "💸",
  Beneficiaries: "👥",
  Activity: "📋",
  Profile: "👤",
};

function TabBarIcon({ name, focused }: { name: keyof MainTabParamList; focused: boolean }) {
  const theme = useAppTheme();
  return (
    <Text style={{ fontSize: 20, opacity: focused ? 1 : 0.5 }}>
      {TAB_ICONS[name]}
    </Text>
  );
}

function Tabs() {
  const theme = useAppTheme();
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerStyle: { backgroundColor: theme.primaryDark },
        headerTintColor: "#fff",
        headerTitleStyle: { fontWeight: "600" },
        tabBarStyle: { backgroundColor: theme.tabBar, borderTopColor: theme.border, height: 60, paddingBottom: 8 },
        tabBarActiveTintColor: theme.primary,
        tabBarInactiveTintColor: theme.textSecondary,
        tabBarIcon: ({ focused }) => <TabBarIcon name={route.name as keyof MainTabParamList} focused={focused} />,
      })}
    >
      <Tab.Screen name="Home" component={HomeScreen} options={{ title: "Home" }} />
      <Tab.Screen name="Send" component={SendHomeScreen} options={{ title: "Send" }} />
      <Tab.Screen name="Beneficiaries" component={BeneficiariesScreen} options={{ title: "Beneficiaries" }} />
      <Tab.Screen name="Activity" component={ActivityScreen} options={{ title: "Activity" }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: "Profile" }} />
    </Tab.Navigator>
  );
}

export function MainNavigator() {
  const theme = useAppTheme();
  return (
    <Stack.Navigator screenOptions={{ headerStyle: { backgroundColor: theme.primaryDark }, headerTintColor: "#fff" }}>
      <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
      <Stack.Screen name="SendFlow" component={SendFlowScreen} options={{ title: "Send Money" }} />
      <Stack.Screen name="PaymentSuccess" component={PaymentSuccessScreen} options={{ title: "Pay Now" }} />
      <Stack.Screen name="TransferTracking" component={TransferTrackingScreen} options={{ title: "Track Transfer" }} />
      <Stack.Screen name="Receipt" component={ReceiptScreen} options={{ title: "Receipt" }} />
      <Stack.Screen name="BeneficiaryForm" component={BeneficiaryFormScreen} options={{ title: "Beneficiary" }} />
      <Stack.Screen name="Kyc" component={KycScreen} options={{ title: "KYC Verification" }} />
      <Stack.Screen name="Referral" component={ReferralScreen} options={{ title: "Refer & Earn" }} />
      <Stack.Screen name="Notifications" component={NotificationsScreen} options={{ title: "Notifications" }} />
      <Stack.Screen name="Support" component={SupportScreen} options={{ title: "Support" }} />
      <Stack.Screen name="EditProfile" component={EditProfileScreen} options={{ title: "Edit Profile" }} />
      <Stack.Screen name="Security" component={SecurityScreen} options={{ title: "Security" }} />
      <Stack.Screen name="EnableBiometrics" component={EnableBiometricsScreen} options={{ title: "Biometrics" }} />
    </Stack.Navigator>
  );
}
