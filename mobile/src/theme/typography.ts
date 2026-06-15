import { TextStyle } from "react-native";

export const typography = {
  display: { fontSize: 34, fontWeight: "800" as TextStyle["fontWeight"], letterSpacing: -0.8, lineHeight: 40 },
  displaySm: { fontSize: 28, fontWeight: "800" as TextStyle["fontWeight"], letterSpacing: -0.5, lineHeight: 34 },
  h1: { fontSize: 26, fontWeight: "700" as TextStyle["fontWeight"], letterSpacing: -0.3, lineHeight: 32 },
  h2: { fontSize: 20, fontWeight: "700" as TextStyle["fontWeight"], letterSpacing: -0.2, lineHeight: 26 },
  h3: { fontSize: 17, fontWeight: "600" as TextStyle["fontWeight"], lineHeight: 22 },
  body: { fontSize: 16, fontWeight: "400" as TextStyle["fontWeight"], lineHeight: 24 },
  bodyBold: { fontSize: 16, fontWeight: "600" as TextStyle["fontWeight"], lineHeight: 24 },
  bodySm: { fontSize: 14, fontWeight: "400" as TextStyle["fontWeight"], lineHeight: 20 },
  caption: { fontSize: 13, fontWeight: "400" as TextStyle["fontWeight"], lineHeight: 18 },
  label: { fontSize: 12, fontWeight: "600" as TextStyle["fontWeight"], letterSpacing: 0.6, textTransform: "uppercase" as TextStyle["textTransform"], lineHeight: 16 },
  button: { fontSize: 16, fontWeight: "600" as TextStyle["fontWeight"], letterSpacing: 0.1 },
  amount: { fontSize: 40, fontWeight: "800" as TextStyle["fontWeight"], letterSpacing: -1.2, lineHeight: 48 },
  amountSm: { fontSize: 28, fontWeight: "700" as TextStyle["fontWeight"], letterSpacing: -0.6, lineHeight: 34 },
  tab: { fontSize: 11, fontWeight: "600" as TextStyle["fontWeight"], letterSpacing: 0.2 },
} as const;
