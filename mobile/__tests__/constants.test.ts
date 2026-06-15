import { CORRIDORS, ACTIVITY_STATUS_FILTERS, BENEFICIARY_CATEGORIES, KYC_WORKFLOW_STATES, USER_TIERS } from "../src/utils/constants";

describe("constants", () => {
  it("defines six remittance corridors from South Africa", () => {
    expect(CORRIDORS).toHaveLength(6);
    expect(CORRIDORS.map((c) => c.country)).toEqual(["GH", "ZW", "ZM", "KE", "NG", "UG"]);
  });

  it("includes activity status filters with refunded", () => {
    const labels = ACTIVITY_STATUS_FILTERS.map((f) => f.label);
    expect(labels).toContain("Refunded");
    expect(labels).toContain("Failed");
  });

  it("defines beneficiary payout categories", () => {
    expect(BENEFICIARY_CATEGORIES.map((c) => c.value)).toContain("mobile_money");
    expect(BENEFICIARY_CATEGORIES.map((c) => c.value)).toContain("cash_pickup");
  });

  it("defines KYC workflow states", () => {
    expect(KYC_WORKFLOW_STATES.map((s) => s.value)).toEqual(["draft", "submitted", "reviewing", "approved", "rejected"]);
  });

  it("defines user tiers with limits", () => {
    expect(USER_TIERS).toHaveLength(3);
    expect(USER_TIERS[0].limit).toMatch(/R/);
  });
});
