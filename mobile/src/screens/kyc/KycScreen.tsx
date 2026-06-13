import { ScrollView, Text } from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as DocumentPicker from "expo-document-picker";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Screen, Title, Button, Card, Muted } from "../../components/ui";
import { kycApi } from "../../api";

const DOC_TYPES = [
  { type: "id_passport", label: "ID / Passport" },
  { type: "proof_of_address", label: "Proof of Address" },
  { type: "selfie", label: "Selfie" },
];

export default function KycScreen() {
  const qc = useQueryClient();
  const { data: docs = [] } = useQuery({
    queryKey: ["kyc-docs"],
    queryFn: async () => (await kycApi.documents()).data,
  });

  const uploadFile = async (documentType: string, uri: string, name: string, mime: string) => {
    const form = new FormData();
    form.append("document_type", documentType);
    form.append("file", { uri, name, type: mime } as unknown as Blob);
    await kycApi.upload(form);
    qc.invalidateQueries({ queryKey: ["kyc-docs"] });
  };

  const pickDocument = async (documentType: string) => {
    const result = await DocumentPicker.getDocumentAsync({ type: ["image/*", "application/pdf"] });
    if (!result.canceled && result.assets[0]) {
      const a = result.assets[0];
      await uploadFile(documentType, a.uri, a.name, a.mimeType || "application/octet-stream");
    }
  };

  const captureSelfie = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) return;
    const result = await ImagePicker.launchCameraAsync({ quality: 0.8 });
    if (!result.canceled && result.assets[0]) {
      const a = result.assets[0];
      await uploadFile("selfie", a.uri, "selfie.jpg", "image/jpeg");
    }
  };

  return (
    <Screen>
      <ScrollView>
        <Title>KYC Documents</Title>
        <Muted>Upload your identity documents for verification</Muted>
        {DOC_TYPES.map((d) => (
          <Card key={d.type} style={{ marginVertical: 8 }}>
            <Text style={{ fontWeight: "600" }}>{d.label}</Text>
            <Muted>
              {docs.find((doc) => doc.document_type === d.type)?.status || "Not uploaded"}
            </Muted>
            {d.type === "selfie" ? (
              <Button title="Capture Selfie" variant="outline" onPress={captureSelfie} />
            ) : (
              <Button title="Upload" variant="outline" onPress={() => pickDocument(d.type)} />
            )}
          </Card>
        ))}
      </ScrollView>
    </Screen>
  );
}
