import { Grid, Card, CardContent, Typography, Box, alpha, useTheme, CircularProgress } from '@mui/material';
import {
  TrendingUp,
  Description,
  CloudUpload,
  QuestionAnswer,
  CheckCircle,

} from '@mui/icons-material';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { useDashboardData } from '../hooks/useDashboardData';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Modern Stat Card
function ModernStatCard({ title, value, subtitle, icon, color, trend }: any) {
  return (
    <Card
      sx={{
        position: 'relative',
        overflow: 'hidden',
        height: '100%',
        minHeight: 220,
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: `0 20px 40px ${alpha(color, 0.3)}`,
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '6px',
          background: `linear-gradient(90deg, ${color}, ${alpha(color, 0.6)})`,
        },
      }}
    >
      <CardContent sx={{ p: 4, pt: 5, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box
            sx={{
              width: 80,
              height: 80,
              borderRadius: 3,
              background: `linear-gradient(135deg, ${alpha(color, 0.2)}, ${alpha(color, 0.05)})`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
          {trend && (
            <Box
              sx={{
                px: 2.5,
                py: 1,
                borderRadius: 2.5,
                bgcolor: trend > 0 ? alpha('#10b981', 0.15) : alpha('#ef4444', 0.15),
                color: trend > 0 ? '#10b981' : '#ef4444',
              }}
            >
              <Typography variant="body1" fontWeight={700}>
                {trend > 0 ? '+' : ''}{trend}%
              </Typography>
            </Box>
          )}
        </Box>

        <Box>
          <Typography 
            variant="h1" 
            fontWeight={800} 
            color="text.primary" 
            gutterBottom 
            sx={{ 
              fontSize: '3.5rem',
              lineHeight: 1,
              mb: 2
            }}
          >
            {value}
          </Typography>

          <Typography variant="h6" color="text.secondary" fontWeight={600} sx={{ mb: 0.5 }}>
            {title}
          </Typography>

          {subtitle && (
            <Typography variant="body2" color="text.secondary" display="block" sx={{ opacity: 0.7 }}>
              {subtitle}
            </Typography>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

// Activity Chart Component
function ActivityLineChart({ data: chartData }: { data: { labels: string[]; documents: number[]; questions: number[] } }) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const data = {
    labels: chartData.labels,
    datasets: [
      {
        label: 'Documents',
        data: chartData.documents,
        borderColor: '#3b82f6',
        backgroundColor: alpha('#3b82f6', 0.1),
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#3b82f6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
      {
        label: 'Questions',
        data: chartData.questions,
        borderColor: '#8b5cf6',
        backgroundColor: alpha('#8b5cf6', 0.1),
        fill: true,
        tension: 0.4,
        borderWidth: 3,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#8b5cf6',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
          color: isDark ? '#e2e8f0' : '#1e293b',
          font: {
            size: 13,
            weight: '500',
          },
        },
      },
      tooltip: {
        backgroundColor: isDark ? '#1e293b' : '#ffffff',
        titleColor: isDark ? '#e2e8f0' : '#1e293b',
        bodyColor: isDark ? '#94a3b8' : '#64748b',
        borderColor: isDark ? '#334155' : '#e2e8f0',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6,
        usePointStyle: true,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: isDark ? alpha('#e2e8f0', 0.05) : alpha('#1e293b', 0.05),
          drawBorder: false,
        },
        ticks: {
          color: isDark ? '#94a3b8' : '#64748b',
          font: {
            size: 12,
          },
          stepSize: 1,
          precision: 0,
        },
        border: {
          display: false,
        },
      },
      x: {
        grid: {
          display: false,
          drawBorder: false,
        },
        ticks: {
          color: isDark ? '#94a3b8' : '#64748b',
          font: {
            size: 12,
          },
        },
        border: {
          display: false,
        },
      },
    },
  };

  // Check if there's any data
  const hasData = chartData.documents.some((v: number) => v > 0) || chartData.questions.some((v: number) => v > 0);

  return (
    <Card>
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Activité de la semaine
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Suivi de vos documents et questions
          </Typography>
        </Box>
        <Box sx={{ height: 440, width: '100%', maxWidth: '100%' }}>
          {hasData ? (
            <Line data={data} options={options} />
          ) : (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center'
            }}>
              <Box sx={{
                width: 64,
                height: 64,
                borderRadius: 2,
                bgcolor: 'action.hover',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2
              }}>
                <CloudUpload sx={{ fontSize: 32, color: 'text.secondary' }} />
              </Box>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                Aucune activité cette semaine
              </Typography>
              <Typography variant="body2" color="text.disabled">
                Vos statistiques apparaîtront ici une fois que vous aurez téléchargé des documents
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

// Document Types Doughnut Chart
function DocumentTypeChart({ data: chartData }: { data: { labels: string[]; data: number[] } }) {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const data = {
    labels: chartData.labels,
    datasets: [
      {
        data: chartData.data,
        backgroundColor: [
          alpha('#3b82f6', 0.8),
          alpha('#10b981', 0.8),
          alpha('#f59e0b', 0.8),
          alpha('#8b5cf6', 0.8),
          alpha('#6b7280', 0.8),
        ],
        borderColor: [
          '#3b82f6',
          '#10b981',
          '#f59e0b',
          '#8b5cf6',
          '#6b7280',
        ],
        borderWidth: 2,
        hoverOffset: 10,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom' as const,
        labels: {
          usePointStyle: true,
          padding: 15,
          color: isDark ? '#e2e8f0' : '#1e293b',
          font: {
            size: 12,
            weight: '500',
          },
        },
      },
      tooltip: {
        backgroundColor: isDark ? '#1e293b' : '#ffffff',
        titleColor: isDark ? '#e2e8f0' : '#1e293b',
        bodyColor: isDark ? '#94a3b8' : '#64748b',
        borderColor: isDark ? '#334155' : '#e2e8f0',
        borderWidth: 1,
        padding: 12,
        boxPadding: 6,
      },
    },
    cutout: '65%',
  };

  // Check if there's any data
  const hasData = chartData.data.some((v: number) => v > 0);

  return (
    <Card>
      <CardContent sx={{ p: 4 }}>
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Types de documents
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Répartition par format
          </Typography>
        </Box>
        <Box sx={{ height: 440, width: '100%', maxWidth: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {hasData ? (
            <Doughnut data={data} options={options} />
          ) : (
            <Box sx={{ 
              display: 'flex', 
              flexDirection: 'column', 
              alignItems: 'center', 
              justifyContent: 'center',
              textAlign: 'center'
            }}>
              <Box sx={{
                width: 64,
                height: 64,
                borderRadius: 2,
                bgcolor: 'action.hover',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 2
              }}>
                <Description sx={{ fontSize: 32, color: 'text.secondary' }} />
              </Box>
              <Typography variant="body1" color="text.secondary" gutterBottom>
                Aucun document
              </Typography>
              <Typography variant="body2" color="text.disabled">
                Importez des documents pour voir leur répartition
              </Typography>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
}

// Recent Activity Card
function RecentActivity({ activities }: { activities: Array<{ id: number; type: string; title: string; time: string; color: string }> }) {
  // Show empty state if no activities
  if (!activities || activities.length === 0) {
    return (
      <Card>
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ textAlign: 'center', mb: 2 }}>
            <Typography variant="h6" fontWeight={600} gutterBottom>
              Activité récente
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Vos dernières actions
            </Typography>
          </Box>
          
          <Box sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            alignItems: 'center', 
            justifyContent: 'center',
            py: 6,
            textAlign: 'center'
          }}>
            <Box sx={{
              width: 64,
              height: 64,
              borderRadius: 2,
              bgcolor: 'action.hover',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 2
            }}>
              <QuestionAnswer sx={{ fontSize: 32, color: 'text.secondary' }} />
            </Box>
            <Typography variant="body1" color="text.secondary" gutterBottom>
              Aucune activité récente
            </Typography>
            <Typography variant="body2" color="text.disabled">
              Commencez par télécharger des documents ou poser une question
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardContent sx={{ p: 3 }}>
        <Box sx={{ textAlign: 'center', mb: 2 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Activité récente
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Vos dernières actions
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
          {activities.map((activity) => (
            <Box
              key={activity.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                p: 1.5,
                borderRadius: 2,
                bgcolor: 'background.default',
                border: '1px solid',
                borderColor: 'divider',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.main',
                  transform: 'translateX(4px)',
                },
              }}
            >
              <Box
                sx={{
                  width: 36,
                  height: 36,
                  borderRadius: 2,
                  bgcolor: alpha(activity.color, 0.1),
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                {activity.type === 'upload' && <CloudUpload sx={{ color: activity.color, fontSize: 18 }} />}
                {activity.type === 'question' && <QuestionAnswer sx={{ color: activity.color, fontSize: 18 }} />}
                {activity.type === 'complete' && <CheckCircle sx={{ color: activity.color, fontSize: 18 }} />}
              </Box>
              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="body2" fontWeight={500} noWrap>
                  {activity.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {activity.time}
                </Typography>
              </Box>
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}

// Main Dashboard
export default function ProfessionalDashboard() {
  const { data: dashboardData, isLoading, error } = useDashboardData();

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error || !dashboardData) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh', px: 3 }}>
        <Card sx={{ maxWidth: 500, width: '100%' }}>
          <CardContent sx={{ textAlign: 'center', p: 4 }}>
            <Typography variant="h6" color="error" gutterBottom>
              Erreur de chargement
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Impossible de charger les données du tableau de bord. Vérifiez que le backend est démarré.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    );
  }

  const { stats, activity, documentTypes, recentActivities } = dashboardData;

  return (
    <Box sx={{ 
      width: '100%',
      minHeight: '100vh',
      display: 'flex',
      justifyContent: 'center',
      px: 3
    }}>
      <Box sx={{ maxWidth: 1600, width: '100%' }}>
        {/* Header */}
        <Box sx={{ mb: 5, textAlign: 'center' }}>
          <Typography variant="h4" fontWeight={700} color="text.primary" gutterBottom>
            Tableau de bord
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Bienvenue, voici un aperçu de votre activité médicale
          </Typography>
        </Box>

        {/* Stats Grid - Full Width Centered */}
        <Grid container spacing={9} sx={{ mb: 5, justifyContent: 'center' }}>
          <Grid item xs={12} sm={6} md={3}>
            <ModernStatCard
              title="Total Documents"
              value={stats.totalDocuments.toString()}
              subtitle="Documents médicaux"
              icon={<Description sx={{ fontSize: 42, color: '#3b82f6' }} />}
              color="#3b82f6"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <ModernStatCard
              title="Imports ce mois"
              value={stats.monthlyUploads.toString()}
              subtitle="Nouveaux fichiers"
              icon={<CloudUpload sx={{ fontSize: 42, color: '#10b981' }} />}
              color="#10b981"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <ModernStatCard
              title="Questions posées"
              value={stats.totalQuestions.toString()}
              subtitle="Interactions IA"
              icon={<QuestionAnswer sx={{ fontSize: 42, color: '#8b5cf6' }} />}
              color="#8b5cf6"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <ModernStatCard
              title="Taux de réussite"
              value={`${stats.successRate}%`}
              subtitle="Précision globale"
              icon={<TrendingUp sx={{ fontSize: 42, color: '#f59e0b' }} />}
              color="#f59e0b"
            />
          </Grid>
        </Grid>

        {/* Charts Section - Side by Side, Full Width */}
        <Grid container spacing={9} sx={{ mb: 4, justifyContent: 'center' }}>
          <Grid item xs={12} sm={6} md={6}>
            <ActivityLineChart data={activity} />
          </Grid>
          <Grid item xs={12} sm={6} md={6}>
            <DocumentTypeChart data={documentTypes} />
          </Grid>
        </Grid>

        {/* Recent Activity - Smaller */}
        <Grid container spacing={9} sx={{ justifyContent: 'center' }}>
          <Grid item xs={12}>
            <RecentActivity activities={recentActivities} />
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
}
