import { StyleSheet, Text, TextInput, TouchableOpacity, View, ActivityIndicator } from "react-native";
import { useThemeColors } from "../store/themeStore";
import { useColorScheme } from "react-native";

export function Screen({ children, style }: { children: React.ReactNode; style?: object }) {
  const c = useThemeColors(useColorScheme() === "dark");
  return <View style={[{ flex: 1, backgroundColor: c.bg, padding: 16 }, style]}>{children}</View>;
}

export function Card({ children, style }: { children: React.ReactNode; style?: object }) {
  const c = useThemeColors(useColorScheme() === "dark");
  return (
    <View style={[{ backgroundColor: c.card, borderRadius: 12, padding: 16, borderWidth: 1, borderColor: c.border }, style]}>
      {children}
    </View>
  );
}

export function Title({ children }: { children: React.ReactNode }) {
  const c = useThemeColors(useColorScheme() === "dark");
  return <Text style={{ fontSize: 22, fontWeight: "700", color: c.primary, marginBottom: 8 }}>{children}</Text>;
}

export function Muted({ children }: { children: React.ReactNode }) {
  const c = useThemeColors(useColorScheme() === "dark");
  return <Text style={{ color: c.textMuted, fontSize: 14 }}>{children}</Text>;
}

export function Input(props: React.ComponentProps<typeof TextInput> & { label?: string }) {
  const c = useThemeColors(useColorScheme() === "dark");
  const { label, style, ...rest } = props;
  return (
    <View style={{ marginBottom: 12 }}>
      {label && <Text style={{ color: c.text, marginBottom: 4, fontWeight: "500" }}>{label}</Text>}
      <TextInput
        placeholderTextColor={c.textMuted}
        style={[
          {
            borderWidth: 1,
            borderColor: c.border,
            borderRadius: 8,
            padding: 12,
            color: c.text,
            backgroundColor: c.card,
          },
          style,
        ]}
        {...rest}
      />
    </View>
  );
}

export function Button({
  title,
  onPress,
  variant = "primary",
  loading,
  disabled,
}: {
  title: string;
  onPress: () => void;
  variant?: "primary" | "outline" | "danger";
  loading?: boolean;
  disabled?: boolean;
}) {
  const c = useThemeColors(useColorScheme() === "dark");
  const bg = variant === "primary" ? c.primary : variant === "danger" ? c.danger : "transparent";
  const textColor = variant === "outline" ? c.primary : "#fff";
  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      style={{
        backgroundColor: bg,
        borderWidth: variant === "outline" ? 1 : 0,
        borderColor: c.primary,
        borderRadius: 8,
        padding: 14,
        alignItems: "center",
        opacity: disabled || loading ? 0.6 : 1,
        marginVertical: 4,
      }}
    >
      {loading ? (
        <ActivityIndicator color={textColor} />
      ) : (
        <Text style={{ color: textColor, fontWeight: "600", fontSize: 16 }}>{title}</Text>
      )}
    </TouchableOpacity>
  );
}

export const styles = StyleSheet.create({
  row: { flexDirection: "row", gap: 8, alignItems: "center" },
  space: { marginVertical: 8 },
  listItem: { paddingVertical: 12, borderBottomWidth: StyleSheet.hairlineWidth },
});
