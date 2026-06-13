export const palette = {
  green900: "#0D3D24",
  green800: "#1B5E3B",
  green700: "#247A4D",
  green600: "#2D9660",
  gold500: "#C9A227",
  gold400: "#D4B84A",
  charcoal900: "#1A1A1A",
  charcoal700: "#374151",
  charcoal500: "#6B7280",
  white: "#FFFFFF",
  offWhite: "#F8FAF9",
  error: "#DC2626",
  success: "#16A34A",
  warning: "#D97706",
  info: "#2563EB",
} as const;

export const lightTheme = {
  ...palette,
  bg: palette.offWhite,
  surface: palette.white,
  text: palette.charcoal900,
  textSecondary: palette.charcoal500,
  border: "#E5E7EB",
  primary: palette.green800,
  primaryDark: palette.green900,
  accent: palette.gold500,
  tabBar: palette.white,
  overlay: "rgba(0,0,0,0.45)",
};

export const darkTheme = {
  ...palette,
  bg: "#0A1410",
  surface: "#152820",
  text: "#F3F4F6",
  textSecondary: "#9CA3AF",
  border: "#2D3748",
  primary: palette.green600,
  primaryDark: palette.green800,
  accent: palette.gold400,
  tabBar: "#152820",
  overlay: "rgba(0,0,0,0.6)",
};

export type AppTheme = typeof lightTheme;
