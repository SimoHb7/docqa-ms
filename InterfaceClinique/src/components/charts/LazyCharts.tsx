import { lazy, Suspense } from 'react';
import { Box, CircularProgress } from '@mui/material';

// Lazy load Chart.js components to reduce initial bundle size
const Line = lazy(() => import('react-chartjs-2').then(module => ({ default: module.Line })));
const Doughnut = lazy(() => import('react-chartjs-2').then(module => ({ default: module.Doughnut })));
const Bar = lazy(() => import('react-chartjs-2').then(module => ({ default: module.Bar })));

// Loading fallback
const ChartLoader = () => (
  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 300 }}>
    <CircularProgress size={40} />
  </Box>
);

// Lazy wrapped components with suspense
export const LazyLine = (props: any) => (
  <Suspense fallback={<ChartLoader />}>
    <Line {...props} />
  </Suspense>
);

export const LazyDoughnut = (props: any) => (
  <Suspense fallback={<ChartLoader />}>
    <Doughnut {...props} />
  </Suspense>
);

export const LazyBar = (props: any) => (
  <Suspense fallback={<ChartLoader />}>
    <Bar {...props} />
  </Suspense>
);
