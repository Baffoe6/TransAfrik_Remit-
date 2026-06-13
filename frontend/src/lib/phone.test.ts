import { describe, expect, it } from "vitest";
import { formatPhoneNumber, isEmailIdentifier, normalizePhoneNumber } from "./phone";

describe("phone utilities", () => {
  it("normalizes South African numbers", () => {
    expect(normalizePhoneNumber("0721234567")).toBe("+27721234567");
  });

  it("formats E.164 for display", () => {
    expect(formatPhoneNumber("+27721234567")).toContain("+27");
  });

  it("detects email login identifier", () => {
    expect(isEmailIdentifier("user@example.com")).toBe(true);
    expect(isEmailIdentifier("+27721234567")).toBe(false);
  });
});
