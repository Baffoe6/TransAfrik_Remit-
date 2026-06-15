import { create } from "zustand";
import { CORRIDORS } from "../utils/constants";

const defaultCorridor = CORRIDORS[0];

interface CalculatorState {
  corridorCode: string;
  destinationCountry: string;
  currency: string;
  sendAmount: string;
  setCorridor: (code: string, country: string, currency: string) => void;
  setSendAmount: (amount: string) => void;
}

export const useCalculatorStore = create<CalculatorState>((set) => ({
  corridorCode: defaultCorridor.code,
  destinationCountry: defaultCorridor.country,
  currency: defaultCorridor.currency,
  sendAmount: "1000",
  setCorridor: (corridorCode, destinationCountry, currency) =>
    set({ corridorCode, destinationCountry, currency }),
  setSendAmount: (sendAmount) => set({ sendAmount }),
}));
