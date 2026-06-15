import { ScrollView, Text, TouchableOpacity, View } from "react-native";
import { Avatar } from "../fintech";
import { useAppTheme, radius, spacing } from "../../theme";
import { typography } from "../../theme/typography";
import { CORRIDORS } from "../../utils/constants";
import type { Beneficiary } from "../../types";
import { hapticLight } from "../../services/haptics";

interface FavoriteRecipientsCarouselProps {
  beneficiaries: Beneficiary[];
  favoriteIds: number[];
  onSelect: (b: Beneficiary) => void;
  onAdd: () => void;
}

export function FavoriteRecipientsCarousel({ beneficiaries, favoriteIds, onSelect, onAdd }: FavoriteRecipientsCarouselProps) {
  const theme = useAppTheme();
  const favorites = beneficiaries.filter((b) => favoriteIds.includes(b.id));
  const recent = favorites.length ? favorites : beneficiaries.slice(0, 5);

  if (!recent.length) return null;

  return (
    <View>
      <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.sm }]}>Favorite recipients</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: spacing.md }}>
        {recent.map((b) => {
          const flag = CORRIDORS.find((c) => c.country === b.country)?.flag;
          return (
            <TouchableOpacity
              key={b.id}
              onPress={() => { hapticLight(); onSelect(b); }}
              style={{ alignItems: "center", width: 72 }}
            >
              <Avatar name={b.full_name} flag={flag} size={56} />
              <Text style={[typography.caption, { color: theme.text, marginTop: 6, textAlign: "center", fontWeight: "600" }]} numberOfLines={2}>
                {b.full_name.split(" ")[0]}
              </Text>
            </TouchableOpacity>
          );
        })}
        <TouchableOpacity onPress={onAdd} style={{ alignItems: "center", width: 72 }}>
          <View style={{ width: 56, height: 56, borderRadius: 28, borderWidth: 2, borderColor: theme.border, borderStyle: "dashed", alignItems: "center", justifyContent: "center" }}>
            <Text style={{ fontSize: 24, color: theme.primary }}>+</Text>
          </View>
          <Text style={[typography.caption, { color: theme.textSecondary, marginTop: 6 }]}>Add</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}
