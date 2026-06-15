import { Text, View } from "react-native";
import { useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";

interface AvatarProps {
  name: string;
  size?: number;
  flag?: string;
}

function initials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase();
  return (name[0] ?? "?").toUpperCase();
}

const COLORS = ["#1B5E3B", "#247A4D", "#C9A227", "#2563EB", "#7C3AED", "#DB2777"];

function colorFor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return COLORS[Math.abs(hash) % COLORS.length];
}

export function Avatar({ name, size = 48, flag }: AvatarProps) {
  const bg = colorFor(name);
  return (
    <View
      style={{
        width: size,
        height: size,
        borderRadius: size / 2,
        backgroundColor: bg,
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {flag ? (
        <Text style={{ fontSize: size * 0.45 }}>{flag}</Text>
      ) : (
        <Text style={[typography.bodyBold, { color: "#fff", fontSize: size * 0.35 }]}>{initials(name)}</Text>
      )}
    </View>
  );
}
