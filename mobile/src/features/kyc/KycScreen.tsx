import { useState } from "react";
import * as ImagePicker from "expo-image-picker";
import { Camera } from "expo-camera";
import { Image, Text, View } from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useFocusEffect } from "@react-navigation/native";
import { useCallback } from "react";import { Ionicons } from "@expo/vector-icons";
import { AlertBanner, Button, FintechCard, ProgressBar, Screen, StatusPill } from "../../components";
import { kycApi, profileApi } from "../../api";
import { KYC_DOC_TYPES, COMPLIANCE } from "../../utils/compliance";
import { KYC_WORKFLOW_STATES } from "../../utils/constants";
import { useVerificationStatus } from "../../hooks/useVerificationStatus";
import { spacing, useAppTheme, radius } from "../../theme";
import { typography } from "../../theme/typography";

const DOCS = KYC_DOC_TYPES.map((d) => ({ ...d, ocr: d.type === "id_passport" }));

function workflowVariant(status: string) {
  const state = KYC_WORKFLOW_STATES.find((s) => s.value === status.toLowerCase());
  return state?.variant ?? "neutral";
}

function workflowLabel(status: string) {
  const state = KYC_WORKFLOW_STATES.find((s) => s.value === status.toLowerCase());
  return state?.label ?? status;
}

export default function KycScreen() {
  const theme = useAppTheme();
  const qc = useQueryClient();
  const { kycRaw, kycApproved, sync } = useVerificationStatus();
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [previewUri, setPreviewUri] = useState<string | null>(null);

  const { data: profile } = useQuery({ queryKey: ["profile"], queryFn: async () => (await profileApi.get()).data });
  const { data: docs = [], refetch } = useQuery({ queryKey: ["kyc-docs"], queryFn: async () => (await kycApi.documents()).data });

  useFocusEffect(
    useCallback(() => {
      void sync();
      void refetch();
    }, [sync, refetch]),
  );

  const uploadedTypes = new Set(docs.map((d) => d.document_type));
  const progress = Math.round((DOCS.filter((d) => uploadedTypes.has(d.type)).length / DOCS.length) * 100);
  const kycStatus = kycApproved ? "approved" : (profile?.kyc_status ?? kycRaw ?? "draft");

  const upload = async (documentType: string, useCamera: boolean, ocr = false) => {
    setUploading(true);
    setError("");
    try {
      if (useCamera) {
        const perm = await Camera.requestCameraPermissionsAsync();
        if (!perm.granted) throw new Error("Camera permission required");
        const result = await ImagePicker.launchCameraAsync({ quality: 0.8 });
        if (result.canceled) return;
        setPreviewUri(result.assets[0].uri);
        if (ocr) setError("OCR scan complete — auto-fill from ID coming in next release");
        await postUpload(documentType, result.assets[0].uri, result.assets[0].fileName ?? "photo.jpg");
      } else {
        const result = await ImagePicker.launchImageLibraryAsync({ quality: 0.8 });
        if (result.canceled) return;
        setPreviewUri(result.assets[0].uri);
        await postUpload(documentType, result.assets[0].uri, result.assets[0].fileName ?? "doc.jpg");
      }
      await refetch();
      await sync();
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
      <Text style={[typography.h1, { color: theme.text }]}>Verify your identity</Text>
      <Text style={[typography.body, { color: theme.textSecondary, marginBottom: spacing.lg }]}>
        {COMPLIANCE.kycRequired} Documents are stored securely via our backend — not on your device.
      </Text>

      {profile?.kyc_rejection_reason && <AlertBanner type="error" message={`Rejected: ${profile.kyc_rejection_reason}`} />}
      {error ? <AlertBanner type={error.includes("OCR") ? "info" : "error"} message={error} /> : null}

      {kycApproved && (
        <FintechCard variant="muted">
          <Text style={[typography.h3, { color: theme.text }]}>Verification approved</Text>
          <Text style={[typography.body, { color: theme.textSecondary, marginTop: spacing.sm }]}>
            Your identity has been verified. You can send money now.
          </Text>
        </FintechCard>
      )}

      <FintechCard variant="hero">
        <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: spacing.md }}>
          <Text style={{ color: "#fff", fontWeight: "700", fontSize: 16 }}>Verification workflow</Text>
          <StatusPill label={workflowLabel(kycStatus)} variant={workflowVariant(kycStatus) as "success"} />
        </View>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 6, marginBottom: spacing.md }}>
          {KYC_WORKFLOW_STATES.map((s) => (
            <View
              key={s.value}
              style={{
                paddingHorizontal: 10,
                paddingVertical: 4,
                borderRadius: radius.full,
                backgroundColor: kycStatus.toLowerCase() === s.value ? "rgba(255,255,255,0.25)" : "rgba(255,255,255,0.08)",
              }}
            >
              <Text style={{ color: "#fff", fontSize: 11, fontWeight: "600" }}>{s.label}</Text>
            </View>
          ))}
        </View>
        <ProgressBar progress={progress} light />
        <Text style={{ color: "rgba(255,255,255,0.7)", fontSize: 13, marginTop: spacing.md }}>
          {progress === 100 ? "All documents uploaded — under review" : `${DOCS.length - uploadedTypes.size} document(s) remaining`}
        </Text>
      </FintechCard>

      {previewUri && (
        <FintechCard variant="outline">
          <Text style={[typography.label, { color: theme.textTertiary, marginBottom: spacing.sm }]}>Document preview</Text>
          <Image source={{ uri: previewUri }} style={{ width: "100%", height: 180, borderRadius: radius.lg }} resizeMode="cover" />
        </FintechCard>
      )}

      {DOCS.map((doc) => {
        if (kycApproved) return null;
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
              <View style={{ gap: spacing.sm }}>
                {doc.ocr && (
                  <Button
                    title="Scan ID (OCR)"
                    onPress={() => upload(doc.type, true, true)}
                    variant="gold"
                    loading={uploading}
                    icon={<Ionicons name="scan-outline" size={18} color="#1B3D2F" />}
                  />
                )}
                <View style={{ flexDirection: "row", gap: spacing.sm }}>
                  <Button title="Take photo" onPress={() => upload(doc.type, true)} variant="primary" loading={uploading} style={{ flex: 1 }} />
                  <Button title="Gallery" onPress={() => upload(doc.type, false)} variant="outline" loading={uploading} style={{ flex: 1 }} />
                </View>
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
