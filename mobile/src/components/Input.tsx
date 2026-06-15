import { Text, TextInput, TextInputProps, View } from "react-native";
import { useAppTheme } from "../theme";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  hint?: string;
}

export function Input({ label, error, hint, style, ...rest }: InputProps) {
  const theme = useAppTheme();
  return (
    <View style={{ marginBottom: spacing.md }}>
      {label ? <Text style={[typography.label, { color: theme.text, marginBottom: spacing.xs }]}>{label}</Text> : null}
      <TextInput
        placeholderTextColor={theme.textSecondary}
        style={[
          {
            borderWidth: 1.5,
            borderColor: error ? theme.error : theme.inputBorder,
            borderRadius: radius.lg,
            padding: spacing.md,
            color: theme.text,
            backgroundColor: theme.inputBg,
            fontSize: 16,
          },
          style,
        ]}
        {...rest}
      />
      {error ? <Text style={[typography.caption, { color: theme.error, marginTop: spacing.xs }]}>{error}</Text> : null}
      {hint && !error ? <Text style={[typography.caption, { color: theme.textSecondary, marginTop: spacing.xs }]}>{hint}</Text> : null}
    </View>
  );
}

interface PinInputProps {
  value: string;
  onChange: (v: string) => void;
  length?: number;
  label?: string;
}

export function PinInput({ value, onChange, length = 4, label }: PinInputProps) {
  const theme = useAppTheme();
  return (
    <View style={{ marginBottom: spacing.md }}>
      {label ? <Text style={[typography.label, { color: theme.text, marginBottom: spacing.sm }]}>{label}</Text> : null}
      <TextInput
        value={value}
        onChangeText={(t) => onChange(t.replace(/\D/g, "").slice(0, length))}
        keyboardType="number-pad"
        secureTextEntry
        maxLength={length}
        placeholder={"•".repeat(length)}
        placeholderTextColor={theme.textSecondary}
        style={{
          borderWidth: 1.5,
          borderColor: theme.border,
          borderRadius: radius.md,
          padding: spacing.lg,
          fontSize: 28,
          letterSpacing: 12,
          textAlign: "center",
          color: theme.text,
          backgroundColor: theme.surface,
        }}
      />
    </View>
  );
}
