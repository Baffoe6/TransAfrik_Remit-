import { SafeAreaView, ScrollView, View, ViewStyle } from "react-native";
import { useAppTheme } from "../theme";
import { spacing } from "../theme/spacing";

interface ScreenProps {
  children: React.ReactNode;
  scroll?: boolean;
  padded?: boolean;
  style?: ViewStyle;
  safe?: boolean;
}

export function Screen({ children, scroll = false, padded = true, style, safe = true }: ScreenProps) {
  const theme = useAppTheme();
  const padding = padded ? spacing.lg : 0;
  const content = scroll ? (
    <ScrollView
      contentContainerStyle={{ padding, paddingBottom: spacing.xxxl }}
      keyboardShouldPersistTaps="handled"
      showsVerticalScrollIndicator={false}
    >
      {children}
    </ScrollView>
  ) : (
    <View style={{ flex: 1, padding }}>{children}</View>
  );

  const Wrapper = safe ? SafeAreaView : View;
  return (
    <Wrapper style={[{ flex: 1, backgroundColor: theme.bg }, style]}>
      {content}
    </Wrapper>
  );
}
