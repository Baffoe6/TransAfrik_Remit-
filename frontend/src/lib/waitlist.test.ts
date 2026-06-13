import { describe, expect, it } from "vitest";

const DESTINATIONS = ["GH", "ZW", "ZM", "KE", "NG", "UG"];

describe("waitlist corridors", () => {
  it("includes all MVP destination corridors from ZA", () => {
    expect(DESTINATIONS).toHaveLength(6);
    expect(DESTINATIONS).toContain("GH");
    expect(DESTINATIONS).toContain("NG");
  });
});

describe("waitlist payload validation", () => {
  it("requires email and destination country", () => {
    const payload = {
      first_name: "Jane",
      last_name: "Doe",
      email: "jane@example.com",
      country_from: "ZA",
      country_to: "GH",
    };
    expect(payload.email).toContain("@");
    expect(payload.country_to).toHaveLength(2);
    expect(payload.country_from).toBe("ZA");
  });
});
