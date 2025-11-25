// Temporary type fix for MUI v7 Grid component
// MUI v7 changed Grid API but TypeScript definitions are strict
// This file adds back the old props for backwards compatibility during migration

import '@mui/material';

declare module '@mui/material/Grid' {
  interface GridProps {
    item?: boolean;
    container?: boolean;
    xs?: boolean | number;
    sm?: boolean | number;
    md?: boolean | number;
    lg?: boolean | number;
    xl?: boolean | number;
  }
}

export {};
