import { Ionicons } from "@expo/vector-icons";
import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { useAppTheme, radius, spacing } from "../../theme";
import { typography } from "../../theme/typography";

export interface QuickAction {
  id: string;
  label: string;
  icon: keyof typeof Ionicons.glyphMap;
  onPress: () => void;
  accent?: boolean;
}

export function QuickActionGrid({ actions }: { actions: QuickAction[] }) {
  const theme = useAppTheme();
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: spacing.sm, paddingVertical: spacing.xs }}>
      {actions.map((a) => (
        <TouchableOpacity
          key={a.id}
          onPress={a.onPress}
          activeOpacity={0.8}
          style={{
            alignItems: "center",
            minWidth: 76,
            paddingVertical: spacing.md,
            paddingHorizontal: spacing.sm,
          }}
        >
          <View
            style={{
              width: 56,
              height: 56,
              borderRadius: radius.lg,
              backgroundColor: a.accent ? theme.accent : theme.primaryMuted,
              alignItems: "center",
              justifyContent: "center",
              marginBottom: spacing.sm,
            }}
          >
            <Ionicons name={a.icon} size={26} color={a.accent ? theme.charcoal900 : theme.primary} />
          </View>
          <Text style={[typography.caption, { color: theme.text, fontWeight: "600", textAlign: "center" }]} numberOfLines={2}>
            {a.label}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}
