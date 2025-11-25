import React from 'react';
import {
  Box,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  Avatar,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
} from '@mui/material';
import {
  Description as DocumentIcon,
  QuestionAnswer as QAIcon,
  Assessment as SynthesisIcon,
  TrendingUp as TrendingIcon,
  Upload as UploadIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from '../services/api';
import { formatRelativeTime, getProcessingStatusColor } from '../utils';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import CardComponent from '../components/ui/Card';

const Dashboard: React.FC = () => {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: dashboardApi.getStats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: activity } = useQuery({
    queryKey: ['recent-activity'],
    queryFn: () => dashboardApi.getRecentActivity(10),
  });

  if (isLoading) {
    return <LoadingSpinner message="Chargement du tableau de bord..." />;
  }

  if (error) {
    return (
      <Box textAlign="center" py={4}>
        <Typography color="error">
          Erreur lors du chargement des données du tableau de bord
        </Typography>
      </Box>
    );
  }

  const statCards = [
    {
      title: 'Documents',
      value: stats?.totalDocuments || 0,
      icon: <DocumentIcon fontSize="large" />,
      color: 'primary',
      subtitle: 'Total des documents',
    },
    {
      title: 'Questions',
      value: stats?.totalQuestions || 0,
      icon: <QAIcon fontSize="large" />,
      color: 'secondary',
      subtitle: 'Questions posées',
    },
    {
      title: 'Fiabilité moyenne',
      value: `${Math.round(stats?.averageConfidence || 0)}%`,
      icon: <TrendingIcon fontSize="large" />,
      color: 'success',
      subtitle: 'Confiance des réponses',
    },
    {
      title: 'Temps de réponse',
      value: `${Math.round(stats?.averageResponseTime || 0)}ms`,
      icon: <SynthesisIcon fontSize="large" />,
      color: 'info',
      subtitle: 'Moyenne des réponses',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
        Tableau de bord
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Vue d'ensemble de votre activité sur InterfaceClinique
      </Typography>

      {/* Stats Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: 'repeat(2, 1fr)',
            md: 'repeat(4, 1fr)',
          },
          gap: 3,
          mb: 4,
        }}
      >
        {statCards.map((stat, index) => (
          <CardComponent key={index}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h4" component="div" fontWeight={700}>
                    {stat.value}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stat.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {stat.subtitle}
                  </Typography>
                </Box>
                <Avatar
                  sx={{
                    bgcolor: `${stat.color}.main`,
                    width: 48,
                    height: 48,
                  }}
                >
                  {stat.icon}
                </Avatar>
              </Box>
            </CardContent>
          </CardComponent>
        ))}
      </Box>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' },
          gap: 3,
        }}
      >
        {/* Document Status Distribution */}
        <CardComponent title="État des documents">
            <CardContent>
              {stats?.documentsByStatus && Object.entries(stats.documentsByStatus).map(([status, count]) => (
                <Box key={status} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                    <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                      {status.replace('_', ' ')}
                    </Typography>
                    <Chip
                      label={count}
                      size="small"
                      sx={{
                        bgcolor: getProcessingStatusColor(status),
                        color: 'white',
                      }}
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(count / (stats.totalDocuments || 1)) * 100}
                    sx={{
                      height: 8,
                      borderRadius: 4,
                      bgcolor: 'grey.200',
                      '& .MuiLinearProgress-bar': {
                        bgcolor: getProcessingStatusColor(status),
                        borderRadius: 4,
                      },
                    }}
                  />
                </Box>
              ))}
            </CardContent>
          </CardComponent>

        {/* Recent Activity */}
        <CardComponent title="Activité récente">
            <CardContent sx={{ p: 0 }}>
              <List>
                {activity?.map((item, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemAvatar>
                        <Avatar sx={{ bgcolor: 'primary.main' }}>
                          {item.type === 'upload' && <UploadIcon />}
                          {item.type === 'question' && <QAIcon />}
                          {item.type === 'search' && <SearchIcon />}
                        </Avatar>
                      </ListItemAvatar>
                      <ListItemText
                        primary={item.details}
                        secondary={formatRelativeTime(item.timestamp)}
                        primaryTypographyProps={{
                          variant: 'body2',
                          fontWeight: 500,
                        }}
                        secondaryTypographyProps={{
                          variant: 'caption',
                        }}
                      />
                    </ListItem>
                    {index < (activity.length - 1) && <Divider variant="inset" />}
                  </React.Fragment>
                ))}
                {!activity?.length && (
                  <ListItem>
                    <ListItemText
                      primary="Aucune activité récente"
                      secondary="Les nouvelles activités apparaîtront ici"
                      primaryTypographyProps={{
                        variant: 'body2',
                        color: 'text.secondary',
                      }}
                      secondaryTypographyProps={{
                        variant: 'caption',
                        color: 'text.secondary',
                      }}
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </CardComponent>
      </Box>

      {/* Document Types Distribution */}
      <Box sx={{ mt: 3 }}>
        <CardComponent title="Répartition par type de document">
          <CardContent>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: {
                  xs: 'repeat(2, 1fr)',
                  sm: 'repeat(3, 1fr)',
                  md: 'repeat(4, 1fr)',
                },
                gap: 2,
              }}
            >
              {stats?.documentsByType && Object.entries(stats.documentsByType).map(([type, count]) => (
                <Box key={type} textAlign="center">
                  <Typography variant="h5" fontWeight={600}>
                    {count}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {type.replace('_', ' ')}
                  </Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </CardComponent>
      </Box>
    </Box>
  );
};

export default Dashboard;