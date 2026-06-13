import { create } from "zustand";
import type { TransferQuote } from "../api/transfers";
import type { PaymentMethod } from "../api/payments";
import type { Beneficiary } from "../types";

export interface SendFlowState {
  step: number;
  destinationCountry: string;
  corridorCode: string;
  currency: string;
  amount: string;
  quote: TransferQuote | null;
  beneficiary: Beneficiary | null;
  paymentMethod: PaymentMethod | null;
  transferId: number | null;
  reset: () => void;
  setStep: (step: number) => void;
  setDestination: (country: string, code: string, currency: string) => void;
  setAmount: (amount: string) => void;
  setQuote: (quote: TransferQuote | null) => void;
  setBeneficiary: (b: Beneficiary | null) => void;
  setPaymentMethod: (m: PaymentMethod | null) => void;
  setTransferId: (id: number) => void;
}

const initial = {
  step: 1,
  destinationCountry: "GH",
  corridorCode: "ZA-GH",
  currency: "GHS",
  amount: "1000",
  quote: null as TransferQuote | null,
  beneficiary: null as Beneficiary | null,
  paymentMethod: null as PaymentMethod | null,
  transferId: null as number | null,
};

export const useSendFlowStore = create<SendFlowState>((set) => ({
  ...initial,
  reset: () => set(initial),
  setStep: (step) => set({ step }),
  setDestination: (destinationCountry, corridorCode, currency) =>
    set({ destinationCountry, corridorCode, currency, quote: null }),
  setAmount: (amount) => set({ amount, quote: null }),
  setQuote: (quote) => set({ quote }),
  setBeneficiary: (beneficiary) => set({ beneficiary }),
  setPaymentMethod: (paymentMethod) => set({ paymentMethod }),
  setTransferId: (transferId) => set({ transferId }),
}));
