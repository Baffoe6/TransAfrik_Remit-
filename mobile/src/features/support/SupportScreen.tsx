import { useState } from "react";
import { FlatList, Linking } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { AlertBanner, Body, Button, Caption, Card, H2, Input, Screen } from "../../components";
import { supportApi } from "../../api";
import { FAQ_ITEMS } from "../../utils/constants";

export default function SupportScreen() {
  const qc = useQueryClient();
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const { data: tickets = [], refetch } = useQuery({
    queryKey: ["support-tickets"],
    queryFn: async () => (await supportApi.listTickets()).data,
  });

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      await supportApi.createTicket({ subject, message });
      setSubject("");
      setMessage("");
      await refetch();
      await qc.invalidateQueries({ queryKey: ["support-tickets"] });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create ticket");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen scroll>
      <H2>Support</H2>
      <Button title="WhatsApp Support" onPress={() => Linking.openURL("https://wa.me/27123456789")} variant="primary" />

      <Card>
        <H2>FAQ</H2>
        {FAQ_ITEMS.map((f) => (
          <Card key={f.q} style={{ marginBottom: 8 }}>
            <Body>{f.q}</Body>
            <Caption>{f.a}</Caption>
          </Card>
        ))}
      </Card>

      <Card>
        <H2>Create Ticket</H2>
        {error ? <AlertBanner type="error" message={error} /> : null}
        <Input label="Subject" value={subject} onChangeText={setSubject} />
        <Input label="Message" value={message} onChangeText={setMessage} multiline />
        <Button title="Submit Ticket" onPress={submit} loading={loading} />
      </Card>

      <H2>Your Tickets</H2>
      {tickets.map((t) => (
        <Card key={t.id}>
          <Body>{t.subject}</Body>
          <Caption>{t.status} · {new Date(t.created_at).toLocaleDateString()}</Caption>
        </Card>
      ))}
    </Screen>
  );
}
