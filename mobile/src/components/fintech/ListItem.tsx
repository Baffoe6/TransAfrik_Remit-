import { Ionicons } from "@expo/vector-icons";
import { Text, TouchableOpacity, View, ViewStyle } from "react-native";
import { useAppTheme } from "../../theme";
import { radius, spacing } from "../../theme/spacing";
import { typography } from "../../theme/typography";
import { Avatar } from "./Avatar";

interface ListItemProps {
  title: string;
  subtitle?: string;
  meta?: string;
  avatarName?: string;
  flag?: string;
  icon?: keyof typeof Ionicons.glyphMap;
  iconColor?: string;
  onPress?: () => void;
  right?: React.ReactNode;
  style?: ViewStyle;
  showChevron?: boolean;
}

export function ListItem({
  title,
  subtitle,
  meta,
  avatarName,
  flag,
  icon,
  iconColor,
  onPress,
  right,
  style,
  showChevron = true,
}: ListItemProps) {
  const theme = useAppTheme();
  const content = (
    <View
      style={[
        {
          flexDirection: "row",
          alignItems: "center",
          paddingVertical: spacing.md,
          paddingHorizontal: spacing.lg,
          gap: spacing.md,
          backgroundColor: theme.surface,
        },
        style,
      ]}
    >
      {avatarName ? <Avatar name={avatarName} flag={flag} size={44} /> : null}
      {icon ? (
        <View
          style={{
            width: 44,
            height: 44,
            borderRadius: radius.md,
            backgroundColor: theme.primaryMuted,
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Ionicons name={icon} size={22} color={iconColor ?? theme.primary} />
        </View>
      ) : null}
      <View style={{ flex: 1 }}>
        <Text style={[typography.bodyBold, { color: theme.text }]} numberOfLines={1}>
          {title}
        </Text>
        {subtitle ? (
          <Text style={[typography.caption, { color: theme.textSecondary, marginTop: 2 }]} numberOfLines={1}>
            {subtitle}
          </Text>
        ) : null}
        {meta ? (
          <Text style={[typography.caption, { color: theme.textTertiary, marginTop: 2 }]} numberOfLines={1}>
            {meta}
          </Text>
        ) : null}
      </View>
      {right}
      {showChevron && onPress ? <Ionicons name="chevron-forward" size={18} color={theme.textTertiary} /> : null}
    </View>
  );

  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} activeOpacity={0.65}>
        {content}
      </TouchableOpacity>
    );
  }
  return content;
}

export function ListDivider() {
  const theme = useAppTheme();
  return <View style={{ height: 1, backgroundColor: theme.borderLight, marginLeft: spacing.lg + 44 + spacing.md }} />;
}
