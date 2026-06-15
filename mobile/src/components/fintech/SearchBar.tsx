import { Ionicons } from "@expo/vector-icons";
import { Text, TextInput, TouchableOpacity, View } from "react-native";
import { useAppTheme, radius, spacing } from "../../theme";
import { typography } from "../../theme/typography";

interface SearchBarProps {
  value: string;
  onChangeText: (t: string) => void;
  placeholder?: string;
}

export function SearchBar({ value, onChangeText, placeholder = "Search..." }: SearchBarProps) {
  const theme = useAppTheme();
  return (
    <View
      style={{
        flexDirection: "row",
        alignItems: "center",
        backgroundColor: theme.inputBg,
        borderRadius: radius.lg,
        paddingHorizontal: spacing.md,
        borderWidth: 1,
        borderColor: theme.inputBorder,
        marginBottom: spacing.md,
      }}
    >
      <Ionicons name="search" size={20} color={theme.textTertiary} />
      <TextInput
        value={value}
        onChangeText={onChangeText}
        placeholder={placeholder}
        placeholderTextColor={theme.textTertiary}
        style={[typography.body, { flex: 1, paddingVertical: spacing.md, paddingHorizontal: spacing.sm, color: theme.text }]}
      />
      {value.length > 0 ? (
        <TouchableOpacity onPress={() => onChangeText("")}>
          <Ionicons name="close-circle" size={20} color={theme.textTertiary} />
        </TouchableOpacity>
      ) : null}
    </View>
  );
}

interface FilterChipsProps<T extends string> {
  options: { value: T; label: string }[];
  selected: T;
  onSelect: (v: T) => void;
}

export function FilterChips<T extends string>({ options, selected, onSelect }: FilterChipsProps<T>) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", flexWrap: "wrap", gap: spacing.sm, marginBottom: spacing.md }}>
      {options.map((o) => {
        const active = selected === o.value;
        return (
          <TouchableOpacity
            key={o.value}
            onPress={() => onSelect(o.value)}
            activeOpacity={0.8}
            style={{
              paddingHorizontal: spacing.md,
              paddingVertical: spacing.sm,
              borderRadius: radius.full,
              backgroundColor: active ? theme.primary : theme.surfaceMuted,
              borderWidth: active ? 0 : 1,
              borderColor: theme.border,
            }}
          >
            <Text style={[typography.bodySm, { color: active ? "#fff" : theme.textSecondary, fontWeight: "600" }]}>
              {o.label}
            </Text>
          </TouchableOpacity>
        );
      })}
    </View>
  );
}
