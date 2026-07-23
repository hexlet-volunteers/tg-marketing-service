import { type MantineThemeOverride } from '@mantine/core';

export const theme: MantineThemeOverride = {
  primaryColor: 'tgblue',

  colors: {
    primary: [
      '#f1f3f5', '#e9ecef', '#dee2e6', '#ced4da', '#adb5bd',
      '#1a1b1e', '#151619', '#111214', '#0d0e10', '#101216',
    ],
    secondary: [
      '#f8f9fa', '#f1f3f5', '#e9ecef', '#dee2e6', '#ced4da',
      '#495057', '#414850', '#3a3f47', '#33383e', '#2c3036',
    ],
    muted: [
      '#f8f9fa', '#f1f3f5', '#e9ecef', '#dee2e6', '#adb5bd',
      '#868e96', '#7a828a', '#6e767e', '#636a72', '#585f67',
    ],
    tgblue: [
      '#E7F5FB', '#D0EBF9', '#A8D8F0', '#7CC3E6', '#4DADD9',
      '#229ED9', '#1B87BC', '#166FA3', '#115888', '#0B4F6A',
    ],
    tgpurple: [
      '#F3F0FF', '#E6E0FB', '#D0CCF5', '#B5ABED', '#9584E4',
      '#7048E8', '#5F35D6', '#4E28BF', '#3F1FA5', '#3B1F8E',
    ],
    tggreen: [
      '#E6FCF5', '#C3F0D9', '#93E2B8', '#66D399', '#3FC47B',
      '#2F9E44', '#27923B', '#1F7E33', '#1A6D2B', '#1B5E20',
    ],
    tgred: [
      '#FFF5F5', '#FFE3E3', '#FFC9C9', '#FFA8A8', '#FF8787',
      '#E03131', '#C92A2A', '#B02525', '#982020', '#8B1A1A',
    ],
    tgorange: [
      '#FFF4E6', '#FFE8CC', '#FFD8A8', '#FFC078', '#FFA94D',
      '#F08C00', '#E8590C', '#D9480F', '#C2410C', '#8B4000',
    ],
  },

  shadows: {
    xs: '0 1px 2px rgba(16,18,22,.05)',
    sm: '0 1px 3px rgba(16,18,22,.06)',
    md: '0 2px 6px rgba(16,18,22,.08)',
    lg: '0 4px 12px rgba(16,18,22,.08)',
    xl: '0 8px 24px rgba(16,18,22,.10)',
    heroCard: '0 8px 24px rgba(16,18,22,.10)',
    featureCard: '0 1px 3px rgba(16,18,22,.06)',
    modal: '0 24px 70px rgba(0,0,0,.3)',
  },

  fontFamily: "'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  fontFamilyMonospace: "'JetBrains Mono', ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace",
  headings: {
    fontFamily: "'Manrope', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
    sizes: {
      h1: { fontSize: '44px', fontWeight: '800', lineHeight: '1.15' },
      h2: { fontSize: '32px', fontWeight: '800', lineHeight: '1.3' },
      h3: { fontSize: '16px', fontWeight: '800', lineHeight: '1.4' },
      h4: { fontSize: '14px', fontWeight: '700', lineHeight: '1.4' },
    },
  },

  components: {
    Card: {
      defaultProps: {
        withBorder: true,
        radius: 'lg',
      },
      styles: {
        root: {
          cursor: 'pointer',
        },
      },
    },

    Paper: {
      defaultProps: {
        withBorder: true,
        radius: 'lg',
      },
    },

    Container: {
      defaultProps: {
        px: { base: 20 },
        py: { base: 40 },
      },
    },

    Heading: {
      styles: {
        root: {
          letterSpacing: '-0.02em',
        },
      },
    },

  },
};

export const avatarGradients = {
  default: { from: 'tgblue', to: 'tgpurple', deg: 135 },
  tech: { from: 'tgblue', to: 'tgpurple', deg: 135 },
  crypto: { from: '#f76707', to: 'tgorange.6', deg: 135 },
  marketing: { from: '#12b886', to: '#0ca678', deg: 135 },
  psychology: { from: '#f783ac', to: '#e64980', deg: 135 },
  business: { from: 'tgblue', to: '#12b886', deg: 135 },
  sport: { from: '#f76707', to: 'tgblue', deg: 135 },
  books: { from: 'tgpurple', to: '#f783ac', deg: 135 },
};
