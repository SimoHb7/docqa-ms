import React, { useState } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  Chip,
  TextField,
  InputAdornment,
  Button,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { auditApi } from '../services/api';
import { formatDate } from '../utils';
import { AuditLog } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import CardComponent from '../components/ui/Card';

const AuditLogs: React.FC = () => {
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(25);
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [resourceTypeFilter, setResourceTypeFilter] = useState('');

  // Fetch audit logs
  const { data: auditData, isLoading, error } = useQuery({
    queryKey: ['audit-logs', page, rowsPerPage, actionFilter, resourceTypeFilter, searchQuery],
    queryFn: () =>
      auditApi.getLogs({
        action: actionFilter || undefined,
        resource_type: resourceTypeFilter || undefined,
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      }),
  });

  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    setPage(0);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setActionFilter('');
    setResourceTypeFilter('');
    setPage(0);
  };

  const getActionColor = (action: string): 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' => {
    const actionColors: Record<string, any> = {
      document_upload: 'success',
      document_delete: 'error',
      search_query: 'info',
      qa_question: 'primary',
      login: 'success',
      logout: 'warning',
    };
    return actionColors[action] || 'default';
  };

  const getActionLabel = (action: string): string => {
    const actionLabels: Record<string, string> = {
      document_upload: 'Téléchargement',
      document_delete: 'Suppression',
      search_query: 'Recherche',
      qa_question: 'Question Q&R',
      login: 'Connexion',
      logout: 'Déconnexion',
      document_view: 'Consultation',
      synthesis_create: 'Synthèse',
    };
    return actionLabels[action] || action.replace('_', ' ');
  };

  const getResourceTypeLabel = (resourceType: string): string => {
    const typeLabels: Record<string, string> = {
      document: 'Document',
      query: 'Requête',
      user: 'Utilisateur',
      session: 'Session',
      synthesis: 'Synthèse',
    };
    return typeLabels[resourceType] || resourceType;
  };

  if (isLoading) {
    return <LoadingSpinner message="Chargement des logs d'audit..." />;
  }

  if (error) {
    return (
      <Box textAlign="center" py={4}>
        <Typography color="error">
          Erreur lors du chargement des logs d'audit
        </Typography>
      </Box>
    );
  }

  const logs = auditData?.data || [];

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
            Logs d'audit
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Historique des activités et événements système
          </Typography>
        </Box>
        <SecurityIcon sx={{ fontSize: 40, color: 'primary.main' }} />
      </Box>

      {/* Filters */}
      <CardComponent sx={{ mb: 3 }}>
        <Box p={2}>
          <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
            <TextField
              placeholder="Rechercher dans les logs..."
              value={searchQuery}
              onChange={handleSearchChange}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ minWidth: 300 }}
            />

            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Action</InputLabel>
              <Select
                value={actionFilter}
                onChange={(e) => setActionFilter(e.target.value)}
                label="Action"
              >
                <MenuItem value="">Toutes</MenuItem>
                <MenuItem value="document_upload">Téléchargement</MenuItem>
                <MenuItem value="document_delete">Suppression</MenuItem>
                <MenuItem value="search_query">Recherche</MenuItem>
                <MenuItem value="qa_question">Question Q&R</MenuItem>
                <MenuItem value="login">Connexion</MenuItem>
                <MenuItem value="logout">Déconnexion</MenuItem>
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 150 }}>
              <InputLabel>Type de ressource</InputLabel>
              <Select
                value={resourceTypeFilter}
                onChange={(e) => setResourceTypeFilter(e.target.value)}
                label="Type de ressource"
              >
                <MenuItem value="">Tous</MenuItem>
                <MenuItem value="document">Document</MenuItem>
                <MenuItem value="query">Requête</MenuItem>
                <MenuItem value="user">Utilisateur</MenuItem>
                <MenuItem value="session">Session</MenuItem>
              </Select>
            </FormControl>

            {(searchQuery || actionFilter || resourceTypeFilter) && (
              <Button variant="outlined" onClick={clearFilters}>
                Effacer les filtres
              </Button>
            )}
          </Box>
        </Box>
      </CardComponent>

      {/* Audit Logs Table */}
      <CardComponent>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date & Heure</TableCell>
                <TableCell>Utilisateur</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Ressource</TableCell>
                <TableCell>Détails</TableCell>
                <TableCell>IP</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.map((log) => (
                <TableRow key={log.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {formatDate(log.timestamp)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {log.user_name || log.user_id}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={getActionLabel(log.action)}
                      size="small"
                      color={getActionColor(log.action)}
                      variant="outlined"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {getResourceTypeLabel(log.resource_type)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ID: {log.resource_id.slice(-8)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ maxWidth: 200 }}>
                      {log.details?.query ||
                       log.details?.filename ||
                       log.details?.question ||
                       'N/A'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" fontFamily="monospace">
                      {log.ip_address || 'N/A'}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
              {logs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      Aucun log d'audit trouvé
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          component="div"
          count={auditData?.total || 0}
          page={page}
          onPageChange={handlePageChange}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleRowsPerPageChange}
          labelRowsPerPage="Lignes par page:"
          labelDisplayedRows={({ from, to, count }) =>
            `${from}-${to} sur ${count !== -1 ? count : `plus de ${to}`}`
          }
        />
      </CardComponent>

      {/* Security Notice */}
      <CardComponent sx={{ mt: 3 }}>
        <Box p={2}>
          <Typography variant="h6" color="primary" gutterBottom>
            Sécurité et confidentialité
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Les logs d'audit enregistrent toutes les activités importantes pour assurer la traçabilité
            et la sécurité des données médicales. Ces informations sont conservées de manière sécurisée
            et ne sont accessibles qu'aux utilisateurs autorisés.
          </Typography>
        </Box>
      </CardComponent>
    </Box>
  );
};

export default AuditLogs;