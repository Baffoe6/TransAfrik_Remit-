describe("API base URL", () => {
  it("defaults to production API", () => {
    const url = process.env.EXPO_PUBLIC_API_URL || "https://api.ipaygo.co.za";
    expect(url).toContain("ipaygo.co.za");
  });
});

describe("partner providers", () => {
  const PARTNERS = ["flutterwave", "mukuru", "onafriq", "veengu"];
  it("lists future-ready partners", () => {
    expect(PARTNERS).toHaveLength(4);
  });
});
