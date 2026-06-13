import { useState } from "react";
import * as ImagePicker from "expo-image-picker";
import { Camera } from "expo-camera";
import { Text, View } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { AlertBanner, Body, Button, Caption, Card, H2, Screen } from "../../components";
import { kycApi, profileApi } from "../../api";
import { RootStackParamList } from "../../navigation/MainNavigator";

type Props = NativeStackScreenProps<RootStackParamList, "Kyc">;

const DOCS = [
  { type: "id_document", label: "SA ID / Passport" },
  { type: "proof_of_address", label: "Proof of Address" },
  { type: "selfie", label: "Selfie Verification" },
];

export default function KycScreen({ navigation }: Props) {
  const qc = useQueryClient();
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: async () => (await profileApi.get()).data });
  const { data: docs = [], refetch } = useQuery({ queryKey: ["kyc-docs"], queryFn: async () => (await kycApi.documents()).data });

  const uploadedTypes = new Set(docs.map((d) => d.document_type));
  const progress = Math.round((DOCS.filter((d) => uploadedTypes.has(d.type)).length / DOCS.length) * 100);

  const upload = async (documentType: string, useCamera: boolean) => {
    setUploading(true);
    setError("");
    try {
      if (useCamera) {
        const perm = await Camera.requestCameraPermissionsAsync();
        if (!perm.granted) throw new Error("Camera permission required");
        const result = await ImagePicker.launchCameraAsync({ quality: 0.8 });
        if (result.canceled) return;
        await postUpload(documentType, result.assets[0].uri, result.assets[0].fileName ?? "photo.jpg");
      } else {
        const result = await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });
        if (result.canceled) return;
        await postUpload(documentType, result.assets[0].uri, result.assets[0].fileName ?? "doc.jpg");
      }
      await refetch();
      await qc.invalidateQueries({ queryKey: ["dashboard"] });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const postUpload = async (documentType: string, uri: string, name: string) => {
    const form = new FormData();
    form.append("document_type", documentType);
    form.append("file", { uri, name, type: "image/jpeg" } as unknown as Blob);
    await kycApi.upload(form);
  };

  return (
    <Screen scroll>
      <H2>KYC Verification</H2>
      <Body muted>Verify your identity to send money securely</Body>
      {profile?.kyc_rejection_reason && <AlertBanner type="error" message={`Rejected: ${profile.kyc_rejection_reason}`} />}
      {error ? <AlertBanner type="error" message={error} /> : null}

      <Card elevated accent>
        <Text style={{ color: "rgba(255,255,255,0.8)", fontSize: 13 }}>{progress}% Complete</Text>
        <View style={{ height: 8, backgroundColor: "rgba(255,255,255,0.3)", borderRadius: 4, marginTop: 8 }}>
          <View style={{ width: `${progress}%`, height: 8, backgroundColor: "#C9A227", borderRadius: 4 }} />
        </View>
        <Text style={{ color: "rgba(255,255,255,0.7)", fontSize: 13, marginTop: 8 }}>Status: {profile?.kyc_status ?? "draft"}</Text>
      </Card>

      {DOCS.map((doc) => {
        const uploaded = docs.find((d) => d.document_type === doc.type);
        return (
          <Card key={doc.type}>
            <Text style={{ fontWeight: "600", fontSize: 16 }}>{doc.label}</Text>
            <Caption>{uploaded ? `Uploaded · ${uploaded.status}` : "Not uploaded"}</Caption>
            <View style={{ flexDirection: "row", gap: 8, marginTop: 8 }}>
              <Button title="Camera" onPress={() => upload(doc.type, true)} variant="outline" loading={uploading} />
              <Button title="Gallery" onPress={() => upload(doc.type, false)} variant="secondary" loading={uploading} />
            </View>
          </Card>
        );
      })}

      {progress === 100 && (
        <Card>
          <H2>Submitted</H2>
          <Caption>Our compliance team will review your documents within 24–48 hours.</Caption>
        </Card>
      )}
    </Screen>
  );
}
