import { Text, View } from "react-native";
import { AmountDisplay } from "../fintech";
import type { TransferQuote } from "../../api/transfers";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { formatExchangeRate, formatForeign, formatZAR } from "../../utils/format";

interface CustomerQuoteSummaryProps {
  quote: TransferQuote;
  currency?: string;
  light?: boolean;
  compact?: boolean;
  deliveryMethod?: string;
  estimatedDelivery?: string;
}

export function CustomerQuoteSummary({
  quote,
  currency,
  light,
  compact,
  deliveryMethod,
  estimatedDelivery,
}: CustomerQuoteSummaryProps) {
  const theme = useAppTheme();
  const toCurrency = quote.to_currency ?? currency ?? "GHS";
  const fromCurrency = quote.from_currency ?? "ZAR";
  const rate = quote.customer_rate ?? quote.exchange_rate;
  const amountToPay = quote.amount_to_pay_zar ?? quote.total_amount_zar;
  const receive = quote.receive_amount ?? quote.receive_amount_ghs;

  const labelColor = light ? "rgba(255,255,255,0.75)" : theme.textSecondary;
  const valueColor = light ? "#fff" : theme.text;
  const mutedColor = light ? "rgba(255,255,255,0.7)" : theme.textTertiary;

  return (
    <View style={{ gap: spacing.sm }}>
      <AmountDisplay
        label="Amount to pay"
        amount={formatZAR(amountToPay)}
        sublabel="Final amount — no extra charges at checkout"
        size={compact ? "sm" : "lg"}
        light={light}
      />

      <View style={{ paddingLeft: spacing.xs, gap: 4 }}>
        <Text style={[typography.caption, { color: mutedColor }]}>Includes</Text>
        <Row label="Transfer fee" value={formatZAR(quote.fee_zar)} labelColor={labelColor} valueColor={valueColor} />
      </View>

      <View style={{ height: 1, backgroundColor: light ? "rgba(255,255,255,0.2)" : theme.borderLight, marginVertical: spacing.xs }} />

      <AmountDisplay
        label="Recipient receives"
        amount={formatForeign(receive, toCurrency)}
        size="sm"
        light={light}
      />

      <Row
        label="Exchange rate"
        value={formatExchangeRate(rate, fromCurrency, toCurrency)}
        labelColor={labelColor}
        valueColor={valueColor}
      />

      {(deliveryMethod ?? quote.delivery_method) ? (
        <Row
          label="Delivery method"
          value={deliveryMethod ?? quote.delivery_method ?? "—"}
          labelColor={labelColor}
          valueColor={valueColor}
        />
      ) : null}

      {(estimatedDelivery ?? quote.estimated_delivery) ? (
        <Row
          label="Estimated delivery"
          value={estimatedDelivery ?? quote.estimated_delivery ?? "—"}
          labelColor={labelColor}
          valueColor={valueColor}
        />
      ) : null}
    </View>
  );
}

function Row({
  label,
  value,
  labelColor,
  valueColor,
}: {
  label: string;
  value: string;
  labelColor: string;
  valueColor: string;
}) {
  return (
    <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
      <Text style={[typography.caption, { color: labelColor }]}>{label}</Text>
      <Text style={[typography.bodySm, { color: valueColor, fontWeight: "600", textAlign: "right", flexShrink: 1, marginLeft: spacing.sm }]}>
        {value}
      </Text>
    </View>
  );
}
