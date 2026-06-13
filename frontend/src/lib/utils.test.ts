import { describe, expect, it } from "vitest";
import { cn, formatCurrency } from "./utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("px-2", "py-1")).toContain("px-2");
    expect(cn("px-2", "px-4")).toContain("px-4");
  });
});

describe("formatCurrency", () => {
  it("formats ZAR amounts", () => {
    const formatted = formatCurrency("1000", "ZAR");
    expect(formatted).toMatch(/1[\s,]?000/);
    expect(formatted).toMatch(/R/);
  });

  it("accepts numeric input", () => {
    expect(formatCurrency(50.5, "ZAR")).toMatch(/50/);
  });
});
