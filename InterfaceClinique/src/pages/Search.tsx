import React, { useState, useMemo } from 'react';
import {
  Box,
  Typography,
  TextField,
  InputAdornment,
  Button,
  Card,
  CardContent,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Alert,
  Paper,
} from '@mui/material';
import {
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
  Description as DocumentIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { useQuery } from '@tanstack/react-query';
import { searchApi } from '../services/api';
import { formatDate, getConfidenceColor, getConfidenceLabel } from '../utils';
import { SearchResult, FilterOptions } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ButtonComponent from '../components/ui/Button';

const Search: React.FC = () => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({});
  const [searchExecuted, setSearchExecuted] = useState(false);

  // Search query
  const { data: searchData, isLoading, error, refetch } = useQuery({
    queryKey: ['search', query, filters],
    queryFn: () => searchApi.search(query, filters),
    enabled: false, // Only run when manually triggered
  });

  const handleSearch = () => {
    if (query.trim()) {
      setSearchExecuted(true);
      refetch();
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const handleFilterChange = (key: keyof FilterOptions, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value || undefined,
    }));
  };

  const clearFilters = () => {
    setFilters({});
  };

  const results = searchData?.results || [];
  const totalResults = searchData?.total || 0;
  const executionTime = searchData?.execution_time_ms || 0;

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
        Recherche sémantique
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Recherchez dans vos documents médicaux avec l'intelligence artificielle
      </Typography>

      {/* Search Input */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box display="flex" gap={2} alignItems="center">
            <TextField
              fullWidth
              placeholder="Ex: hypertension traitement, diabète insulino-résistance, etc."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
              sx={{ flex: 1 }}
            />
            <ButtonComponent
              onClick={handleSearch}
              disabled={!query.trim() || isLoading}
              loading={isLoading}
            >
              Rechercher
            </ButtonComponent>
          </Box>

          {/* Quick Filters */}
          <Box display="flex" gap={1} mt={2} flexWrap="wrap">
            <Chip
              label="Rapports médicaux"
              onClick={() => handleFilterChange('document_type', 'medical_report')}
              variant={filters.document_type === 'medical_report' ? 'filled' : 'outlined'}
              size="small"
            />
            <Chip
              label="Ordonnances"
              onClick={() => handleFilterChange('document_type', 'prescription')}
              variant={filters.document_type === 'prescription' ? 'filled' : 'outlined'}
              size="small"
            />
            <Chip
              label="Résultats labo"
              onClick={() => handleFilterChange('document_type', 'lab_results')}
              variant={filters.document_type === 'lab_results' ? 'filled' : 'outlined'}
              size="small"
            />
            {Object.keys(filters).length > 0 && (
              <Chip
                label="Effacer les filtres"
                onClick={clearFilters}
                variant="outlined"
                color="secondary"
                size="small"
              />
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Search Results */}
      {searchExecuted && (
        <>
          {isLoading && <LoadingSpinner message="Recherche en cours..." />}

          {error && (
            <Alert severity="error" sx={{ mb: 3 }}>
              Erreur lors de la recherche. Veuillez réessayer.
            </Alert>
          )}

          {searchData && !isLoading && (
            <>
              {/* Results Summary */}
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                <Typography variant="h6">
                  {totalResults} résultat{totalResults !== 1 ? 's' : ''} trouvé{totalResults !== 1 ? 's' : ''}
                  {executionTime > 0 && (
                    <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                      ({executionTime}ms)
                    </Typography>
                  )}
                </Typography>
              </Box>

              {/* Results List */}
              {results.length > 0 ? (
                <List>
                  {results.map((result, index) => (
                    <Paper key={result.chunk_id} elevation={1} sx={{ mb: 2 }}>
                      <Accordion>
                        <AccordionSummary
                          expandIcon={<ExpandMoreIcon />}
                          sx={{
                            '& .MuiAccordionSummary-content': {
                              alignItems: 'center',
                              gap: 2,
                            },
                          }}
                        >
                          <Box display="flex" alignItems="center" gap={2} flex={1}>
                            <DocumentIcon color="primary" />
                            <Box flex={1}>
                              <Typography variant="subtitle1" fontWeight={600}>
                                {result.filename || `Document ${result.document_id.slice(-8)}`}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                Score de pertinence: {(result.score * 100).toFixed(1)}%
                              </Typography>
                            </Box>
                            <Chip
                              label={`${getConfidenceLabel(result.score)}`}
                              size="small"
                              sx={{
                                bgcolor: getConfidenceColor(result.score),
                                color: 'white',
                              }}
                            />
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails>
                          <Divider sx={{ mb: 2 }} />

                          {/* Content Preview */}
                          <Box sx={{ mb: 3 }}>
                            <Typography variant="body2" sx={{ mb: 1 }}>
                              <strong>Extrait pertinent :</strong>
                            </Typography>
                            <Paper
                              sx={{
                                p: 2,
                                bgcolor: 'grey.50',
                                borderRadius: 1,
                                fontFamily: 'monospace',
                                fontSize: '0.875rem',
                                lineHeight: 1.5,
                              }}
                            >
                              {result.content}
                            </Paper>
                          </Box>

                          {/* Metadata */}
                          <Box display="flex" gap={2} flexWrap="wrap" alignItems="center">
                            {result.metadata?.page && (
                              <Chip
                                icon={<LocationIcon />}
                                label={`Page ${result.metadata.page}`}
                                size="small"
                                variant="outlined"
                              />
                            )}
                            {result.patient_id && (
                              <Chip
                                label={`Patient: ${result.patient_id}`}
                                size="small"
                                variant="outlined"
                                color="secondary"
                              />
                            )}
                            <Typography variant="caption" color="text.secondary">
                              ID du chunk: {result.chunk_id.slice(-8)}
                            </Typography>
                          </Box>
                        </AccordionDetails>
                      </Accordion>
                    </Paper>
                  ))}
                </List>
              ) : (
                <Paper sx={{ p: 4, textAlign: 'center' }}>
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    Aucun résultat trouvé
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Essayez de reformuler votre recherche ou d'utiliser des termes plus généraux.
                  </Typography>
                </Paper>
              )}
            </>
          )}
        </>
      )}

      {/* Search Tips */}
      {!searchExecuted && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Conseils de recherche
            </Typography>
            <Typography variant="body2" paragraph>
              • Utilisez des termes médicaux précis (ex: "hypertension artérielle", "diabète de type 2")
            </Typography>
            <Typography variant="body2" paragraph>
              • Combinez plusieurs concepts (ex: "traitement insuline diabète")
            </Typography>
            <Typography variant="body2" paragraph>
              • Utilisez les filtres pour affiner vos résultats par type de document
            </Typography>
            <Typography variant="body2">
              • La recherche sémantique comprend le contexte et les synonymes médicaux
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default Search;