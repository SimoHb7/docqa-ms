import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,

  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,

  CircularProgress,
  Autocomplete,
  Stack,
  Divider,
  Paper,
  Grid,
} from '@mui/material';
import {
  Assessment as SynthesisIcon,

  Download as DownloadIcon,
  Timeline as TimelineIcon,
  Compare as CompareIcon,
  Summarize as SummarizeIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useAuth0 } from '@auth0/auth0-react';
import { backendSynthesis } from '../services/backend';
import { documentsApi } from '../services/api';
import { formatDate } from '../utils';
import { SynthesisRequest, SynthesisResponse, Document } from '../types';
import { useSynthesisStore } from '../store/pageStores';

import ButtonComponent from '../components/ui/Button';
import CardComponent from '../components/ui/Card';

const ModernSynthesis: React.FC = () => {
  const { isAuthenticated, isLoading: authLoading } = useAuth0();
  
  // Use Zustand store for persistent state across navigation
  const {
    synthesisType,
    setSynthesisType,
    patientId,
    setPatientId,
    selectedDocuments,
    setSelectedDocuments,
    result,
    setResult,
  } = useSynthesisStore();

  // Fetch available documents using proper API client with auth interceptor
  const { data: documentsData, isLoading: loadingDocuments } = useQuery({
    queryKey: ['documents', 'synthesis-page'],
    queryFn: async () => {
      console.log('🔍 Fetching documents with auth...');
      // Use documentsApi which has auth interceptor
      const result = await documentsApi.list({ limit: 1000 });
      console.log('✅ Documents fetched:', result);
      return result;
    },
    enabled: isAuthenticated && !authLoading, // Only fetch when authenticated
    staleTime: 30000, // Cache for 30 seconds
    retry: 1,
  });

  // API returns { data: Document[], total: number, ... }
  // Parse metadata if it's a string
  const allDocuments = React.useMemo(() => {
    if (!documentsData?.data) return [];
    
    return documentsData.data.map(doc => {
      // Parse metadata if it's a JSON string
      if (doc.metadata && typeof doc.metadata === 'string') {
        try {
          doc.metadata = JSON.parse(doc.metadata);
        } catch (e) {
          console.error('Failed to parse metadata for document:', doc.id, e);
        }
      }
      // Extract patient_id to top level for convenience
      if (doc.metadata && typeof doc.metadata === 'object') {
        doc.patient_id = doc.metadata.patient_id;
        doc.document_type = doc.metadata.document_type;
      }
      return doc;
    });
  }, [documentsData]);
  
  // Debug logging
  React.useEffect(() => {
    console.log('📊 documentsData:', documentsData);
    console.log('📦 allDocuments:', allDocuments);
    console.log('📦 allDocuments length:', allDocuments.length);
    if (allDocuments.length > 0) {
      console.log('📄 First document structure:', allDocuments[0]);
      console.log('🔑 First document patient_id:', allDocuments[0].patient_id);
      console.log('🔑 First document metadata:', allDocuments[0].metadata);
    }
  }, [documentsData, allDocuments]);

  // Get unique patient IDs for autocomplete suggestions
  const availablePatientIds = React.useMemo(() => {
    const ids = allDocuments
      .map(doc => doc.patient_id || doc.metadata?.patient_id)
      .filter((id): id is string => !!id);
    const uniqueIds = Array.from(new Set(ids)).sort((a, b) => a.localeCompare(b));
    console.log('📋 Available patient IDs:', uniqueIds);
    return uniqueIds;
  }, [allDocuments]);

  // Filter documents by patient ID (case-insensitive partial match)
  const documents = React.useMemo(() => {
    if (!patientId.trim()) {
      return allDocuments;
    }
    const searchTerm = patientId.toLowerCase().trim();
    const filtered = allDocuments.filter(doc => {
      // Check both top-level patient_id and metadata.patient_id
      const docPatientId = doc.patient_id || doc.metadata?.patient_id;
      return docPatientId?.toLowerCase().includes(searchTerm);
    });
    console.log(`🔍 Filtering for "${patientId}": found ${filtered.length} documents`);
    return filtered;
  }, [allDocuments, patientId]);

  // Auto-select documents when patient ID changes
  React.useEffect(() => {
    if (patientId.trim() && documents.length > 0) {
      // Auto-select all documents for this patient
      setSelectedDocuments(documents);
    }
  }, [patientId, documents]);

  // Create synthesis mutation
  const createMutation = useMutation({
    mutationFn: (request: SynthesisRequest) => backendSynthesis.generate(request),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleCreateSynthesis = () => {
    if (selectedDocuments.length === 0 && synthesisType !== 'summary') {
      alert('Veuillez sélectionner au moins un document');
      return;
    }

    if (synthesisType === 'summary' && selectedDocuments.length === 0) {
      alert('Veuillez sélectionner un document');
      return;
    }

    const documentIds = selectedDocuments.map(doc => doc.id);
    
    const request: SynthesisRequest = {
      synthesis_id: `synthesis-${Date.now()}`,
      type: synthesisType,
      parameters: {
        patient_id: patientId || 'ANON_PAT_001',
        document_ids: documentIds,
      },
    };

    if (synthesisType === 'summary' && documentIds.length > 0) {
      request.parameters.document_id = documentIds[0];
    }

    createMutation.mutate(request);
  };

  const handleDownloadSynthesis = () => {
    if (!result) return;

    const content = `# ${result.result.title}

Généré le: ${formatDate(result.generated_at)}
Temps d'exécution: ${result.execution_time_ms}ms
Statut: ${result.status}

${result.result.content}

## Métadonnées
- Documents analysés: ${result.result._metadata?.documents_analyzed || 0}
- Données anonymisées: ${result.result._metadata?.used_anonymized_data ? 'Oui' : 'Non'}
${result.result._metadata?.total_pii_detected !== undefined ? `- Entités PII détectées: ${result.result._metadata.total_pii_detected}` : ''}

${result.result.key_findings ? `## Points clés\n${result.result.key_findings.map(f => `- ${f}`).join('\n')}` : ''}

${result.result.recommendations ? `## Recommandations\n${result.result.recommendations.map(r => `- ${r}`).join('\n')}` : ''}
`;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `synthese-${result.result.title.replace(/\s+/g, '-')}-${Date.now()}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getSynthesisTypeInfo = (type: string) => {
    const info: Record<string, { icon: React.ReactNode; label: string; description: string; color: string }> = {
      patient_timeline: {
        icon: <TimelineIcon />,
        label: 'Chronologie patient',
        description: 'Génère une chronologie médicale complète à partir de plusieurs documents',
        color: '#2196f3',
      },
      comparison: {
        icon: <CompareIcon />,
        label: 'Comparaison de documents',
        description: 'Compare plusieurs documents pour analyser les différences et similitudes',
        color: '#ff9800',
      },
      summary: {
        icon: <SummarizeIcon />,
        label: 'Résumé de document',
        description: 'Crée un résumé détaillé d\'un document médical',
        color: '#4caf50',
      },
    };
    return info[type] || info.patient_timeline;
  };

  const synthesisTypes = [
    {
      value: 'patient_timeline',
      ...getSynthesisTypeInfo('patient_timeline'),
    },
    {
      value: 'comparison',
      ...getSynthesisTypeInfo('comparison'),
    },
    {
      value: 'summary',
      ...getSynthesisTypeInfo('summary'),
    },
  ];

  const renderResult = () => {
    if (!result) return null;

    const { result: data, execution_time_ms, generated_at } = result;
    const typeInfo = getSynthesisTypeInfo(synthesisType);

    return (
      <Card sx={{ borderTop: `4px solid ${typeInfo.color}`, boxShadow: 3 }}>
        <CardContent sx={{ p: 3 }}>
          {/* Header */}
          <Box sx={{ mb: 3 }}>
            <Box display="flex" alignItems="flex-start" justifyContent="space-between" gap={2}>
              <Box display="flex" alignItems="flex-start" gap={2} flex={1}>
                <Box sx={{ 
                  p: 1.5, 
                  borderRadius: 2, 
                  bgcolor: `${typeInfo.color}20`,
                  color: typeInfo.color,
                  display: 'flex'
                }}>
                  {typeInfo.icon}
                </Box>
                <Box flex={1}>
                  <Typography variant="h5" fontWeight={700} gutterBottom>
                    {data.title}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                    <Typography variant="caption" color="text.secondary">
                      📅 {formatDate(generated_at)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      ⏱️ {execution_time_ms}ms
                    </Typography>
                  </Box>
                </Box>
              </Box>
              <ButtonComponent
                variant="outlined"
                size="small"
                startIcon={<DownloadIcon />}
                onClick={handleDownloadSynthesis}
              >
                Télécharger
              </ButtonComponent>
            </Box>
          </Box>

          {/* Metadata Badges */}
          {data._metadata && (
            <Box sx={{ mb: 3 }}>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {data._metadata.used_anonymized_data && (
                  <Chip 
                    label="✓ Données anonymisées" 
                    size="small" 
                    color="success" 
                  />
                )}
                <Chip 
                  label={`${data._metadata.documents_analyzed} document(s) analysé(s)`} 
                  size="small" 
                  variant="outlined"
                />
                {data._metadata.total_pii_detected !== undefined && (
                  <Chip 
                    label={`${data._metadata.total_pii_detected} informations protégées`} 
                    size="small" 
                    color="warning"
                    variant="outlined"
                  />
                )}
              </Stack>
            </Box>
          )}

          <Divider sx={{ mb: 3 }} />

          {/* Main Content */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mb: 2 }}>
              Synthèse complète
            </Typography>
            <Paper 
              variant="outlined" 
              sx={{ 
                p: 3, 
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50',
                borderRadius: 2,
              }}
            >
              <Typography 
                variant="body2" 
                component="pre" 
                sx={{ 
                  whiteSpace: 'pre-wrap', 
                  fontFamily: 'system-ui, -apple-system, sans-serif',
                  fontSize: '0.9375rem',
                  lineHeight: 1.7,
                  maxHeight: '600px',
                  overflow: 'auto',
                  margin: 0,
                  color: 'text.primary',
                }}
              >
                {data.content}
              </Typography>
            </Paper>
          </Box>

          {/* Key Findings */}
          {data.key_findings && data.key_findings.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mb: 2 }}>
                📌 Points clés
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.default' }}>
                <Stack spacing={1.5}>
                  {data.key_findings.map((finding, index) => (
                    <Box key={index} display="flex" alignItems="flex-start" gap={1.5}>
                      <Box sx={{
                        mt: 0.5,
                        width: 6,
                        height: 6,
                        borderRadius: '50%',
                        bgcolor: 'success.main',
                        flexShrink: 0
                      }} />
                      <Typography variant="body2" sx={{ flex: 1 }}>{finding}</Typography>
                    </Box>
                  ))}
                </Stack>
              </Paper>
            </Box>
          )}

          {/* Comparisons */}
          {data.comparisons && data.comparisons.length > 0 && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mb: 2 }}>
                🔍 Comparaisons
              </Typography>
              <Grid container spacing={2}>
                {data.comparisons.map((comp, index) => (
                  <Grid size={{ xs: 12, sm: 6 }} key={index}>
                    <Paper 
                      variant="outlined" 
                      sx={{ 
                        p: 2, 
                        height: '100%',
                        bgcolor: 'background.default',
                        '&:hover': {
                          bgcolor: 'action.hover'
                        }
                      }}
                    >
                      <Typography variant="caption" color="primary.main" fontWeight={700} sx={{ textTransform: 'uppercase', letterSpacing: 0.5 }}>
                        {comp.category}
                      </Typography>
                      {comp.filename && (
                        <Typography variant="body2" fontWeight={500} sx={{ mt: 0.5, mb: 1 }}>{comp.filename}</Typography>
                      )}
                      {comp.size !== undefined && (
                        <Typography variant="caption" color="text.secondary">
                          {comp.size} caractères
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </Box>
          )}

          {/* Recommendations */}
          {data.recommendations && data.recommendations.length > 0 && (
            <Box>
              <Typography variant="subtitle2" fontWeight={600} mb={1}>
                Recommandations
              </Typography>
              <Stack spacing={0.5}>
                {data.recommendations.map((rec, index) => (
                  <Box key={index} display="flex" alignItems="center" gap={1}>
                    <InfoIcon sx={{ fontSize: 16, color: 'info.main' }} />
                    <Typography variant="body2">{rec}</Typography>
                  </Box>
                ))}
              </Stack>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box sx={{ maxWidth: 1600, mx: 'auto' }}>
      {/* Header Section */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
          Synthèses Médicales Intelligentes
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Générez des rapports et analyses à partir de documents médicaux anonymisés
        </Typography>
      </Box>

      {/* Synthesis Type Selection - Full Width Cards */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 2 }}>
          Étape 1 : Choisissez le type de synthèse
        </Typography>
        <Grid container spacing={2}>
          {synthesisTypes.map((type) => (
            <Grid key={type.value} size={{ xs: 12, md: 4 }}>
              <Card 
                sx={{ 
                  cursor: 'pointer',
                  border: 2,
                  borderColor: synthesisType === type.value ? type.color : 'transparent',
                  bgcolor: synthesisType === type.value ? `${type.color}08` : 'background.paper',
                  transition: 'all 0.2s',
                  height: '100%',
                  '&:hover': {
                    borderColor: type.color,
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                  }
                }}
                onClick={() => {
                  setSynthesisType(type.value as any);
                  setResult(null);
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2 }}>
                    <Box 
                      sx={{ 
                        p: 1.5, 
                        borderRadius: 2, 
                        bgcolor: `${type.color}20`,
                        color: type.color,
                        display: 'flex'
                      }}
                    >
                      {type.icon}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                        {type.label}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                        {type.description}
                      </Typography>
                    </Box>
                    {synthesisType === type.value && (
                      <CheckIcon sx={{ color: type.color }} />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      <Grid container spacing={3}>
        {/* Configuration Panel */}
        <Grid size={{ xs: 12, md: 5 }}>
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Étape 2 : Sélection des documents
              </Typography>
              <Divider sx={{ mb: 3 }} />

              {/* Patient ID Selection */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mb: 1.5 }}>
                  ID Patient
                </Typography>
                <Autocomplete
                  freeSolo
                  options={availablePatientIds}
                  value={patientId}
                  onInputChange={(_, newValue) => setPatientId(newValue || '')}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      fullWidth
                      placeholder="Ex: pat_002, P_001, p_111"
                      helperText={
                        patientId.trim() 
                          ? `${documents.length} document(s) trouvé(s)` 
                          : `${availablePatientIds.length} patient(s) disponible(s)`
                      }
                      InputProps={{
                        ...params.InputProps,
                        endAdornment: (
                          <>
                            {params.InputProps.endAdornment}
                            {patientId && documents.length > 0 && (
                              <Chip 
                                label={`${documents.length}`} 
                                size="small" 
                                color="primary"
                                sx={{ mr: 1 }}
                              />
                            )}
                          </>
                        ),
                      }}
                    />
                  )}
                />
              </Box>

              {/* Document Selection */}
              {patientId.trim() && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mb: 1.5 }}>
                    Documents
                    <Typography component="span" variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                      {synthesisType === 'summary' 
                        ? '(1 requis)' 
                        : synthesisType === 'comparison'
                        ? '(min. 2 requis)'
                        : '(1 ou plus)'}
                    </Typography>
                  </Typography>
                  <Autocomplete
                    multiple
                    options={documents}
                    getOptionLabel={(option) => option.filename}
                    value={selectedDocuments}
                    onChange={(_, newValue) => setSelectedDocuments(newValue)}
                    loading={loadingDocuments}
                    noOptionsText="Aucun document trouvé"
                    renderInput={(params) => (
                      <TextField
                        {...params}
                        placeholder={documents.length > 0 ? "Cliquez pour sélectionner" : "Aucun document disponible"}
                      />
                    )}
                    renderOption={(props, option) => {
                      const { key, ...otherProps } = props as any;
                      return (
                        <li key={key} {...otherProps}>
                          <Box sx={{ width: '100%' }}>
                            <Typography variant="body2" fontWeight={500}>{option.filename}</Typography>
                            <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                              <Chip label={option.file_type} size="small" variant="outlined" />
                              <Chip 
                                label={option.is_anonymized ? 'Anonymisé' : 'Non anonymisé'} 
                                size="small" 
                                color={option.is_anonymized ? 'success' : 'default'}
                              />
                            </Box>
                          </Box>
                        </li>
                      );
                    }}
                  />
                </Box>
              )}

              {/* Status Messages */}
              {patientId.trim() && documents.length === 0 && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Aucun document pour "{patientId}"
                  </Typography>
                  <Typography variant="caption" display="block">
                    Essayez: {availablePatientIds.slice(0, 3).join(', ')}
                    {availablePatientIds.length > 3 && `... (+${availablePatientIds.length - 3})`}
                  </Typography>
                </Alert>
              )}

              {selectedDocuments.length > 0 && (
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 2, 
                    mb: 3, 
                    bgcolor: 'success.50',
                    borderColor: 'success.main',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <CheckIcon color="success" fontSize="small" />
                    <Typography variant="subtitle2" fontWeight={600}>
                      {selectedDocuments.length} document(s) sélectionné(s)
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {selectedDocuments.map((doc) => (
                      <Chip 
                        key={doc.id}
                        label={doc.filename}
                        size="small"
                        variant="outlined"
                        color="success"
                      />
                    ))}
                  </Stack>
                  {synthesisType === 'comparison' && selectedDocuments.length < 2 && (
                    <Typography variant="caption" color="warning.main" sx={{ display: 'block', mt: 1 }}>
                      ⚠️ Comparaison nécessite au moins 2 documents
                    </Typography>
                  )}
                </Paper>
              )}

              <Divider sx={{ mb: 3 }} />

              {/* Action Button */}
              <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mb: 1.5 }}>
                Étape 3 : Générer
              </Typography>
              <ButtonComponent
                fullWidth
                size="large"
                onClick={handleCreateSynthesis}
                loading={createMutation.isPending}
                disabled={
                  selectedDocuments.length === 0 || 
                  (synthesisType === 'comparison' && selectedDocuments.length < 2)
                }
              >
                {createMutation.isPending ? 'Génération en cours...' : 'Générer la synthèse'}
              </ButtonComponent>

              {createMutation.error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  <strong>Erreur:</strong> {(createMutation.error as Error).message || 'Échec de la génération'}
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Quick Guide Card */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <InfoIcon color="primary" fontSize="small" />
                <Typography variant="subtitle2" fontWeight={600}>
                  Guide rapide
                </Typography>
              </Box>
              <Stack spacing={1.5}>
                <Box>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Chronologie
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Suivez l'évolution médicale d'un patient dans le temps
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Comparaison
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Analysez les différences entre plusieurs documents
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" fontWeight={500} gutterBottom>
                    Résumé
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block">
                    Obtenez un résumé concis d'un document unique
                  </Typography>
                </Box>
              </Stack>
              <Alert severity="success" sx={{ mt: 2 }} icon={<CheckIcon />}>
                <Typography variant="caption">
                  Toutes les synthèses utilisent du contenu anonymisé
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Panel */}
        <Grid size={{ xs: 12, md: 7 }}>
          {createMutation.isPending ? (
            <Card sx={{ minHeight: 400 }}>
              <CardContent sx={{ textAlign: 'center', py: 10 }}>
                <CircularProgress size={60} thickness={4} />
                <Typography variant="h6" sx={{ mt: 3, fontWeight: 600 }}>
                  Génération de la synthèse...
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Analyse des {selectedDocuments.length} document(s) en cours
                </Typography>
                <Box sx={{ 
                  mt: 4, 
                  px: 3, 
                  py: 2, 
                  bgcolor: 'action.hover', 
                  borderRadius: 2,
                  display: 'inline-block'
                }}>
                  <Typography variant="caption" color="text.secondary">
                    ⏱️ Temps estimé : 5-15 secondes
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          ) : result ? (
            renderResult()
          ) : (
            <Card sx={{ minHeight: 400 }}>
              <CardContent sx={{ textAlign: 'center', py: 10 }}>
                <Box sx={{
                  width: 100,
                  height: 100,
                  borderRadius: 3,
                  bgcolor: 'action.hover',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mx: 'auto',
                  mb: 3
                }}>
                  <SynthesisIcon sx={{ fontSize: 50, color: 'text.secondary' }} />
                </Box>
                <Typography variant="h6" color="text.secondary" fontWeight={600} gutterBottom>
                  Prêt à générer une synthèse
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1, mb: 3 }}>
                  Suivez les 3 étapes à gauche pour commencer
                </Typography>
                <Stack spacing={1} sx={{ maxWidth: 400, mx: 'auto', textAlign: 'left' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ 
                      width: 32, 
                      height: 32, 
                      borderRadius: '50%', 
                      bgcolor: 'primary.main', 
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      fontSize: '0.875rem'
                    }}>
                      1
                    </Box>
                    <Typography variant="body2">Choisir le type de synthèse</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ 
                      width: 32, 
                      height: 32, 
                      borderRadius: '50%', 
                      bgcolor: 'primary.main', 
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      fontSize: '0.875rem'
                    }}>
                      2
                    </Box>
                    <Typography variant="body2">Sélectionner patient et documents</Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <Box sx={{ 
                      width: 32, 
                      height: 32, 
                      borderRadius: '50%', 
                      bgcolor: 'primary.main', 
                      color: 'white',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontWeight: 'bold',
                      fontSize: '0.875rem'
                    }}>
                      3
                    </Box>
                    <Typography variant="body2">Générer la synthèse</Typography>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ModernSynthesis;
