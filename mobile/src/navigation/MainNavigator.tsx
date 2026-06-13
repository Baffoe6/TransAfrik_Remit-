import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import DashboardScreen from "../screens/dashboard/DashboardScreen";
import BeneficiariesScreen from "../screens/beneficiaries/BeneficiariesScreen";
import BeneficiaryFormScreen from "../screens/beneficiaries/BeneficiaryFormScreen";
import TransfersScreen from "../screens/transfers/TransfersScreen";
import CreateTransferScreen from "../screens/transfers/CreateTransferScreen";
import TransferDetailScreen from "../screens/transfers/TransferDetailScreen";
import KycScreen from "../screens/kyc/KycScreen";
import ReferralScreen from "../screens/referral/ReferralScreen";
import ProfileScreen from "../screens/profile/ProfileScreen";
import WalletScreen from "../screens/wallet/WalletScreen";
import { useThemeColors } from "../store/themeStore";
import { useColorScheme, Text } from "react-native";

export type MainTabParamList = {
  Home: undefined;
  Send: undefined;
  Beneficiaries: undefined;
  Profile: undefined;
};

export type RootStackParamList = {
  Tabs: undefined;
  BeneficiaryForm: { id?: number };
  CreateTransfer: undefined;
  TransferDetail: { id: number };
  Kyc: undefined;
  Referral: undefined;
  Wallet: undefined;
};

const Tab = createBottomTabNavigator<MainTabParamList>();
const Stack = createNativeStackNavigator<RootStackParamList>();

function TabIcon({ label, focused }: { label: string; focused: boolean }) {
  const c = useThemeColors(useColorScheme() === "dark");
  return <Text style={{ color: focused ? c.primary : c.textMuted, fontSize: 11 }}>{label}</Text>;
}

function Tabs() {
  const c = useThemeColors(useColorScheme() === "dark");
  return (
    <Tab.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: c.primary },
        headerTintColor: "#fff",
        tabBarStyle: { backgroundColor: c.card, borderTopColor: c.border },
      }}
    >
      <Tab.Screen name="Home" component={DashboardScreen} options={{ title: "Dashboard", tabBarIcon: ({ focused }) => <TabIcon label="Home" focused={focused} /> }} />
      <Tab.Screen name="Send" component={TransfersScreen} options={{ title: "Transfers", tabBarIcon: ({ focused }) => <TabIcon label="Send" focused={focused} /> }} />
      <Tab.Screen name="Beneficiaries" component={BeneficiariesScreen} options={{ title: "Beneficiaries", tabBarIcon: ({ focused }) => <TabIcon label="People" focused={focused} /> }} />
      <Tab.Screen name="Profile" component={ProfileScreen} options={{ title: "Profile", tabBarIcon: ({ focused }) => <TabIcon label="Me" focused={focused} /> }} />
    </Tab.Navigator>
  );
}

export function MainNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen name="Tabs" component={Tabs} options={{ headerShown: false }} />
      <Stack.Screen name="BeneficiaryForm" component={BeneficiaryFormScreen} options={{ title: "Beneficiary" }} />
      <Stack.Screen name="CreateTransfer" component={CreateTransferScreen} options={{ title: "New Transfer" }} />
      <Stack.Screen name="TransferDetail" component={TransferDetailScreen} options={{ title: "Transfer" }} />
      <Stack.Screen name="Kyc" component={KycScreen} options={{ title: "KYC" }} />
      <Stack.Screen name="Referral" component={ReferralScreen} options={{ title: "Referrals" }} />
      <Stack.Screen name="Wallet" component={WalletScreen} options={{ title: "Wallet" }} />
    </Stack.Navigator>
  );
}
