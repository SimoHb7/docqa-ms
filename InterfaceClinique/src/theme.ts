import { createTheme } from '@mui/material/styles';

// Professional medical theme with excellent dark mode
const getTheme = (mode: 'light' | 'dark' | 'system' = 'system') => {
  const isDark = mode === 'dark' || (mode === 'system' && window.matchMedia?.('(prefers-color-scheme: dark)').matches);

  return createTheme({
    palette: {
      mode: isDark ? 'dark' : 'light',
      primary: {
        main: isDark ? '#3b82f6' : '#2563eb', // Brighter blue for dark mode
        light: '#60a5fa',
        dark: '#1d4ed8',
        contrastText: '#ffffff',
      },
      secondary: {
        main: isDark ? '#8b5cf6' : '#7c3aed', // Purple accent
        light: '#a78bfa',
        dark: '#6d28d9',
        contrastText: '#ffffff',
      },
      success: {
        main: isDark ? '#10b981' : '#059669',
        light: '#34d399',
        dark: '#047857',
      },
      warning: {
        main: isDark ? '#f59e0b' : '#d97706',
        light: '#fbbf24',
        dark: '#b45309',
      },
      error: {
        main: isDark ? '#ef4444' : '#dc2626',
        light: '#f87171',
        dark: '#b91c1c',
      },
      info: {
        main: isDark ? '#06b6d4' : '#0891b2',
        light: '#22d3ee',
        dark: '#0e7490',
      },
      background: {
        default: isDark ? '#0a0e1a' : '#f8fafc',
        paper: isDark ? '#111827' : '#ffffff',
      },
      text: {
        primary: isDark ? '#e2e8f0' : '#1e293b',
        secondary: isDark ? '#94a3b8' : '#64748b',
        disabled: isDark ? '#475569' : '#cbd5e1',
      },
      divider: isDark ? '#1e293b' : '#e2e8f0',
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: {
        fontSize: '2.5rem',
        fontWeight: 700,
        lineHeight: 1.2,
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 600,
        lineHeight: 1.3,
      },
      h3: {
        fontSize: '1.75rem',
        fontWeight: 600,
        lineHeight: 1.4,
      },
      h4: {
        fontSize: '1.5rem',
        fontWeight: 600,
        lineHeight: 1.4,
      },
      h5: {
        fontSize: '1.25rem',
        fontWeight: 600,
        lineHeight: 1.5,
      },
      h6: {
        fontSize: '1.125rem',
        fontWeight: 600,
        lineHeight: 1.5,
      },
      body1: {
        fontSize: '1rem',
        lineHeight: 1.6,
      },
      body2: {
        fontSize: '0.875rem',
        lineHeight: 1.6,
      },
      button: {
        textTransform: 'none',
        fontWeight: 500,
      },
    },
    shape: {
      borderRadius: 8,
    },
    components: {
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            padding: '8px 16px',
            fontWeight: 500,
            boxShadow: 'none',
            '&:hover': {
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
            },
          },
          contained: {
            '&:hover': {
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            },
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 16,
            boxShadow: isDark
              ? '0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -1px rgba(0, 0, 0, 0.3)'
              : '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
            border: `1px solid ${isDark ? '#1e293b' : '#e2e8f0'}`,
            backgroundColor: isDark ? '#111827' : '#ffffff',
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 12,
          },
        },
      },
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 8,
            },
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 6,
            fontWeight: 500,
          },
        },
      },
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? '#111827' : '#ffffff',
            color: isDark ? '#e2e8f0' : '#1e293b',
            borderBottom: `1px solid ${isDark ? '#1e293b' : '#e2e8f0'}`,
            boxShadow: isDark ? '0 1px 3px 0 rgba(0, 0, 0, 0.5)' : 'none',
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRight: `1px solid ${isDark ? '#1e293b' : '#e2e8f0'}`,
            backgroundColor: isDark ? '#111827' : '#ffffff',
          },
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            margin: '2px 8px',
            '&.Mui-selected': {
              backgroundColor: isDark ? '#334155' : '#f1f5f9',
              '&:hover': {
                backgroundColor: isDark ? '#475569' : '#e2e8f0',
              },
            },
          },
        },
      },
      MuiTableHead: {
        styleOverrides: {
          root: {
            backgroundColor: isDark ? '#1e293b' : '#f8fafc',
            '& .MuiTableCell-head': {
              fontWeight: 600,
              borderBottom: `1px solid ${isDark ? '#334155' : '#e2e8f0'}`,
            },
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: {
            '&:hover': {
              backgroundColor: isDark ? '#1e293b' : '#f8fafc',
            },
          },
        },
      },
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: 12,
          },
        },
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            backgroundColor: isDark ? '#334155' : '#1e293b',
            fontSize: '0.75rem',
          },
        },
      },
    },
  });
};

export default getTheme;