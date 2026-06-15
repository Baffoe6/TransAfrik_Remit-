import { useQuery } from "@tanstack/react-query";
import { transfersApi } from "../api/transfers";
import { useDebounce } from "./useDebounce";

export function useLiveQuote(amount: string, destinationCountry: string, enabled = true) {
  const debouncedAmount = useDebounce(amount, 500);
  const numeric = parseFloat(debouncedAmount);
  const valid = enabled && !Number.isNaN(numeric) && numeric >= 50;

  return useQuery({
    queryKey: ["quote", debouncedAmount, destinationCountry],
    queryFn: async () => (await transfersApi.calculate(debouncedAmount, destinationCountry)).data,
    enabled: valid,
    staleTime: 30_000,
    retry: 1,
  });
}
