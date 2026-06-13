/** Future-ready partner provider registry (mock on backend). */
import { PARTNER_PROVIDERS } from "../types";

export const partnerService = {
  list() {
    return PARTNER_PROVIDERS.map((code) => ({
      code,
      name: code.charAt(0).toUpperCase() + code.slice(1),
      status: "mock" as const,
    }));
  },
};
