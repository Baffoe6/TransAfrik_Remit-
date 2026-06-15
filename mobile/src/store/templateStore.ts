import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";

export interface TransferTemplate {
  id: string;
  name: string;
  beneficiaryId: number;
  beneficiaryName: string;
  amount: string;
  corridorCode: string;
  destinationCountry: string;
  currency: string;
  createdAt: string;
}

interface TemplateState {
  templates: TransferTemplate[];
  loaded: boolean;
  load: () => Promise<void>;
  saveTemplate: (t: Omit<TransferTemplate, "id" | "createdAt">) => Promise<void>;
  removeTemplate: (id: string) => Promise<void>;
}

const KEY = "transfer_templates";

export const useTemplateStore = create<TemplateState>((set, get) => ({
  templates: [],
  loaded: false,
  load: async () => {
    const raw = await AsyncStorage.getItem(KEY);
    set({ templates: raw ? JSON.parse(raw) : [], loaded: true });
  },
  saveTemplate: async (t) => {
    const entry: TransferTemplate = {
      ...t,
      id: `tpl_${Date.now()}`,
      createdAt: new Date().toISOString(),
    };
    const next = [entry, ...get().templates].slice(0, 10);
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ templates: next });
  },
  removeTemplate: async (id) => {
    const next = get().templates.filter((x) => x.id !== id);
    await AsyncStorage.setItem(KEY, JSON.stringify(next));
    set({ templates: next });
  },
}));
