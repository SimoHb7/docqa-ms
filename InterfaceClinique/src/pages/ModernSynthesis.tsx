import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Autocomplete,
  Stack,
  Divider,
  Paper,
  Grid,
} from '@mui/material';
import {
  Assessment as SynthesisIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon,
  Compare as CompareIcon,
  Summarize as SummarizeIcon,
  CheckCircle as CheckIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { backendSynthesis, backendDocuments } from '../services/backend';
import { formatDate } from '../utils';
import { SynthesisRequest, SynthesisResponse, Document } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ButtonComponent from '../components/ui/Button';
import CardComponent from '../components/ui/Card';

const ModernSynthesis: React.FC = () => {
  const [synthesisType, setSynthesisType] = useState<'patient_timeline' | 'comparison' | 'summary'>('patient_timeline');
  const [patientId, setPatientId] = useState('');
  const [selectedDocuments, setSelectedDocuments] = useState<Document[]>([]);
  const [result, setResult] = useState<SynthesisResponse | null>(null);

  // Fetch available documents
  const { data: documentsData, isLoading: loadingDocuments } = useQuery({
    queryKey: ['documents'],
    queryFn: () => backendDocuments.list({ limit: 1000 }),
  });

  // API returns { data: Document[], total: number, ... }
  const allDocuments = documentsData?.data || [];
  
  // Debug logging
  React.useEffect(() => {
    console.log('📊 documentsData:', documentsData);
    console.log('📦 allDocuments:', allDocuments);
    console.log('📦 allDocuments length:', allDocuments.length);
  }, [documentsData, allDocuments]);

  // Get unique patient IDs for autocomplete suggestions
  const availablePatientIds = React.useMemo(() => {
    const ids = allDocuments
      .map(doc => doc.patient_id)
      .filter((id): id is string => !!id);
    return Array.from(new Set(ids)).sort();
  }, [allDocuments]);

  // Filter documents by patient ID (case-insensitive partial match)
  const documents = React.useMemo(() => {
    if (!patientId.trim()) {
      return allDocuments;
    }
    const searchTerm = patientId.toLowerCase().trim();
    const filtered = allDocuments.filter(doc => 
      doc.patient_id?.toLowerCase().includes(searchTerm)
    );
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

    const { result: data, execution_time_ms, generated_at, status } = result;
    const typeInfo = getSynthesisTypeInfo(synthesisType);

    return (
      <Card sx={{ mt: 3, borderLeft: `4px solid ${typeInfo.color}` }}>
        <CardContent>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
            <Box display="flex" alignItems="center" gap={2}>
              <Box sx={{ color: typeInfo.color }}>{typeInfo.icon}</Box>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  {data.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Généré le {formatDate(generated_at)} • {execution_time_ms}ms
                </Typography>
              </Box>
            </Box>
            <ButtonComponent
              size="small"
              startIcon={<DownloadIcon />}
              onClick={handleDownloadSynthesis}
            >
              Télécharger
            </ButtonComponent>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Metadata */}
          {data._metadata && (
            <Box mb={2}>
              <Stack direction="row" spacing={1} flexWrap="wrap" mb={1}>
                {data._metadata.used_anonymized_data && (
                  <Chip 
                    label="Données anonymisées" 
                    size="small" 
                    color="success" 
                    icon={<CheckIcon />}
                  />
                )}
                <Chip 
                  label={`${data._metadata.documents_analyzed} document(s)`} 
                  size="small" 
                  variant="outlined"
                />
                {data._metadata.total_pii_detected !== undefined && (
                  <Chip 
                    label={`${data._metadata.total_pii_detected} PII détectées`} 
                    size="small" 
                    color="warning"
                    variant="outlined"
                  />
                )}
              </Stack>
            </Box>
          )}

          {/* Content */}
          <Paper 
            variant="outlined" 
            sx={{ 
              p: 2, 
              mb: 2, 
              bgcolor: (theme) => theme.palette.mode === 'dark' ? 'grey.900' : 'grey.50'
            }}
          >
            <Typography 
              variant="body2" 
              component="pre" 
              sx={{ 
                whiteSpace: 'pre-wrap', 
                fontFamily: 'monospace',
                fontSize: '0.875rem',
                maxHeight: '400px',
                overflow: 'auto',
              }}
            >
              {data.content}
            </Typography>
          </Paper>

          {/* Key Findings */}
          {data.key_findings && data.key_findings.length > 0 && (
            <Box mb={2}>
              <Typography variant="subtitle2" fontWeight={600} mb={1}>
                Points clés
              </Typography>
              <Stack spacing={0.5}>
                {data.key_findings.map((finding, index) => (
                  <Box key={index} display="flex" alignItems="center" gap={1}>
                    <CheckIcon sx={{ fontSize: 16, color: 'success.main' }} />
                    <Typography variant="body2">{finding}</Typography>
                  </Box>
                ))}
              </Stack>
            </Box>
          )}

          {/* Comparisons */}
          {data.comparisons && data.comparisons.length > 0 && (
            <Box mb={2}>
              <Typography variant="subtitle2" fontWeight={600} mb={1}>
                Comparaisons
              </Typography>
              <Grid container spacing={1}>
                {data.comparisons.map((comp, index) => (
                  <Grid item xs={12} sm={6} md={4} key={index}>
                    <Paper variant="outlined" sx={{ p: 1.5 }}>
                      <Typography variant="caption" color="text.secondary" fontWeight={600}>
                        {comp.category}
                      </Typography>
                      {comp.filename && (
                        <Typography variant="body2" noWrap>{comp.filename}</Typography>
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
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
        Synthèses Médicales Intelligentes
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Générez des rapports et analyses à partir de documents médicaux anonymisés
      </Typography>

      <Grid container spacing={3}>
        {/* Configuration Panel */}
        <Grid item xs={12} md={5}>
          <CardComponent title="Configuration" icon={<SynthesisIcon />}>
            <CardContent>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Type de synthèse</InputLabel>
                <Select
                  value={synthesisType}
                  onChange={(e) => {
                    setSynthesisType(e.target.value as any);
                    setResult(null);
                  }}
                  label="Type de synthèse"
                >
                  {synthesisTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Box display="flex" alignItems="center" gap={2}>
                        <Box sx={{ color: type.color }}>{type.icon}</Box>
                        <Box>
                          <Typography variant="body2" fontWeight={500}>
                            {type.label}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {type.description}
                          </Typography>
                        </Box>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Autocomplete
                freeSolo
                options={availablePatientIds}
                value={patientId}
                onInputChange={(_, newValue) => setPatientId(newValue || '')}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    fullWidth
                    label="ID Patient"
                    placeholder="Ex: pat_002, P_001, p_111"
                    helperText={
                      patientId.trim() 
                        ? `${documents.length} document(s) trouvé(s) pour "${patientId}"` 
                        : `${availablePatientIds.length} patient(s) disponible(s) - Commencez à taper ou sélectionnez`
                    }
                    InputProps={{
                      ...params.InputProps,
                      endAdornment: (
                        <>
                          {params.InputProps.endAdornment}
                          {patientId && documents.length > 0 && (
                            <Chip 
                              label={`${documents.length} docs`} 
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
                sx={{ mb: 3 }}
              />

              <Autocomplete
                multiple
                options={documents}
                getOptionLabel={(option) => option.filename}
                value={selectedDocuments}
                onChange={(_, newValue) => setSelectedDocuments(newValue)}
                loading={loadingDocuments}
                noOptionsText={
                  patientId.trim() 
                    ? "Aucun document trouvé pour ce patient" 
                    : "Entrez un ID patient pour voir les documents"
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label={synthesisType === 'summary' ? 'Sélectionner un document' : 'Sélectionner des documents'}
                    placeholder={patientId.trim() ? "Documents filtrés par patient" : "Entrez d'abord un ID patient..."}
                    helperText={
                      synthesisType === 'summary' 
                        ? 'Sélectionnez un document' 
                        : synthesisType === 'comparison'
                        ? 'Sélectionnez au moins 2 documents'
                        : 'Sélectionnez un ou plusieurs documents'
                    }
                  />
                )}
                renderOption={(props, option) => (
                  <li {...props}>
                    <Box>
                      <Typography variant="body2">{option.filename}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {option.file_type} • {option.is_anonymized ? 'Anonymisé' : 'Non anonymisé'}
                        {option.patient_id && ` • Patient: ${option.patient_id}`}
                      </Typography>
                    </Box>
                  </li>
                )}
                sx={{ mb: 3 }}
              />

              {patientId.trim() && documents.length === 0 && (
                <Alert severity="warning" sx={{ mb: 3 }}>
                  <Typography variant="body2" fontWeight={500}>
                    Aucun document trouvé pour le patient "{patientId}"
                  </Typography>
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    IDs patients disponibles: {availablePatientIds.slice(0, 5).join(', ')}
                    {availablePatientIds.length > 5 && ` et ${availablePatientIds.length - 5} autre(s)...`}
                  </Typography>
                </Alert>
              )}

              {selectedDocuments.length > 0 && (
                <Alert severity="info" sx={{ mb: 3 }} icon={<CheckIcon />}>
                  {selectedDocuments.length} document(s) sélectionné(s)
                  {patientId.trim() && ` pour le patient ${patientId}`}
                  {synthesisType === 'comparison' && selectedDocuments.length < 2 && 
                    ` (au moins 2 requis pour la comparaison)`
                  }
                </Alert>
              )}

              <ButtonComponent
                fullWidth
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
                  Erreur: {(createMutation.error as Error).message || 'Échec de la génération'}
                </Alert>
              )}
            </CardContent>
          </CardComponent>

          {/* Usage Tips */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                💡 Conseils d'utilisation
              </Typography>
              <Typography variant="body2" paragraph sx={{ fontSize: '0.875rem' }}>
                <strong>• ID Patient:</strong> Entrez un ID patient pour filtrer automatiquement tous ses documents
              </Typography>
              <Typography variant="body2" paragraph sx={{ fontSize: '0.875rem' }}>
                <strong>• Chronologie:</strong> Pour suivre l'évolution d'un patient sur plusieurs documents
              </Typography>
              <Typography variant="body2" paragraph sx={{ fontSize: '0.875rem' }}>
                <strong>• Comparaison:</strong> Pour analyser les différences entre 2+ documents
              </Typography>
              <Typography variant="body2" sx={{ fontSize: '0.875rem' }}>
                <strong>• Résumé:</strong> Pour obtenir un résumé détaillé d'un seul document
              </Typography>
              <Alert severity="success" sx={{ mt: 2 }} icon={<CheckIcon />}>
                Les synthèses utilisent automatiquement le contenu anonymisé des documents
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Results Panel */}
        <Grid item xs={12} md={7}>
          {createMutation.isPending ? (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <CircularProgress size={60} />
                <Typography variant="h6" sx={{ mt: 3 }}>
                  Génération de la synthèse en cours...
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Analyse des documents et génération du contenu
                </Typography>
              </CardContent>
            </Card>
          ) : result ? (
            renderResult()
          ) : (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <SynthesisIcon sx={{ fontSize: 80, color: 'text.disabled', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Configurez et lancez une synthèse
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Sélectionnez un type de synthèse et des documents pour commencer
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default ModernSynthesis;
