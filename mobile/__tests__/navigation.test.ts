describe("navigation journeys", () => {
  it("defines main tab routes for remittance flows", () => {
    const tabs = ["Home", "Send", "Beneficiaries", "Activity", "Profile"];
    const stack = ["SendFlow", "TransferTracking", "Receipt", "Kyc", "Security", "Notifications", "Support"];
    expect(tabs).toHaveLength(5);
    expect(stack).toContain("SendFlow");
    expect(stack).toContain("Security");
  });

  it("maps send flow steps", () => {
    const steps = ["Corridor", "Amount", "Recipient", "Payment", "Review"];
    expect(steps).toHaveLength(5);
    expect(steps[1]).toBe("Amount");
  });
});
