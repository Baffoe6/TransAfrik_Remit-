import { create } from "zustand";

type Counter = { count: number; inc: () => void };

const useCounter = create<Counter>((set) => ({
  count: 0,
  inc: () => set((s) => ({ count: s.count + 1 })),
}));

describe("zustand store", () => {
  it("increments state", () => {
    useCounter.getState().inc();
    expect(useCounter.getState().count).toBe(1);
  });
});
