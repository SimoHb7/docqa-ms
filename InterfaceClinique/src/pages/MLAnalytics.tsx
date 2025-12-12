import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Chip,
  Paper,
  Alert,
  LinearProgress,
  Divider,
  IconButton,
  Tooltip,
  alpha,
  useTheme,
  CircularProgress,
  Badge,
  Autocomplete,
} from '@mui/material';
import {
  Send,
  AutoAwesome as AIIcon,
  Speed as SpeedIcon,
  CheckCircle,
  Error as ErrorIcon,
  ContentCopy as CopyIcon,
  Refresh as RefreshIcon,
  TrendingUp,
  LocalHospital,
  Science,
  Biotech,
  BarChart as BarChartIcon,
  Label as LabelIcon,
} from '@mui/icons-material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Doughnut, Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';
import { mlApi, documentsApi } from '../services/api';
import toast from 'react-hot-toast';
import ButtonComponent from '../components/ui/Button';
import type { MLClassificationResponse, MLEntityExtractionResponse, MLAnalyzeResponse, Document } from '../types';

// Register ChartJS components
ChartJS.register(ArcElement, RadialLinearScale, PointElement, LineElement, Filler, ChartTooltip, Legend);

// Sample medical texts in French
const SAMPLE_TEXTS = [
  {
    title: 'Analyse sanguine',
    text: 'Analyse sanguine du patient: Hémoglobine 14.5 g/dL, Leucocytes 7200/mm³, Plaquettes 250000/mm³. Valeurs dans les normes.',
  },
  {
    title: 'Prescription',
    text: 'Patient diabétique de type 2. Prescription: Metformine 850mg 2x/jour, Atorvastatine 20mg le soir. Contrôle glycémique dans 3 mois.',
  },
  {
    title: 'Consultation',
    text: 'Patient présente une hypertension artérielle (145/95 mmHg). Antécédents de cardiopathie ischémique. Traitement par Ramipril 5mg recommandé.',
  },
  {
    title: 'Résultat IRM',
    text: 'IRM cérébrale: Absence de lésion hémorragique ou ischémique aiguë. Discrète atrophie cortico-sous-corticale. Leucopathie vasculaire modérée.',
  },
];

// Color mapping for document types
const DOC_TYPE_COLORS: Record<string, string> = {
  blood_test: '#ef4444',
  xray: '#8b5cf6',
  mri: '#6366f1',
  prescription: '#3b82f6',
  medical_report: '#06b6d4',
  lab_result: '#10b981',
  consultation_note: '#84cc16',
};

// Professional gradient colors for entities
const ENTITY_COLORS: Record<string, string> = {
  DISEASE: '#ef4444',
  MEDICATION: '#3b82f6',
  DOSAGE: '#f59e0b',
  TEST: '#8b5cf6',
  SYMPTOM: '#ec4899',
  ANATOMY: '#06b6d4',
  DEFAULT: '#6b7280',
};

