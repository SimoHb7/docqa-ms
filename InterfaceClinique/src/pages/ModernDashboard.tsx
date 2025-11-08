import { Grid, Card, CardContent, Typography, Box, LinearProgress, IconButton, alpha, useTheme, Chip, Avatar, AvatarGroup } from '@mui/material';
import {
  TrendingUp,
  Description,
  CloudUpload,
  QuestionAnswer,
  MoreVert,
  ArrowUpward,
  ArrowDownward,
  AccessTime,
  CheckCircle,
  PendingActions,
} from '@mui/icons-material';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

// Stat Card Component
function StatCard({ title, value, change, trend, icon, color }: any) {
  const theme = useTheme();
  const isPositive = trend === 'up';

  return (
    <Card
      sx={{
        height: '100%',
        background: `linear-gradient(135deg, ${alpha(color, 0.1)} 0%, ${alpha(color, 0.05)} 100%)`,
        border: `1px solid ${alpha(color, 0.2)}`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 12px 24px ${alpha(color, 0.2)}`,
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 2,
              bgcolor: alpha(color, 0.15),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {icon}
          </Box>
          <IconButton size="small">
            <MoreVert fontSize="small" />
          </IconButton>
        </Box>

        <Typography variant="h4" fontWeight={700} gutterBottom>
          {value}
        </Typography>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          {title}
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
          {isPositive ? (
            <ArrowUpward fontSize="small" sx={{ color: 'success.main' }} />
          ) : (
            <ArrowDownward fontSize="small" sx={{ color: 'error.main' }} />
          )}
          <Typography variant="caption" sx={{ color: isPositive ? 'success.main' : 'error.main', fontWeight: 600 }}>
            {change}
          </Typography>
          <Typography variant="caption" color="text.secondary">
            vs mois dernier
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}

// Recent Documents Component
function RecentDocuments() {
  const documents = [
    { id: 1, name: 'Rapport_Patient_001.pdf', date: 'Il y a 2 heures', status: 'processed', type: 'PDF', size: '2.4 MB' },
    { id: 2, name: 'Analyse_Biologique_Marie.docx', date: 'Il y a 5 heures', status: 'processing', type: 'DOCX', size: '1.1 MB' },
    { id: 3, name: 'IRM_Cranienne_Jean.pdf', date: 'Aujourd\'hui', status: 'pending', type: 'PDF', size: '15.2 MB' },
    { id: 4, name: 'Ordonnance_Dupont.pdf', date: 'Hier', status: 'processed', type: 'PDF', size: '0.8 MB' },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed': return 'success';
      case 'processing': return 'warning';
      case 'pending': return 'default';
      default: return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'processed': return 'Traité';
      case 'processing': return 'En cours';
      case 'pending': return 'En attente';
      default: return status;
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6" fontWeight={600}>
            Documents récents
          </Typography>
          <Chip label="Voir tout" size="small" clickable />
        </Box>

        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {documents.map((doc) => (
            <Box
              key={doc.id}
              sx={{
                display: 'flex',
                alignItems: 'center',
                p: 2,
                borderRadius: 2,
                bgcolor: 'background.default',
                border: '1px solid',
                borderColor: 'divider',
                transition: 'all 0.2s',
                '&:hover': {
                  borderColor: 'primary.main',
                  bgcolor: alpha('#1976d2', 0.02),
                },
              }}
            >
              <Avatar
                sx={{
                  width: 44,
                  height: 44,
                  bgcolor: 'primary.main',
                  mr: 2,
                }}
              >
                <Description />
              </Avatar>

              <Box sx={{ flex: 1, minWidth: 0 }}>
                <Typography variant="subtitle2" fontWeight={600} noWrap>
                  {doc.name}
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                  <Typography variant="caption" color="text.secondary">
                    {doc.type} • {doc.size}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    • {doc.date}
                  </Typography>
                </Box>
              </Box>

              <Chip
                label={getStatusLabel(doc.status)}
                color={getStatusColor(doc.status)}
                size="small"
                sx={{ minWidth: 90 }}
              />
            </Box>
          ))}
        </Box>
      </CardContent>
    </Card>
  );
}

// Activity Chart
function ActivityChart() {
  const data = [
    { name: 'Lun', documents: 12, questions: 24 },
    { name: 'Mar', documents: 19, questions: 32 },
    { name: 'Mer', documents: 15, questions: 28 },
    { name: 'Jeu', documents: 25, questions: 45 },
    { name: 'Ven', documents: 22, questions: 38 },
    { name: 'Sam', documents: 8, questions: 15 },
    { name: 'Dim', documents: 5, questions: 10 },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Activité de la semaine
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="documents" fill="#1976d2" radius={[8, 8, 0, 0]} />
            <Bar dataKey="questions" fill="#2e7d32" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// Document Types Pie Chart
function DocumentTypesChart() {
  const data = [
    { name: 'PDF', value: 45, color: '#1976d2' },
    { name: 'DOCX', value: 25, color: '#2e7d32' },
    { name: 'HL7', value: 20, color: '#ed6c02' },
    { name: 'Autres', value: 10, color: '#9c27b0' },
  ];

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" fontWeight={600} gutterBottom>
          Types de documents
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

// Main Dashboard Component
export default function ModernDashboard() {
  const theme = useTheme();

  return (
    <Box>
      {/* Page Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Tableau de bord
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Bienvenue sur votre espace médical. Voici un aperçu de votre activité.
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Documents"
            value="248"
            change="+12.5%"
            trend="up"
            icon={<Description sx={{ fontSize: 28, color: '#1976d2' }} />}
            color="#1976d2"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Imports ce mois"
            value="32"
            change="+8.2%"
            trend="up"
            icon={<CloudUpload sx={{ fontSize: 28, color: '#2e7d32' }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Questions posées"
            value="156"
            change="+24.1%"
            trend="up"
            icon={<QuestionAnswer sx={{ fontSize: 28, color: '#ed6c02' }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Taux de réussite"
            value="94%"
            change="-2.3%"
            trend="down"
            icon={<TrendingUp sx={{ fontSize: 28, color: '#9c27b0' }} />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <ActivityChart />
        </Grid>
        <Grid item xs={12} md={4}>
          <DocumentTypesChart />
        </Grid>
      </Grid>

      {/* Recent Documents */}
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <RecentDocuments />
        </Grid>
      </Grid>
    </Box>
  );
}
