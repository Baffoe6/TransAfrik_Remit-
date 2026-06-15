import { useState } from "react";
import * as ImagePicker from "expo-image-picker";
import { Camera } from "expo-camera";
import { Text, View } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { NativeStackScreenProps } from "@react-navigation/native-stack";
import { Ionicons } from "@expo/vector-icons";
import { AlertBanner, Button, FintechCard, ProgressBar, Screen, StatusPill } from "../../components";
import { kycApi, profileApi } from "../../api";
import { spacing, useAppTheme } from "../../theme";
import { typography } from "../../theme/typography";
import { radius } from "../../theme/spacing";
import { RootStackParamList } from "../../navigation/MainNavigator";

type Props = NativeStackScreenProps<RootStackParamList, "Kyc">;

const DOCS = [
  { type: "id_document", label: "SA ID or Passport", icon: "card-outline" as const, hint: "Clear photo of your ID document" },
  { type: "proof_of_address", label: "Proof of Address", icon: "home-outline" as const, hint: "Utility bill or bank statement (3 months)" },
  { type: "selfie", label: "Selfie Verification", icon: "person-circle-outline" as const, hint: "Hold your ID next to your face" },
];

export default function KycScreen({ navigation }: Props) {
  const theme = useAppTheme();
  const qc = useQueryClient();
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);

  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: async () => (await profileApi.get()).data });
  const { data: docs = [], refetch } = useQuery({ queryKey: ["kyc-docs"], queryFn: async () => (await kycApi.documents()).data });

  const uploadedTypes = new Set(docs.map((d) => d.document_type));
  const progress = Math.round((DOCS.filter((d) => uploadedTypes.has(d.type)).length / DOCS.length) * 100);
  const kycStatus = profile?.kyc_status ?? "draft";

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

  const statusVariant = kycStatus === "approved" ? "success" : kycStatus === "rejected" ? "error" : "warning";

  return (
    <Screen scroll>
      <Text style={[typography.h1, { color: theme.text }]}>Verify your identity</Text>
      <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.lg }]}>
        Required by FICA regulations. Your data is encrypted and secure.
      </Text>

      {profile?.kyc_rejection_reason && <AlertBanner type="error" message={`Rejected: ${profile.kyc_rejection_reason}`} />}
      {error ? <AlertBanner type="error" message={error} /> : null}

      <FintechCard variant="hero">
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.md }}>
          <Text style={{ color: "#fff", fontWeight: "700", fontSize: 16 }}>Verification progress</Text>
          <StatusPill label={kycStatus} variant={statusVariant as "success"} />
        </View>
        <ProgressBar progress={progress} light />
        <Text style={{ color: "rgba(255,255,255,0.7)", fontSize: 13, marginTop: spacing.md }}>
          {progress === 100 ? "All documents uploaded — under review" : `${DOCS.length - uploadedTypes.size} document(s) remaining`}
        </Text>
      </FintechCard>

      {DOCS.map((doc) => {
        const uploaded = docs.find((d) => d.document_type === doc.type);
        const done = !!uploaded;
        return (
          <FintechCard key={doc.type} variant={done ? "accent" : "elevated"}>
            <View style={{ flexDirection: "row", gap: spacing.md, marginBottom: spacing.md }}>
              <View style={{ width: 48, height: 48, borderRadius: radius.lg, backgroundColor: done ? theme.primaryMuted : theme.surfaceMuted, alignItems: "center", justifyContent: "center" }}>
                <Ionicons name={done ? "checkmark-circle" : doc.icon} size={26} color={done ? theme.success : theme.primary} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={[typography.bodyBold, { color: theme.text }]}>{doc.label}</Text>
                <Text style={[typography.caption, { color: theme.textSecondary }]}>{doc.hint}</Text>
                {uploaded ? <StatusPill label={uploaded.status} variant="success" /> : null}
              </View>
            </View>
            {!done && (
              <View style={{ flexDirection: "row", gap: spacing.sm }}>
                <Button title="Take photo" onPress={() => upload(doc.type, true)} variant="primary" loading={uploading} style={{ flex: 1 }} />
                <Button title="Gallery" onPress={() => upload(doc.type, false)} variant="outline" loading={uploading} style={{ flex: 1 }} />
              </View>
            )}
          </FintechCard>
        );
      })}

      {progress === 100 && (
        <FintechCard variant="muted">
          <Text style={[typography.h3, { color: theme.text }]}>Under review</Text>
          <Text style={[typography.body, { color: theme.textSecondary, marginTop: spacing.sm }]}>
            Our compliance team will verify your documents within 24–48 hours. We'll notify you when approved.
          </Text>
        </FintechCard>
      )}
    </Screen>
  );
}
