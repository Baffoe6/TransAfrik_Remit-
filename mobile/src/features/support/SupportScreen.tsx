import { useState } from "react";
import { Linking, Text, TouchableOpacity, View } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Ionicons } from "@expo/vector-icons";
import { AlertBanner, Button, FintechCard, Input, Screen, StatusPill } from "../../components";
import { supportApi } from "../../api";
import { FAQ_ITEMS } from "../../utils/constants";
import { SUPPORT_CATEGORIES, COMPLIANCE } from "../../utils/compliance";
import { spacing, useAppTheme, radius } from "../../theme";
import { typography } from "../../theme/typography";
import { formatDate } from "../../utils/format";
import { hapticLight } from "../../services/haptics";

const WHATSAPP_URL = "https://wa.me/27123456789?text=Hi%20TransAfrik%2C%20I%20need%20help%20with%20my%20transfer";

export default function SupportScreen() {
  const qc = useQueryClient();
  const theme = useAppTheme();
  const [category, setCategory] = useState("general");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [expandedFaq, setExpandedFaq] = useState<string | null>(null);
  const [tab, setTab] = useState<"help" | "tickets" | "chat">("help");

  const { data: tickets = [], refetch } = useQuery({
    queryKey: ["support-tickets"],
    queryFn: async () => (await supportApi.listTickets()).data,
  });

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      await supportApi.createTicket({
        subject: `[${SUPPORT_CATEGORIES.find((c) => c.value === category)?.label ?? category}] ${subject}`,
        message,
      });
      setSubject("");
      setMessage("");
      await refetch();
      await qc.invalidateQueries({ queryKey: ["support-tickets"] });
      setTab("tickets");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create ticket");
    } finally {
      setLoading(false);
    }
  };

  const openWhatsApp = () => {
    hapticLight();
    Linking.openURL(WHATSAPP_URL);
  };

  return (
    <Screen scroll>
      <Text style={[typography.h1, { color: theme.text }]}>Help & support</Text>
      <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.lg }]}>
        WhatsApp, tickets, FAQ and live chat
      </Text>

      <View style={{ flexDirection: "row", gap: spacing.sm, marginBottom: spacing.lg }}>
        {(["help", "tickets", "chat"] as const).map((t) => (
          <TouchableOpacity
            key={t}
            onPress={() => setTab(t)}
            style={{
              flex: 1,
              paddingVertical: spacing.sm,
              borderRadius: radius.full,
              backgroundColor: tab === t ? theme.primary : theme.surfaceMuted,
              alignItems: "center",
            }}
          >
            <Text style={[typography.caption, { color: tab === t ? "#fff" : theme.text, fontWeight: "700", textTransform: "capitalize" }]}>{t}</Text>
          </TouchableOpacity>
        ))}
      </View>

      {tab === "help" && (
        <>
          <FintechCard variant="hero" padding="lg">
            <View style={{ flexDirection: "row", alignItems: "center", gap: spacing.md }}>
              <Ionicons name="logo-whatsapp" size={32} color="#25D366" />
              <View style={{ flex: 1 }}>
                <Text style={{ color: "#fff", fontWeight: "700", fontSize: 16 }}>WhatsApp support</Text>
                <Text style={{ color: "rgba(255,255,255,0.75)", fontSize: 13 }}>Fastest response · Mon–Sat 8am–8pm</Text>
              </View>
            </View>
            <Button title="Chat on WhatsApp" onPress={openWhatsApp} variant="gold" style={{ marginTop: spacing.md }} />
          </FintechCard>

          <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>FAQ</Text>
          {FAQ_ITEMS.map((f) => (
            <TouchableOpacity key={f.q} onPress={() => setExpandedFaq(expandedFaq === f.q ? null : f.q)} activeOpacity={0.85}>
              <FintechCard variant="muted" padding="md" style={{ marginBottom: spacing.sm }}>
                <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                  <Text style={[typography.bodyBold, { color: theme.text, flex: 1 }]}>{f.q}</Text>
                  <Ionicons name={expandedFaq === f.q ? "chevron-up" : "chevron-down"} size={18} color={theme.textTertiary} />
                </View>
                {expandedFaq === f.q && (
                  <Text style={[typography.bodySm, { color: theme.textSecondary, marginTop: spacing.sm }]}>{f.a}</Text>
                )}
              </FintechCard>
            </TouchableOpacity>
          ))}
        </>
      )}

      {tab === "tickets" && (
        <>
          <FintechCard variant="elevated">
            <Text style={[typography.h3, { color: theme.text, marginBottom: spacing.md }]}>Create ticket</Text>
            {error ? <AlertBanner type="error" message={error} /> : null}
            <Text style={[typography.label, { color: theme.textTertiary, marginBottom: spacing.xs }]}>Category</Text>
            <View style={{ flexDirection: "row", flexWrap: "wrap", gap: spacing.xs, marginBottom: spacing.md }}>
              {SUPPORT_CATEGORIES.map((c) => (
                <TouchableOpacity key={c.value} onPress={() => setCategory(c.value)} style={{ paddingHorizontal: 10, paddingVertical: 6, borderRadius: radius.full, backgroundColor: category === c.value ? theme.primary : theme.surfaceMuted }}>
                  <Text style={{ color: category === c.value ? "#fff" : theme.text, fontSize: 12, fontWeight: "600" }}>{c.label}</Text>
                </TouchableOpacity>
              ))}
            </View>
            <Input label="Subject" value={subject} onChangeText={setSubject} />
            <Input label="Message" value={message} onChangeText={setMessage} multiline />
            <Button title="Submit ticket" onPress={submit} loading={loading} />
          </FintechCard>

          <Text style={[typography.h3, { color: theme.text, marginTop: spacing.lg, marginBottom: spacing.md }]}>Your tickets</Text>
          {tickets.length === 0 ? (
            <Text style={[typography.body, { color: theme.textSecondary }]}>No tickets yet</Text>
          ) : (
            tickets.map((t) => (
              <FintechCard key={t.id} variant="default" padding="md" style={{ marginBottom: spacing.sm }}>
                <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center" }}>
                  <Text style={[typography.bodyBold, { color: theme.text }]}>{t.subject}</Text>
                  <StatusPill label={t.status} variant="info" size="sm" />
                </View>
                <Text style={[typography.caption, { color: theme.textSecondary, marginTop: 4 }]}>{formatDate(t.created_at)}</Text>
              </FintechCard>
            ))
          )}
        </>
      )}

      {tab === "chat" && (
        <FintechCard variant="muted">
          <View style={{ alignItems: "center", padding: spacing.xl }}>
            <Ionicons name="chatbubbles-outline" size={48} color={theme.primary} />
            <Text style={[typography.h3, { color: theme.text, marginTop: spacing.md }]}>Live chat</Text>
            <Text style={[typography.body, { color: theme.textSecondary, textAlign: "center", marginTop: spacing.sm }]}>
              In-app live chat is coming soon. Use WhatsApp for immediate assistance.
            </Text>
            <Button title="Open WhatsApp" onPress={openWhatsApp} variant="primary" style={{ marginTop: spacing.lg }} />
          </View>
        </FintechCard>
      )}
    </Screen>
  );
}
