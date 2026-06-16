import { isValidPassword, isValidPin, isValidGhanaMobile, isValidDateOfBirth } from "../src/utils/validation";
import { FLUTTERWAVE_METHOD_CODES } from "../src/utils/compliance";

describe("production validation", () => {
  it("validates 4-digit PINs", () => {
    expect(isValidPin("1234")).toBe(true);
    expect(isValidPin("12")).toBe(false);
    expect(isValidPin("abcd")).toBe(false);
  });

  it("requires 8+ char passwords for legacy email login", () => {
    expect(isValidPassword("short")).toBe(false);
    expect(isValidPassword("secure123")).toBe(true);
  });

  it("validates Ghana mobile numbers", () => {
    expect(isValidGhanaMobile("0241234567")).toBe(true);
    expect(isValidGhanaMobile("123")).toBe(false);
  });

  it("validates date of birth", () => {
    expect(isValidDateOfBirth("1990-05-15")).toBe(true);
    expect(isValidDateOfBirth("2020-01-01")).toBe(false);
  });

  it("identifies Flutterwave payment codes", () => {
    expect(FLUTTERWAVE_METHOD_CODES.has("flutterwave")).toBe(true);
    expect(FLUTTERWAVE_METHOD_CODES.has("pay_at")).toBe(false);
  });
});
