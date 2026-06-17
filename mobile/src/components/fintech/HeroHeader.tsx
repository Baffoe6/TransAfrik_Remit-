import { Ionicons } from "@expo/vector-icons";
import { Text, TouchableOpacity, View } from "react-native";
import { LinearGradient } from "expo-linear-gradient";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useAppTheme, spacing } from "../../theme";
import { typography } from "../../theme/typography";

interface HeroHeaderProps {
  greeting?: string;
  title: string;
  subtitle?: string;
  rightAction?: { icon: keyof typeof Ionicons.glyphMap; onPress: () => void; badge?: string };
  children?: React.ReactNode;
  compact?: boolean;
}

export function HeroHeader({ greeting, title, subtitle, rightAction, children, compact }: HeroHeaderProps) {
  const theme = useAppTheme();
  const insets = useSafeAreaInsets();

  return (
    <LinearGradient
      colors={[...theme.heroGradient]}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
      style={{
        paddingTop: insets.top + (compact ? spacing.md : spacing.lg),
        paddingBottom: compact ? spacing.lg : spacing.xl,
        paddingHorizontal: spacing.lg,
        borderBottomLeftRadius: 28,
        borderBottomRightRadius: 28,
      }}
    >
      <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
        <View style={{ flex: 1 }}>
          {greeting ? (
            <Text style={[typography.bodySm, { color: "rgba(255,255,255,0.8)", marginBottom: 4 }]}>{greeting}</Text>
          ) : null}
          <Text style={[compact ? typography.h1 : typography.displaySm, { color: "#fff" }]}>{title}</Text>
          {subtitle ? (
            <Text style={[typography.bodySm, { color: "rgba(255,255,255,0.75)", marginTop: 6 }]}>{subtitle}</Text>
          ) : null}
        </View>
        {rightAction ? (
          <TouchableOpacity
            onPress={rightAction.onPress}
            style={{
              width: 44,
              height: 44,
              borderRadius: 22,
              backgroundColor: "rgba(255,255,255,0.15)",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Ionicons name={rightAction.icon} size={22} color="#fff" />
            {rightAction.badge ? (
              <View
                style={{
                  position: "absolute",
                  top: 4,
                  right: 4,
                  minWidth: 18,
                  height: 18,
                  borderRadius: 9,
                  backgroundColor: theme.accent,
                  alignItems: "center",
                  justifyContent: "center",
                  paddingHorizontal: 4,
                }}
              >
                <Text style={{ color: "#1B5E3B", fontSize: 10, fontWeight: "800" }}>{rightAction.badge}</Text>
              </View>
            ) : null}
          </TouchableOpacity>
        ) : null}
      </View>
      {children}
    </LinearGradient>
  );
}