const MLAnalytics: React.FC = () => {
  const theme = useTheme();
  const [patientId, setPatientId] = useState<string>('');
  const [showDocuments, setShowDocuments] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [classificationResult, setClassificationResult] = useState<MLClassificationResponse | null>(null);
  const [entitiesResult, setEntitiesResult] = useState<MLEntityExtractionResponse | null>(null);
  const [processingTime, setProcessingTime] = useState<number>(0);

  // Fetch all documents
  const { data: allDocumentsDataRaw, isLoading: isLoadingDocuments } = useQuery({
    queryKey: ['all-documents'],
    queryFn: () => documentsApi.list({ limit: 1000 }),
  });

  // Parse metadata and extract patient_id to top level (like ModernSynthesis)
  const allDocumentsData = React.useMemo(() => {
    if (!allDocumentsDataRaw?.data) return null;
    
    const parsedData = allDocumentsDataRaw.data.map(doc => {
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

    return {
      ...allDocumentsDataRaw,
      data: parsedData
    };
  }, [allDocumentsDataRaw]);

  // Extract unique patient IDs
  const patientIds = React.useMemo(() => {
    if (!allDocumentsData?.data) return [];
    const ids = allDocumentsData.data
      .map(doc => doc.patient_id || doc.metadata?.patient_id)
      .filter((id): id is string => !!id);
    return [...new Set(ids)].sort();
  }, [allDocumentsData]);

  // Filter documents by patient ID (client-side filtering)
  const documentsData = React.useMemo(() => {
    if (!showDocuments || !patientId || !allDocumentsData?.data) {
      return { data: [], total: 0, limit: 0, offset: 0 };
    }
    
    const searchTerm = patientId.toLowerCase().trim();
    const filtered = allDocumentsData.data.filter(doc => {
      const docPatientId = doc.patient_id || doc.metadata?.patient_id;
      return docPatientId?.toLowerCase().includes(searchTerm);
    });

    return {
      data: filtered,
      total: filtered.length,
      limit: filtered.length,
      offset: 0
    };
  }, [allDocumentsData, patientId, showDocuments]);

  // Health check
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['ml-health'],
    queryFn: mlApi.health,
    refetchInterval: 30000,
  });

  // Full analysis mutation
  const analyzeMutation = useMutation({
    mutationFn: async (documentId: string) => {
      // Find document in filtered list (already loaded)
      const doc = documentsData?.data?.find(d => d.id === documentId);
      
      if (!doc) {
        throw new Error('Document introuvable dans la liste');
      }
      
      setSelectedDocument(doc);
      
      // Use document content or filename for analysis
      const textToAnalyze = doc.content || doc.filename || '';
      
      if (!textToAnalyze || textToAnalyze.trim() === '') {
        throw new Error('Le document ne contient pas de texte à analyser');
      }
      
      console.log('📝 Analyzing text:', textToAnalyze.substring(0, 100) + '...');
      return mlApi.analyze({ text: textToAnalyze, extract_entities: true, classify: true });
    },
    onSuccess: (data: MLAnalyzeResponse) => {
      if (data.classification) setClassificationResult(data.classification);
      if (data.entities) setEntitiesResult(data.entities);
      setProcessingTime(data.processing_time_ms);
      toast.success(`✨ Analyse terminée en ${data.processing_time_ms}ms`);
    },
    onError: (error: any) => {
      console.error('Analyze error:', error);
      const errorMsg = error?.response?.data?.detail || error?.message || 'Erreur inconnue';
      toast.error(`❌ Erreur: ${errorMsg}`);
    },
  });

  const handleAnalyze = () => {
    if (!selectedDocumentId) {
      toast.error('Veuillez sélectionner un document');
      return;
    }
    
    console.log('🔍 Analyzing document:', selectedDocumentId);
    setClassificationResult(null);
    setEntitiesResult(null);
    analyzeMutation.mutate(selectedDocumentId);
  };

  const handlePatientIdSubmit = async () => {
    if (!patientId.trim()) {
      toast.error('Veuillez entrer un ID patient');
      return;
    }

    // Check if any documents exist for this patient ID (partial match)
    const searchTerm = patientId.toLowerCase().trim();
    const hasDocuments = allDocumentsData?.data?.some(doc => {
      const docPatientId = doc.patient_id || doc.metadata?.patient_id;
      return docPatientId?.toLowerCase().includes(searchTerm);
    });

    if (!hasDocuments) {
      toast.error(`Aucun document trouvé pour le patient "${patientId}". Veuillez vérifier l'ID.`);
      return;
    }

    setShowDocuments(true);
    setSelectedDocumentId(null);
    setClassificationResult(null);
    setEntitiesResult(null);
  };

  const handleResetPatient = () => {
    setPatientId('');
    setShowDocuments(false);
    setSearchQuery('');
    setSelectedDocumentId(null);
    setSelectedDocument(null);
    setClassificationResult(null);
    setEntitiesResult(null);
  };

  const handleDocumentSelect = (docId: string) => {
    setSelectedDocumentId(docId);
    setClassificationResult(null);
    setEntitiesResult(null);
  };

  // Filter documents by search query
  const filteredDocuments = documentsData?.data?.filter((doc) =>
    doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.document_type?.toLowerCase().includes(searchQuery.toLowerCase())
  ) || [];

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('📋 Copié!');
  };

  // Prepare doughnut chart data
  const doughnutData = classificationResult
    ? {
        labels: Object.keys(classificationResult.all_probabilities).map((k) => k.replace(/_/g, ' ')),
        datasets: [
          {
            data: Object.values(classificationResult.all_probabilities).map((v) => Math.round(v * 100)),
            backgroundColor: Object.keys(classificationResult.all_probabilities).map(
              (k) => alpha(DOC_TYPE_COLORS[k] || '#3b82f6', 0.8)
            ),
            borderColor: Object.keys(classificationResult.all_probabilities).map(
              (k) => DOC_TYPE_COLORS[k] || '#3b82f6'
            ),
            borderWidth: 3,
          },
        ],
      }
    : null;

  // Prepare radar chart data for entities
  const radarData =
    entitiesResult && entitiesResult.Count > 0
      ? {
          labels: entitiesResult.value.slice(0, 6).map((e) => e.label),
          datasets: [
            {
              label: 'Confiance',
              data: entitiesResult.value.slice(0, 6).map((e) => e.confidence * 100),
              backgroundColor: alpha(theme.palette.primary.main, 0.2),
              borderColor: theme.palette.primary.main,
              borderWidth: 3,
              pointBackgroundColor: theme.palette.primary.main,
              pointBorderColor: '#fff',
              pointHoverBackgroundColor: '#fff',
              pointHoverBorderColor: theme.palette.primary.main,
              pointRadius: 6,
              pointHoverRadius: 8,
            },
          ],
        }
      : null;

  return (
    <Box
      sx={{
        maxWidth: 1400,
        mx: 'auto',
        px: { xs: 2, sm: 3, md: 4 },
      }}
    >
      {/* Hero Header with Gradient */}
      <Box
        sx={{
          mb: 4,
          p: 4,
          borderRadius: 4,
          background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.1)} 0%, ${alpha(
            theme.palette.secondary.main,
            0.1
          )} 100%)`,
          border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
          position: 'relative',
          overflow: 'hidden',
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Box
              sx={{
                width: 64,
                height: 64,
                borderRadius: 3,
                background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.3)}`,
              }}
            >
              <AIIcon sx={{ fontSize: 36, color: 'white' }} />
            </Box>
            <Box>
              <Typography variant="h3" fontWeight={800} gutterBottom>
                Analyseur IA Médical
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 800, lineHeight: 1.8 }}>
                Testez nos modèles d'IA sur vos textes médicaux : <strong>classification automatique</strong> du type de document et <strong>extraction intelligente</strong> des entités médicales (maladies, médicaments, dosages, tests...)
              </Typography>
            </Box>
          </Box>

          {/* Service Status Badge */}
          <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
            {healthData?.models_loaded ? (
              <>
                <Chip
                  icon={<CheckCircle />}
                  label="Service ML Actif"
                  color="success"
                  sx={{ fontWeight: 600, px: 1 }}
                />
                <Chip
                  icon={<Science />}
                  label="CamemBERT Loaded"
                  variant="outlined"
                  sx={{ fontWeight: 600 }}
                />
                <Chip
                  icon={<Biotech />}
                  label="BioBERT Loaded"
                  variant="outlined"
                  sx={{ fontWeight: 600 }}
                />
              </>
            ) : (
              <Chip
                icon={<ErrorIcon />}
                label="Service ML non disponible"
                color="warning"
                sx={{ fontWeight: 600 }}
              />
            )}
          </Box>
        </Box>
      </Box>

      {/* Patient ID Input Section */}
      {!showDocuments ? (
        <Card
          elevation={2}
          sx={{
            mb: 3,
            background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(
              theme.palette.primary.main,
              0.02
            )} 100%)`,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
          }}
        >
          <CardContent>
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: 3,
                  bgcolor: alpha(theme.palette.primary.main, 0.1),
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  mb: 3,
                }}
              >
                <LocalHospital sx={{ fontSize: 48, color: theme.palette.primary.main }} />
              </Box>
              <Typography variant="h5" fontWeight={700} gutterBottom>
                Entrer l'ID du Patient
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 4, maxWidth: 600, mx: 'auto' }}>
                Saisissez l'identifiant du patient pour voir ses documents médicaux et les analyser avec l'IA
              </Typography>

              <Box sx={{ maxWidth: 500, mx: 'auto' }}>
                <Autocomplete
                  freeSolo
                  openOnFocus
                  options={patientIds}
                  value={patientId}
                  onChange={(event, newValue) => {
                    setPatientId(newValue || '');
                  }}
                  onInputChange={(event, newInputValue) => {
                    setPatientId(newInputValue);
                  }}
                  ListboxProps={{
                    style: {
                      maxHeight: '250px',
                    },
                  }}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      placeholder="Ex: PAT-12345"
                      helperText={`${patientIds.length} patient(s) disponible(s)`}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter') {
                          handlePatientIdSubmit();
                        }
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          bgcolor: 'background.paper',
                          fontSize: '1.1rem',
                        },
                      }}
                      InputProps={{
                        ...params.InputProps,
                        startAdornment: (
                          <>
                            <Box sx={{ ml: 1, mr: 1, display: 'flex', alignItems: 'center' }}>
                              <Typography color="text.secondary" fontWeight={600}>
                                ID:
                              </Typography>
                            </Box>
                            {params.InputProps.startAdornment}
                          </>
                        ),
                      }}
                    />
                  )}
                  renderOption={(props, option) => {
                    const { key, ...otherProps } = props;
                    return (
                      <Box component="li" key={key} {...otherProps} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LocalHospital sx={{ fontSize: 18, color: theme.palette.primary.main }} />
                        <Typography>{option}</Typography>
                      </Box>
                    );
                  }}
                  noOptionsText="Aucun ID patient trouvé"
                  sx={{ mb: 2 }}
                />
                <ButtonComponent
                  variant="contained"
                  color="primary"
                  fullWidth
                  onClick={handlePatientIdSubmit}
                  disabled={!patientId.trim()}
                  sx={{
                    py: 1.5,
                    fontWeight: 600,
                    textTransform: 'none',
                    fontSize: '1rem',
                  }}
                >
                  Voir les Documents
                </ButtonComponent>
              </Box>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Patient Info Bar */}
          <Card
            elevation={1}
            sx={{
              mb: 3,
              background: `linear-gradient(135deg, ${alpha(theme.palette.success.main, 0.1)} 0%, ${alpha(
                theme.palette.success.main,
                0.05
              )} 100%)`,
              border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box
                    sx={{
                      width: 48,
                      height: 48,
                      borderRadius: 2,
                      bgcolor: alpha(theme.palette.success.main, 0.2),
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <LocalHospital sx={{ color: theme.palette.success.main, fontSize: 28 }} />
                  </Box>
                  <Box>
                    <Typography variant="caption" color="text.secondary" fontWeight={600}>
                      PATIENT SÉLECTIONNÉ
                    </Typography>
                    <Typography variant="h6" fontWeight={700}>
                      {patientId}
                    </Typography>
                  </Box>
                </Box>
                <ButtonComponent
                  variant="outlined"
                  color="primary"
                  onClick={handleResetPatient}
                  startIcon={<RefreshIcon />}
                  sx={{ textTransform: 'none' }}
                >
                  Changer Patient
                </ButtonComponent>
              </Box>
            </CardContent>
          </Card>

          {/* Document Selection Section */}
          <Card
            elevation={2}
            sx={{
              mb: 3,
              background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(
                theme.palette.primary.main,
                0.02
              )} 100%)`,
              border: `1px solid ${alpha(theme.palette.primary.main, 0.1)}`,
            }}
          >
            <CardContent>
              <Grid container spacing={3}>
                <Grid item xs={12} md={8}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box>
                      <Typography variant="h6" fontWeight={600}>
                        Documents du Patient
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {filteredDocuments.length} document(s) trouvé(s)
                      </Typography>
                    </Box>
                  </Box>

                  {/* Search Bar */}
                  <TextField
                    fullWidth
                    size="small"
                    variant="outlined"
                    placeholder="Rechercher un document par nom ou type..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    sx={{
                      mb: 2,
                      '& .MuiOutlinedInput-root': {
                        bgcolor: 'background.paper',
                      },
                    }}
                    InputProps={{
                      startAdornment: (
                        <Box sx={{ mr: 1, color: 'text.secondary' }}>
                          🔍
                        </Box>
                      ),
                    }}
                  />

                  {/* Document List */}
                  {isLoadingDocuments ? (
                    <Box sx={{ textAlign: 'center', py: 4 }}>
                      <CircularProgress size={40} />
                      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                        Chargement des documents...
                      </Typography>
                    </Box>
                  ) : filteredDocuments.length > 0 ? (
                    <Box
                      sx={{
                        maxHeight: 400,
                        overflowY: 'auto',
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 2,
                        bgcolor: 'background.paper',
                      }}
                    >
                      {filteredDocuments.map((doc) => (
                        <Paper
                          key={doc.id}
                          elevation={0}
                          sx={{
                            p: 2,
                            m: 1,
                            cursor: 'pointer',
                            border: `2px solid ${
                              selectedDocumentId === doc.id
                                ? theme.palette.primary.main
                                : 'transparent'
                            }`,
                            bgcolor: selectedDocumentId === doc.id
                              ? alpha(theme.palette.primary.main, 0.08)
                              : 'transparent',
                            transition: 'all 0.2s',
                            '&:hover': {
                              bgcolor: alpha(theme.palette.primary.main, 0.05),
                              transform: 'translateX(4px)',
                            },
                          }}
                          onClick={() => handleDocumentSelect(doc.id)}
                        >
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Box
                              sx={{
                                width: 40,
                                height: 40,
                                borderRadius: 1,
                                bgcolor: alpha(theme.palette.primary.main, 0.1),
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                              }}
                            >
                              <LocalHospital sx={{ color: theme.palette.primary.main }} />
                            </Box>
                            <Box sx={{ flex: 1 }}>
                              <Typography variant="body1" fontWeight={600}>
                                {doc.filename}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                                <Chip
                                  label={doc.file_type}
                                  size="small"
                                  sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                                <Chip
                                  label={doc.processing_status}
                                  size="small"
                                  color={doc.processing_status === 'processed' ? 'success' : 'default'}
                                  sx={{ height: 20, fontSize: '0.7rem' }}
                                />
                                {doc.is_anonymized && (
                                  <Chip
                                    label="Anonymisé"
                                    size="small"
                                    color="info"
                                    sx={{ height: 20, fontSize: '0.7rem' }}
                                  />
                                )}
                              </Box>
                            </Box>
                            {selectedDocumentId === doc.id && (
                              <CheckCircle sx={{ color: theme.palette.primary.main }} />
                            )}
                          </Box>
                        </Paper>
                      ))}
                    </Box>
                  ) : (
                    <Alert severity="info" sx={{ mt: 2 }}>
                      {searchQuery
                        ? `Aucun document trouvé pour "${searchQuery}"`
                        : `Aucun document trouvé pour le patient ${patientId}`}
                    </Alert>
                  )}
                </Grid>

            {/* Right Column - Action & Stats */}
            <Grid item xs={12} md={4}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, height: '100%' }}>
                {/* Selected Document Info */}
                {selectedDocument && (
                  <Paper
                    elevation={0}
                    sx={{
                      p: 2,
                      border: `1px solid ${alpha(theme.palette.success.main, 0.3)}`,
                      bgcolor: alpha(theme.palette.success.main, 0.05),
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 1, display: 'block' }}>
                      DOCUMENT SÉLECTIONNÉ
                    </Typography>
                    <Typography variant="body2" fontWeight={600} noWrap>
                      {selectedDocument.filename}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {selectedDocument.file_type} • {(selectedDocument.file_size / 1024).toFixed(1)} KB
                    </Typography>
                  </Paper>
                )}

                {/* Analyze Button */}
                <ButtonComponent
                  variant="contained"
                  color="primary"
                  fullWidth
                  onClick={handleAnalyze}
                  loading={analyzeMutation.isPending}
                  disabled={!selectedDocumentId}
                  startIcon={<Send />}
                  sx={{
                    py: 1.8,
                    fontWeight: 600,
                    textTransform: 'none',
                    fontSize: '1rem',
                  }}
                >
                  {analyzeMutation.isPending ? 'Analyse en cours...' : 'Analyser avec IA'}
                </ButtonComponent>

                {analyzeMutation.isPending && <LinearProgress />}

                {/* Quick Stats */}
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    flex: 1,
                    border: `1px solid ${theme.palette.divider}`,
                    bgcolor: alpha(theme.palette.primary.main, 0.03),
                  }}
                >
                  <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ mb: 2, display: 'block' }}>
                    STATISTIQUES
                  </Typography>

                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Classification
                      </Typography>
                      <Typography variant="h5" fontWeight={700}>
                        {classificationResult ? `${(classificationResult.confidence * 100).toFixed(0)}%` : '-'}
                      </Typography>
                    </Box>
                    <Divider />
                    <Box>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Entités NER
                      </Typography>
                      <Typography variant="h5" fontWeight={700}>
                        {entitiesResult?.Count || 0}
                      </Typography>
                    </Box>
                    {processingTime > 0 && (
                      <>
                        <Divider />
                        <Box>
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            Temps
                          </Typography>
                          <Typography variant="h5" fontWeight={700}>
                            {processingTime}ms
                          </Typography>
                        </Box>
                      </>
                    )}
                  </Box>
                </Paper>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
        </>
      )}

      {/* Results Section - Only show if documents are visible */}
      {showDocuments && (
        <Grid container spacing={3}>
        {/* Classification Results with Doughnut Chart */}
        {classificationResult && doughnutData && (
          <>
            {/* Predicted Class - Hero Card */}
            <Grid item xs={12} md={4}>
              <Card
                elevation={3}
                sx={{
                  height: '100%',
                  position: 'relative',
                  overflow: 'hidden',
                  background: `linear-gradient(135deg, ${alpha(
                    DOC_TYPE_COLORS[classificationResult.predicted_class] || '#3b82f6',
                    0.15
                  )} 0%, ${alpha(DOC_TYPE_COLORS[classificationResult.predicted_class] || '#3b82f6', 0.05)} 100%)`,
                  border: `2px solid ${DOC_TYPE_COLORS[classificationResult.predicted_class] || '#3b82f6'}`,
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: `0 20px 40px ${alpha(DOC_TYPE_COLORS[classificationResult.predicted_class] || '#3b82f6', 0.3)}`,
                  },
                }}
              >
                <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <LocalHospital
                      sx={{
                        fontSize: 64,
                        color: DOC_TYPE_COLORS[classificationResult.predicted_class] || '#3b82f6',
                        mb: 2,
                      }}
                    />
                    <Typography variant="caption" color="text.secondary" fontWeight={700} sx={{ display: 'block', mb: 1 }}>
                      TYPE DÉTECTÉ
                    </Typography>
                    <Typography variant="h4" fontWeight={800} sx={{ textTransform: 'uppercase', mb: 3, wordBreak: 'break-word' }}>
                      {classificationResult.predicted_class.replace(/_/g, ' ')}
                    </Typography>
                  </Box>

                  <Divider sx={{ my: 2 }} />

                  <Box sx={{ textAlign: 'center', mb: 2 }}>
                    <Typography variant="caption" color="text.secondary" fontWeight={700}>
                      NIVEAU DE CONFIANCE
                    </Typography>
                    <Box sx={{ position: 'relative', display: 'inline-flex', mt: 2 }}>
                      <CircularProgress
                        variant="determinate"
                        value={classificationResult.confidence * 100}
                        size={120}
                        thickness={6}
                        sx={{
                          color: DOC_TYPE_COLORS[classificationResult.predicted_class] || '#3b82f6',
                          '& .MuiCircularProgress-circle': {
                            strokeLinecap: 'round',
                          },
                        }}
                      />
                      <Box
                        sx={{
                          top: 0,
                          left: 0,
                          bottom: 0,
                          right: 0,
                          position: 'absolute',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}
                      >
                        <Typography variant="h4" fontWeight={800}>
                          {(classificationResult.confidence * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                    </Box>
                  </Box>

                  <Chip
                    label={classificationResult.model_used === 'pretrained' ? 'Modèle Pré-entraîné' : 'Modèle Fine-tuné'}
                    size="small"
                    color={classificationResult.model_used === 'finetuned' ? 'success' : 'default'}
                    sx={{ alignSelf: 'center', fontWeight: 700, mt: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            {/* Doughnut Chart - All Probabilities */}
            <Grid item xs={12} md={8}>
              <Card elevation={3} sx={{ height: '100%' }}>
                <CardContent sx={{ p: 4 }}>
                  <Typography variant="h6" fontWeight={700} sx={{ mb: 3 }}>
                    Distribution des Probabilités
                  </Typography>
                  <Box sx={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Doughnut
                      data={doughnutData}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'right',
                            labels: {
                              font: {
                                size: 14,
                                weight: '600',
                              },
                              padding: 15,
                              usePointStyle: true,
                              pointStyle: 'circle',
                            },
                          },
                          tooltip: {
                            callbacks: {
                              label: (context) => {
                                return ` ${context.label}: ${context.parsed}%`;
                              },
                            },
                            backgroundColor: alpha(theme.palette.background.paper, 0.95),
                            titleColor: theme.palette.text.primary,
                            bodyColor: theme.palette.text.primary,
                            borderColor: theme.palette.divider,
                            borderWidth: 1,
                            padding: 12,
                            displayColors: true,
                            boxPadding: 6,
                          },
                        },
                        cutout: '65%',
                      }}
                    />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}

        {/* Entity Extraction Results */}
        {entitiesResult && entitiesResult.Count > 0 && (
          <>
            {/* Radar Chart */}
            {radarData && (
              <Grid item xs={12} md={6}>
                <Card elevation={3} sx={{ height: '100%' }}>
                  <CardContent sx={{ p: 4 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                      <Typography variant="h6" fontWeight={700}>
                        Analyse de Confiance NER
                      </Typography>
                      <Chip label={`${entitiesResult.Count} entités`} color="primary" sx={{ fontWeight: 700 }} />
                    </Box>
                    <Box sx={{ height: 350 }}>
                      <Radar
                        data={radarData}
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          scales: {
                            r: {
                              beginAtZero: true,
                              max: 100,
                              ticks: {
                                stepSize: 20,
                                font: {
                                  size: 11,
                                },
                              },
                              pointLabels: {
                                font: {
                                  size: 13,
                                  weight: '600',
                                },
                              },
                              grid: {
                                color: alpha(theme.palette.divider, 0.3),
                              },
                            },
                          },
                          plugins: {
                            legend: {
                              display: false,
                            },
                            tooltip: {
                              callbacks: {
                                label: (context) => ` Confiance: ${context.parsed.r.toFixed(1)}%`,
                              },
                            },
                          },
                        }}
                      />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}

            {/* Entity Cards Grid */}
            <Grid item xs={12} md={radarData ? 6 : 12}>
              <Card elevation={3} sx={{ height: '100%' }}>
                <CardContent sx={{ p: 4 }}>
                  <Typography variant="h6" fontWeight={700} sx={{ mb: 3 }}>
                    Entités Médicales Extraites
                  </Typography>
                  <Box sx={{ maxHeight: radarData ? 430 : 'auto', overflowY: 'auto', pr: 1 }}>
                    <Grid container spacing={2}>
                      {entitiesResult.value.map((entity, idx) => (
                        <Grid item xs={12} sm={radarData ? 12 : 6} md={radarData ? 12 : 4} lg={radarData ? 12 : 3} key={idx}>
                          <Paper
                            elevation={0}
                            sx={{
                              p: 2.5,
                              borderRadius: 3,
                              border: '2px solid',
                              borderColor: alpha(ENTITY_COLORS[entity.label] || ENTITY_COLORS.DEFAULT, 0.3),
                              bgcolor: alpha(ENTITY_COLORS[entity.label] || ENTITY_COLORS.DEFAULT, 0.05),
                              transition: 'all 0.3s',
                              '&:hover': {
                                transform: 'translateY(-4px)',
                                boxShadow: 4,
                                borderColor: ENTITY_COLORS[entity.label] || ENTITY_COLORS.DEFAULT,
                              },
                            }}
                          >
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', mb: 1.5 }}>
                              <Chip
                                label={entity.label}
                                size="small"
                                sx={{
                                  bgcolor: ENTITY_COLORS[entity.label] || ENTITY_COLORS.DEFAULT,
                                  color: 'white',
                                  fontWeight: 800,
                                  fontSize: '0.65rem',
                                  letterSpacing: 0.5,
                                }}
                              />
                              <Tooltip title="Copier">
                                <IconButton size="small" onClick={() => copyToClipboard(entity.text)}>
                                  <CopyIcon fontSize="small" />
                                </IconButton>
                              </Tooltip>
                            </Box>
                            <Typography
                              variant="body2"
                              fontWeight={700}
                              sx={{
                                wordBreak: 'break-word',
                                mb: 1.5,
                                minHeight: 40,
                                display: '-webkit-box',
                                WebkitLineClamp: 2,
                                WebkitBoxOrient: 'vertical',
                                overflow: 'hidden',
                              }}
                            >
                              {entity.text}
                            </Typography>
                            <Box>
                              <Typography
                                variant="caption"
                                color="text.secondary"
                                fontWeight={700}
                                sx={{ display: 'block', mb: 0.5 }}
                              >
                                Confiance: {(entity.confidence * 100).toFixed(0)}%
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={entity.confidence * 100}
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  bgcolor: alpha(ENTITY_COLORS[entity.label] || ENTITY_COLORS.DEFAULT, 0.2),
                                  '& .MuiLinearProgress-bar': {
                                    bgcolor: ENTITY_COLORS[entity.label] || ENTITY_COLORS.DEFAULT,
                                    borderRadius: 3,
                                  },
                                }}
                              />
                            </Box>
                          </Paper>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}

        {/* Performance Stats Cards */}
        {(classificationResult || entitiesResult || processingTime > 0) && (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <Card
                elevation={2}
                sx={{
                  background: `linear-gradient(135deg, ${alpha('#10b981', 0.1)} 0%, ${alpha('#10b981', 0.05)} 100%)`,
                  border: `1px solid ${alpha('#10b981', 0.2)}`,
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 24px ${alpha('#10b981', 0.2)}`,
                  },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: alpha('#10b981', 0.15),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <CheckCircle sx={{ color: '#10b981', fontSize: 28 }} />
                    </Box>
                    <Typography variant="body2" fontWeight={600} color="text.secondary">
                      Classification
                    </Typography>
                  </Box>
                  <Typography variant="h3" fontWeight={800} sx={{ mb: 0.5 }}>
                    {classificationResult ? '✓' : '-'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {classificationResult ? `${(classificationResult.confidence * 100).toFixed(0)}% confiance` : 'En attente'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card
                elevation={2}
                sx={{
                  background: `linear-gradient(135deg, ${alpha('#3b82f6', 0.1)} 0%, ${alpha('#3b82f6', 0.05)} 100%)`,
                  border: `1px solid ${alpha('#3b82f6', 0.2)}`,
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 24px ${alpha('#3b82f6', 0.2)}`,
                  },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: alpha('#3b82f6', 0.15),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <LocalHospital sx={{ color: '#3b82f6', fontSize: 28 }} />
                    </Box>
                    <Typography variant="body2" fontWeight={600} color="text.secondary">
                      Entités NER
                    </Typography>
                  </Box>
                  <Typography variant="h3" fontWeight={800} sx={{ mb: 0.5 }}>
                    {entitiesResult?.Count || 0}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {entitiesResult ? 'Extraites' : 'En attente'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card
                elevation={2}
                sx={{
                  background: `linear-gradient(135deg, ${alpha('#f59e0b', 0.1)} 0%, ${alpha('#f59e0b', 0.05)} 100%)`,
                  border: `1px solid ${alpha('#f59e0b', 0.2)}`,
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 24px ${alpha('#f59e0b', 0.2)}`,
                  },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: alpha('#f59e0b', 0.15),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <SpeedIcon sx={{ color: '#f59e0b', fontSize: 28 }} />
                    </Box>
                    <Typography variant="body2" fontWeight={600} color="text.secondary">
                      Performance
                    </Typography>
                  </Box>
                  <Typography variant="h3" fontWeight={800} sx={{ mb: 0.5 }}>
                    {processingTime > 0 ? `${processingTime}` : '-'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {processingTime > 0 ? 'milliseconds' : 'En attente'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card
                elevation={2}
                sx={{
                  background: `linear-gradient(135deg, ${alpha('#8b5cf6', 0.1)} 0%, ${alpha('#8b5cf6', 0.05)} 100%)`,
                  border: `1px solid ${alpha('#8b5cf6', 0.2)}`,
                  transition: 'all 0.3s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: `0 12px 24px ${alpha('#8b5cf6', 0.2)}`,
                  },
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: alpha('#8b5cf6', 0.15),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <AIIcon sx={{ color: '#8b5cf6', fontSize: 28 }} />
                    </Box>
                    <Typography variant="body2" fontWeight={600} color="text.secondary">
                      Modèles IA
                    </Typography>
                  </Box>
                  <Typography variant="h3" fontWeight={800} sx={{ mb: 0.5 }}>
                    2
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    CamemBERT + BioBERT
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </>
        )}

        {/* Empty State - Full Width */}
        {!classificationResult && !entitiesResult && !analyzeMutation.isPending && (
          <Grid item xs={12}>
            <Card
              elevation={0}
              sx={{
                p: 8,
                textAlign: 'center',
                border: `2px dashed ${alpha(theme.palette.primary.main, 0.2)}`,
                background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.03)} 0%, ${alpha(theme.palette.secondary.main, 0.03)} 100%)`,
              }}
            >
              <Box
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 2,
                  mb: 3,
                }}
              >
                <Box
                  sx={{
                    width: 64,
                    height: 64,
                    borderRadius: 3,
                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <AIIcon sx={{ fontSize: 32, color: theme.palette.primary.main }} />
                </Box>
                <Box
                  sx={{
                    width: 64,
                    height: 64,
                    borderRadius: 3,
                    bgcolor: alpha('#10b981', 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Science sx={{ fontSize: 32, color: '#10b981' }} />
                </Box>
                <Box
                  sx={{
                    width: 64,
                    height: 64,
                    borderRadius: 3,
                    bgcolor: alpha('#3b82f6', 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Biotech sx={{ fontSize: 32, color: '#3b82f6' }} />
                </Box>
              </Box>
              <Typography variant="h5" fontWeight={700} gutterBottom>
                Prêt à analyser vos documents médicaux
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3, maxWidth: 600, mx: 'auto' }}>
                Sélectionnez un document déjà importé dans votre application et cliquez sur "Analyser avec IA" pour obtenir la classification automatique et l'extraction des entités médicales.
              </Typography>
            </Card>
          </Grid>
        )}

        {/* Loading State - Full Width */}
        {analyzeMutation.isPending && (
          <Grid item xs={12}>
            <Card elevation={2} sx={{ p: 6, textAlign: 'center' }}>
              <Box
                sx={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: 3,
                }}
              >
                <Box sx={{ position: 'relative' }}>
                  <CircularProgress size={80} thickness={3.5} />
                  <Box
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                    }}
                  >
                    <AIIcon sx={{ fontSize: 36, color: theme.palette.primary.main }} />
                  </Box>
                </Box>
                <Box>
                  <Typography variant="h6" fontWeight={700} gutterBottom>
                    Analyse IA en cours...
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    Nos modèles CamemBERT et BioBERT analysent votre document
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1.5, justifyContent: 'center', flexWrap: 'wrap' }}>
                    <Chip
                      icon={<Science />}
                      label="Classification en cours"
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                    <Chip
                      icon={<Biotech />}
                      label="Extraction des entités"
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  </Box>
                </Box>
              </Box>
            </Card>
          </Grid>
        )}

        {/* Bottom Information Cards */}
        <Grid item xs={12}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
          <Card
            elevation={1}
            sx={{
              height: '100%',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: theme.shadows[6],
              },
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.primary.main, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <BarChartIcon sx={{ color: 'primary.main', fontSize: 28 }} />
                </Box>
                <Typography variant="h6" fontWeight={700}>
                  CamemBERT
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                Modèle de classification basé sur BERT, pré-entraîné sur du français. 110M paramètres. Classification en 7
                types de documents médicaux.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card
            elevation={1}
            sx={{
              height: '100%',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: theme.shadows[6],
              },
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.success.main, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <LabelIcon sx={{ color: 'success.main', fontSize: 28 }} />
                </Box>
                <Typography variant="h6" fontWeight={700}>
                  BioBERT
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                Modèle NER spécialisé biomédical. Extraction d'entités: maladies, médicaments, dosages, tests, symptômes et
                anatomie.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card
            elevation={1}
            sx={{
              height: '100%',
              transition: 'all 0.3s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: theme.shadows[6],
              },
            }}
          >
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Box
                  sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    bgcolor: alpha(theme.palette.warning.main, 0.1),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <TrendingUp sx={{ color: 'warning.main', fontSize: 28 }} />
                </Box>
                <Typography variant="h6" fontWeight={700}>
                  Performance
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ lineHeight: 1.7 }}>
                Inférence rapide sur CPU (~50-80ms). Modèles pré-entraînés prêts. Fine-tuning disponible sur Google Colab
                pour améliorer la précision.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
          </Grid>
        </Grid>
      </Grid>
      )}
    </Box>
  );
};

export default MLAnalytics;
