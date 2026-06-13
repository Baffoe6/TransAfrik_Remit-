import { Modal, Text, TouchableOpacity, View } from "react-native";
import { useAppTheme } from "../theme";
import { radius, spacing } from "../theme/spacing";
import { typography } from "../theme/typography";
import { Button } from "./Button";

interface ModalSheetProps {
  visible: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export function ModalSheet({ visible, onClose, title, children }: ModalSheetProps) {
  const theme = useAppTheme();
  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onClose}>
      <TouchableOpacity style={{ flex: 1, backgroundColor: theme.overlay }} activeOpacity={1} onPress={onClose} />
      <View
        style={{
          backgroundColor: theme.surface,
          borderTopLeftRadius: radius.xl,
          borderTopRightRadius: radius.xl,
          padding: spacing.xl,
          paddingBottom: spacing.xxxl,
        }}
      >
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.lg }}>
          <Text style={[typography.h3, { color: theme.text }]}>{title}</Text>
          <TouchableOpacity onPress={onClose}>
            <Text style={{ fontSize: 22, color: theme.textSecondary }}>×</Text>
          </TouchableOpacity>
        </View>
        {children}
      </View>
    </Modal>
  );
}

export function AlertBanner({ type, message }: { type: "success" | "error" | "info"; message: string }) {
  const colors = { success: "#DCFCE7", error: "#FEE2E2", info: "#DBEAFE" };
  const fg = { success: "#166534", error: "#991B1B", info: "#1E40AF" };
  return (
    <View style={{ backgroundColor: colors[type], padding: spacing.md, borderRadius: radius.md, marginBottom: spacing.md }}>
      <Text style={[typography.body, { color: fg[type] }]}>{message}</Text>
    </View>
  );
}
