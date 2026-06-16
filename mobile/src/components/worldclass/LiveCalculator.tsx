import { ActivityIndicator, Text, TextInput, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { AmountDisplay, FintechCard } from "../fintech";
import { useLiveQuote } from "../../hooks/useLiveQuote";
import { useAppTheme, radius, spacing } from "../../theme";
import { typography } from "../../theme/typography";
import { formatForeign, formatZAR } from "../../utils/format";
import { PAYOUT_PARTNERS } from "../../utils/constants";

interface LiveCalculatorProps {
  amount: string;
  onAmountChange: (v: string) => void;
  destinationCountry: string;
  currency: string;
  corridorCode: string;
  onSend?: () => void;
  compact?: boolean;
}

export function LiveCalculator({
  amount,
  onAmountChange,
  destinationCountry,
  currency,
  corridorCode,
  compact,
}: LiveCalculatorProps) {
  const theme = useAppTheme();
  const { data: quote, isFetching, isError } = useLiveQuote(amount, destinationCountry);

  const partner = PAYOUT_PARTNERS.find((p) => (p.corridors as readonly string[]).includes(destinationCountry));

  return (
    <FintechCard variant={compact ? "elevated" : "hero"}>
      {!compact && (
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.md }}>
          <Text style={[typography.label, { color: "rgba(255,255,255,0.75)" }]}>Live exchange rate</Text>
          {isFetching && <ActivityIndicator size="small" color="#fff" />}
        </View>
      )}

      <View style={{ marginBottom: spacing.md }}>
        <Text style={[typography.caption, { color: compact ? theme.textSecondary : "rgba(255,255,255,0.75)", marginBottom: 6 }]}>
          You send
        </Text>
        <TextInput
          value={amount}
          onChangeText={onAmountChange}
          keyboardType="decimal-pad"
          style={[
            typography.amountSm,
            {
              color: compact ? theme.text : "#fff",
              backgroundColor: compact ? theme.inputBg : "rgba(255,255,255,0.12)",
              borderRadius: radius.lg,
              padding: spacing.md,
              borderWidth: 1,
              borderColor: compact ? theme.border : "rgba(255,255,255,0.2)",
            },
          ]}
        />
      </View>

      {quote && !isError ? (
        <>
          <View style={{ height: 1, backgroundColor: compact ? theme.borderLight : "rgba(255,255,255,0.2)", marginVertical: spacing.sm }} />
          <View style={{ gap: spacing.sm }}>
            <Row label="Fee" value={formatZAR(quote.fee_zar)} light={!compact} muted />
            <Row
              label="Rate"
              value={`1 ${quote.from_currency ?? "ZAR"} = ${quote.customer_rate ?? quote.exchange_rate} ${quote.to_currency ?? currency}`}
              light={!compact}
              muted
            />
            <AmountDisplay
              label="Recipient receives"
              amount={formatForeign(quote.receive_amount ?? quote.receive_amount_ghs, quote.to_currency ?? currency)}
              sublabel={`Total ${formatZAR(quote.total_amount_zar)}`}
              size="sm"
              light={!compact}
            />
          </View>
          {partner && (
            <View style={{ flexDirection: "row", alignItems: "center", gap: 6, marginTop: spacing.md }}>
              <Ionicons name="shield-checkmark" size={14} color={compact ? theme.primary : theme.accent} />
              <Text style={[typography.caption, { color: compact ? theme.textSecondary : "rgba(255,255,255,0.8)" }]}>
                Payout via {partner.name} · {corridorCode}
              </Text>
            </View>
          )}
        </>
      ) : isError ? (
        <Text style={{ color: compact ? theme.error : "#FCA5A5", fontSize: 13 }}>Unable to fetch live rate</Text>
      ) : (
        <Text style={{ color: compact ? theme.textTertiary : "rgba(255,255,255,0.6)", fontSize: 13 }}>Enter amount (min R50)</Text>
      )}
    </FintechCard>
  );
}

function Row({ label, value, light, muted }: { label: string; value: string; light?: boolean; muted?: boolean }) {
  const theme = useAppTheme();
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
      <Text style={[typography.caption, { color: light ? "rgba(255,255,255,0.7)" : theme.textSecondary }]}>{label}</Text>
      <Text style={[typography.bodySm, { color: muted ? (light ? "rgba(255,255,255,0.9)" : theme.text) : theme.text, fontWeight: "600" }]}>{value}</Text>
    </View>
  );
}
