/** TransAfrik Remit — design tokens (Wise / Remitly / Revolut tier) */

export const tokens = {
  brand: {
    green: "#1B5E3B",
    greenDark: "#0D3D24",
    greenLight: "#2D9660",
    gold: "#C9A227",
    goldLight: "#E8D48A",
  },
  motion: {
    fast: 150,
    normal: 250,
    slow: 400,
  },
  hitSlop: { top: 12, bottom: 12, left: 12, right: 12 },
  tabBarHeight: 64,
  headerHeight: 56,
  maxContentWidth: 480,
} as const;

export type DesignTokens = typeof tokens;
