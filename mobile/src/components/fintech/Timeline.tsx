import { Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useAppTheme, spacing } from "../../theme";
import { typography } from "../../theme/typography";

export interface TimelineStep {
  title: string;
  subtitle?: string;
  note?: string;
  active?: boolean;
  completed?: boolean;
}

export function Timeline({ steps }: { steps: TimelineStep[] }) {
  const theme = useAppTheme();
  return (
    <View>
      {steps.map((step, i) => {
        const isLast = i === steps.length - 1;
        const dotColor = step.completed ? theme.success : step.active ? theme.primary : theme.border;
        return (
          <View key={i} style={{ flexDirection: "row", minHeight: 56 }}>
            <View style={{ alignItems: "center", width: 28 }}>
              <View
                style={{
                  width: step.active ? 14 : 10,
                  height: step.active ? 14 : 10,
                  borderRadius: 7,
                  backgroundColor: dotColor,
                  borderWidth: step.active ? 3 : 0,
                  borderColor: theme.primaryMuted,
                }}
              />
              {!isLast ? (
                <View style={{ flex: 1, width: 2, backgroundColor: step.completed ? theme.success + "60" : theme.border, marginVertical: 4 }} />
              ) : null}
            </View>
            <View style={{ flex: 1, paddingBottom: spacing.lg, paddingLeft: spacing.sm }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 6 }}>
                {step.completed ? <Ionicons name="checkmark-circle" size={16} color={theme.success} /> : null}
                <Text style={[typography.bodyBold, { color: step.active || step.completed ? theme.text : theme.textTertiary }]}>
                  {step.title}
                </Text>
              </View>
              {step.subtitle ? <Text style={[typography.caption, { color: theme.textSecondary, marginTop: 2 }]}>{step.subtitle}</Text> : null}
              {step.note ? <Text style={[typography.caption, { color: theme.textTertiary, marginTop: 2 }]}>{step.note}</Text> : null}
            </View>
          </View>
        );
      })}
    </View>
  );
}

export function ProgressBar({ progress, light }: { progress: number; light?: boolean }) {
  const theme = useAppTheme();
  const pct = Math.min(100, Math.max(0, progress));
  return (
    <View>
      <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: spacing.sm }}>
        <Text style={[typography.caption, { color: light ? "rgba(255,255,255,0.85)" : theme.textSecondary }]}>Progress</Text>
        <Text style={[typography.caption, { color: light ? "#fff" : theme.primary, fontWeight: "700" }]}>{pct}%</Text>
      </View>
      <View style={{ height: 6, backgroundColor: light ? "rgba(255,255,255,0.25)" : theme.border, borderRadius: 3, overflow: "hidden" }}>
        <View style={{ width: `${pct}%`, height: 6, backgroundColor: light ? theme.accent : theme.primary, borderRadius: 3 }} />
      </View>
    </View>
  );
}
