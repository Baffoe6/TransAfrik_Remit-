"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { KycStatusBadge } from "@/components/transfers/status-badge";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import type { Profile } from "@/types";

export default function ProfilePage() {
  const { user, refreshUser } = useAuth();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    api<Profile>("/profile").then(setProfile).catch(() => {});
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile) return;
    setSaving(true);
    try {
      const updated = await api<Profile>("/profile", {
        method: "PATCH",
        body: JSON.stringify({
          first_name: profile.first_name,
          last_name: profile.last_name,
          date_of_birth: profile.date_of_birth,
          id_number: profile.id_number,
          address_line1: profile.address_line1,
          city: profile.city,
          province: profile.province,
          postal_code: profile.postal_code,
        }),
      });
      setProfile(updated);
      setMessage("Profile updated successfully");
    } catch {
      setMessage("Failed to update profile");
    } finally {
      setSaving(false);
    }
  };

  const verifyEmail = async () => {
    await api("/auth/verify-email", { method: "POST" });
    await refreshUser();
    setMessage("Email marked as verified (placeholder)");
  };

  const verifyPhone = async () => {
    await api("/auth/verify-phone", { method: "POST" });
    await refreshUser();
    setMessage("Phone marked as verified (placeholder)");
  };

  if (!profile) return <p>Loading...</p>;

  const update = (field: keyof Profile) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setProfile((p) => p ? { ...p, [field]: e.target.value } : p);

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-[#1B5E3B]">My Profile</h1>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Account Details
            <KycStatusBadge status={profile.kyc_status} />
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" onClick={verifyEmail} disabled={user?.email_verified}>
              {user?.email_verified ? "Email Verified" : "Verify Email (Placeholder)"}
            </Button>
            <Button variant="outline" size="sm" onClick={verifyPhone} disabled={user?.phone_verified}>
              {user?.phone_verified ? "Phone Verified" : "Verify Phone (Placeholder)"}
            </Button>
          </div>
          {message && <p className="text-sm text-green-700">{message}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Personal Information</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>First Name</Label>
                <Input value={profile.first_name} onChange={update("first_name")} required />
              </div>
              <div className="space-y-2">
                <Label>Last Name</Label>
                <Input value={profile.last_name} onChange={update("last_name")} required />
              </div>
            </div>
            <div className="space-y-2">
              <Label>ID Number</Label>
              <Input value={profile.id_number || ""} onChange={update("id_number")} />
            </div>
            <div className="space-y-2">
              <Label>Date of Birth</Label>
              <Input type="date" value={profile.date_of_birth || ""} onChange={update("date_of_birth")} />
            </div>
            <div className="space-y-2">
              <Label>Address</Label>
              <Input value={profile.address_line1 || ""} onChange={update("address_line1")} />
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label>City</Label>
                <Input value={profile.city || ""} onChange={update("city")} />
              </div>
              <div className="space-y-2">
                <Label>Province</Label>
                <Input value={profile.province || ""} onChange={update("province")} />
              </div>
              <div className="space-y-2">
                <Label>Postal Code</Label>
                <Input value={profile.postal_code || ""} onChange={update("postal_code")} />
              </div>
            </div>
            <Button type="submit" disabled={saving}>{saving ? "Saving..." : "Save Changes"}</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
