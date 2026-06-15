import { useCalculatorStore } from "../src/store/calculatorStore";

describe("calculatorStore", () => {
  beforeEach(() => {
    useCalculatorStore.setState({
      corridorCode: "ZA-GH",
      destinationCountry: "GH",
      currency: "GHS",
      sendAmount: "1000",
    });
  });

  it("updates corridor selection", () => {
    useCalculatorStore.getState().setCorridor("ZA-KE", "KE", "KES");
    const s = useCalculatorStore.getState();
    expect(s.corridorCode).toBe("ZA-KE");
    expect(s.destinationCountry).toBe("KE");
    expect(s.currency).toBe("KES");
  });

  it("updates send amount", () => {
    useCalculatorStore.getState().setSendAmount("2500");
    expect(useCalculatorStore.getState().sendAmount).toBe("2500");
  });
});
