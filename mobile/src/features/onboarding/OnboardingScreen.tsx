import { useRef, useState } from "react";
import { Dimensions, FlatList, Text, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Button } from "../../components";
import { useAppTheme } from "../../theme";
import { spacing } from "../../theme/spacing";
import { typography } from "../../theme/typography";
import { useOnboardingStore } from "../../store/onboardingStore";
import { AuthStackParamList } from "../../navigation/AuthNavigator";

const { width } = Dimensions.get("window");

const SLIDES = [
  { title: "Send money home", body: "Fast, secure remittances from South Africa to Africa.", emoji: "🌍" },
  { title: "Pay at retail", body: "Use Pay@, EasyPay, or EFT — no bank account needed.", emoji: "🏪" },
  { title: "Track every step", body: "Real-time transfer tracking with trusted partners.", emoji: "🔒" },
];

type Props = NativeStackScreenProps<AuthStackParamList, "Onboarding">;

export default function OnboardingScreen({ navigation }: Props) {
  const theme = useAppTheme();
  const markComplete = useOnboardingStore((s) => s.markComplete);
  const [index, setIndex] = useState(0);
  const ref = useRef<FlatList>(null);

  const finish = async () => {
    await markComplete();
    navigation.replace("Login");
  };

  return (
    <LinearGradient colors={[theme.primaryDark, theme.primary]} style={{ flex: 1 }}>
      <FlatList
        ref={ref}
        data={SLIDES}
        horizontal
        pagingEnabled
        showsHorizontalScrollIndicator={false}
        onMomentumScrollEnd={(e) => setIndex(Math.round(e.nativeEvent.contentOffset.x / width))}
        keyExtractor={(_, i) => String(i)}
        renderItem={({ item }) => (
          <View style={{ width, flex: 1, justifyContent: "center", alignItems: "center", padding: spacing.xxl }}>
            <Text style={{ fontSize: 72, marginBottom: spacing.xl }}>{item.emoji}</Text>
            <Text style={[typography.display, { color: "#fff", textAlign: "center", marginBottom: spacing.md }]}>{item.title}</Text>
            <Text style={[typography.body, { color: "rgba(255,255,255,0.85)", textAlign: "center" }]}>{item.body}</Text>
          </View>
        )}
      />
      <View style={{ padding: spacing.xl, paddingBottom: spacing.xxxl }}>
        <View style={{ flexDirection: "row", justifyContent: "center", gap: 8, marginBottom: spacing.lg }}>
          {SLIDES.map((_, i) => (
            <View key={i} style={{ width: i === index ? 24 : 8, height: 8, borderRadius: 4, backgroundColor: i === index ? theme.accent : "rgba(255,255,255,0.4)" }} />
          ))}
        </View>
        {index < SLIDES.length - 1 ? (
          <Button title="Next" onPress={() => ref.current?.scrollToIndex({ index: index + 1 })} variant="gold" />
        ) : (
          <Button title="Get Started" onPress={finish} variant="gold" />
        )}
        <Button title="Skip" onPress={finish} variant="ghost" style={{ marginTop: spacing.sm }} />
      </View>
    </LinearGradient>
  );
}
