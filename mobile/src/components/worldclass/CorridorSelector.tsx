import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { CORRIDORS } from "../../utils/constants";
import { useAppTheme, radius, spacing } from "../../theme";
import { typography } from "../../theme/typography";
import { hapticSelection } from "../../services/haptics";

interface CorridorSelectorProps {
  selected: string;
  onSelect: (code: string, country: string, currency: string) => void;
  compact?: boolean;
}

export function CorridorSelector({ selected, onSelect, compact }: CorridorSelectorProps) {
  const theme = useAppTheme();
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: spacing.sm, paddingVertical: spacing.xs }}>
      {CORRIDORS.map((c) => {
        const active = selected === c.code;
        return (
          <TouchableOpacity
            key={c.code}
            onPress={() => {
              hapticSelection();
              onSelect(c.code, c.country, c.currency);
            }}
            activeOpacity={0.8}
            style={{
              paddingHorizontal: compact ? spacing.md : spacing.lg,
              paddingVertical: compact ? spacing.sm : spacing.md,
              borderRadius: radius.full,
              backgroundColor: active ? theme.primary : theme.surfaceMuted,
              borderWidth: active ? 0 : 1,
              borderColor: theme.border,
              flexDirection: "row",
              alignItems: "center",
              gap: 8,
            }}
          >
            <Text style={{ fontSize: compact ? 18 : 22 }}>{c.flag}</Text>
            <View>
              <Text style={[typography.bodySm, { color: active ? "#fff" : theme.text, fontWeight: "600" }]}>
                ZA → {c.name}
              </Text>
              {!compact && (
                <Text style={[typography.caption, { color: active ? "rgba(255,255,255,0.8)" : theme.textSecondary }]}>
                  {c.currency} · {c.eta}
                </Text>
              )}
            </View>
          </TouchableOpacity>
        );
      })}
    </ScrollView>
  );
}
