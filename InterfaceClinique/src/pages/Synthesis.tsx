import React, { useState } from 'react';
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
  Paper,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Assessment as SynthesisIcon,
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useQuery, useMutation } from '@tanstack/react-query';
import { synthesisApi } from '../services/api';
import { formatDate } from '../utils';
import { SynthesisRequest, SynthesisResponse } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ButtonComponent from '../components/ui/Button';
import CardComponent from '../components/ui/Card';

const Synthesis: React.FC = () => {
  const [synthesisType, setSynthesisType] = useState<'patient_timeline' | 'treatment_summary' | 'diagnostic_report' | 'custom'>('patient_timeline');
  const [patientId, setPatientId] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [customPrompt, setCustomPrompt] = useState('');

  // Fetch existing syntheses
  const { data: syntheses, isLoading: loadingSyntheses, refetch } = useQuery({
    queryKey: ['syntheses'],
    queryFn: () => synthesisApi.list({ limit: 10 }),
  });

  // Create synthesis mutation
  const createMutation = useMutation({
    mutationFn: (request: SynthesisRequest) => synthesisApi.generate(request),
    onSuccess: () => {
      refetch();
      // Reset form
      setPatientId('');
      setDateFrom('');
      setDateTo('');
      setCustomPrompt('');
    },
  });

  const handleCreateSynthesis = () => {
    const request: SynthesisRequest = {
      type: synthesisType,
      parameters: {},
    };

    if (synthesisType === 'patient_timeline' || synthesisType === 'treatment_summary') {
      if (!patientId) {
        alert('Veuillez saisir un ID patient');
        return;
      }
      request.parameters.patient_id = patientId;
    }

    if (dateFrom || dateTo) {
      request.parameters.date_range = {
        start: dateFrom || '',
        end: dateTo || '',
      };
    }

    if (synthesisType === 'custom' && customPrompt) {
      (request.parameters as any).custom_prompt = customPrompt;
    }

    createMutation.mutate(request);
  };

  const handleDownloadSynthesis = (synthesis: SynthesisResponse) => {
    const content = `# ${synthesis.type.replace('_', ' ').toUpperCase()}

Généré le: ${formatDate(synthesis.generated_at)}

${synthesis.content}

## Sources
${synthesis.sources.map(source => `- ${source.filename} (${source.relevance_score.toFixed(2)})`).join('\n')}
`;

    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `synthese-${synthesis.synthesis_id}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const getSynthesisTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      patient_timeline: 'Chronologie patient',
      treatment_summary: 'Résumé traitement',
      diagnostic_report: 'Rapport diagnostic',
      custom: 'Synthèse personnalisée',
    };
    return labels[type] || type;
  };

  const synthesisTypes = [
    {
      value: 'patient_timeline',
      label: 'Chronologie patient',
      description: 'Chronologie complète de l\'historique médical d\'un patient',
    },
    {
      value: 'treatment_summary',
      label: 'Résumé traitement',
      description: 'Synthèse des traitements et médicaments prescrits',
    },
    {
      value: 'diagnostic_report',
      label: 'Rapport diagnostic',
      description: 'Rapport consolidé des diagnostics et examens',
    },
    {
      value: 'custom',
      label: 'Synthèse personnalisée',
      description: 'Synthèse sur mesure selon vos critères',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
        Synthèses médicales
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Générez des rapports et synthèses intelligentes à partir de vos documents médicaux
      </Typography>

      <Box display="flex" gap={4}>
        {/* Create Synthesis Form */}
        <Box flex={1}>
          <CardComponent title="Créer une synthèse" icon={<SynthesisIcon />}>
            <CardContent>
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Type de synthèse</InputLabel>
                <Select
                  value={synthesisType}
                  onChange={(e) => setSynthesisType(e.target.value as any)}
                  label="Type de synthèse"
                >
                  {synthesisTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      <Box>
                        <Typography variant="body2" fontWeight={500}>
                          {type.label}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {type.description}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {(synthesisType === 'patient_timeline' || synthesisType === 'treatment_summary') && (
                <TextField
                  fullWidth
                  label="ID Patient"
                  value={patientId}
                  onChange={(e) => setPatientId(e.target.value)}
                  placeholder="Ex: PAT-001"
                  sx={{ mb: 3 }}
                />
              )}

              <Box display="flex" gap={2} sx={{ mb: 3 }}>
                <TextField
                  label="Date début"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  sx={{ flex: 1 }}
                />
                <TextField
                  label="Date fin"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  InputLabelProps={{ shrink: true }}
                  sx={{ flex: 1 }}
                />
              </Box>

              {synthesisType === 'custom' && (
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  label="Prompt personnalisé"
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  placeholder="Décrivez la synthèse souhaitée..."
                  sx={{ mb: 3 }}
                />
              )}

              <ButtonComponent
                fullWidth
                onClick={handleCreateSynthesis}
                loading={createMutation.isPending}
                disabled={
                  (synthesisType === 'patient_timeline' || synthesisType === 'treatment_summary') && !patientId
                }
              >
                Générer la synthèse
              </ButtonComponent>

              {createMutation.error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  Erreur lors de la génération de la synthèse
                </Alert>
              )}
            </CardContent>
          </CardComponent>
        </Box>

        {/* Recent Syntheses */}
        <Box flex={1}>
          <CardComponent title="Synthèses récentes">
            <CardContent sx={{ p: 0 }}>
              {loadingSyntheses ? (
                <LoadingSpinner />
              ) : (
                <Box>
                  {syntheses?.data?.map((synthesis) => (
                    <Accordion key={synthesis.synthesis_id}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Box display="flex" alignItems="center" gap={2} flex={1}>
                          <SynthesisIcon color="primary" />
                          <Box flex={1}>
                            <Typography variant="subtitle2" fontWeight={600}>
                              {getSynthesisTypeLabel(synthesis.type)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatDate(synthesis.generated_at)}
                            </Typography>
                          </Box>
                          <Chip
                            label={`${synthesis.sources.length} sources`}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {synthesis.content.substring(0, 200)}...
                        </Typography>

                        <Box display="flex" gap={1} flexWrap="wrap" sx={{ mb: 2 }}>
                          {synthesis.sources.map((source, index) => (
                            <Chip
                              key={index}
                              label={`${source.filename} (${source.relevance_score.toFixed(2)})`}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                        </Box>

                        <ButtonComponent
                          size="small"
                          startIcon={<DownloadIcon />}
                          onClick={() => handleDownloadSynthesis(synthesis)}
                        >
                          Télécharger
                        </ButtonComponent>
                      </AccordionDetails>
                    </Accordion>
                  ))}

                  {syntheses?.data?.length === 0 && (
                    <Box textAlign="center" py={4}>
                      <Typography color="text.secondary">
                        Aucune synthèse trouvée
                      </Typography>
                    </Box>
                  )}
                </Box>
              )}
            </CardContent>
          </CardComponent>
        </Box>
      </Box>

      {/* Usage Tips */}
      <CardComponent sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Conseils d'utilisation
          </Typography>
          <Typography variant="body2" paragraph>
            • <strong>Chronologie patient :</strong> Idéale pour suivre l'évolution d'un patient sur une période donnée.
          </Typography>
          <Typography variant="body2" paragraph>
            • <strong>Résumé traitement :</strong> Consolide tous les traitements et médicaments d'un patient.
          </Typography>
          <Typography variant="body2" paragraph>
            • <strong>Rapport diagnostic :</strong> Synthèse des diagnostics et résultats d'examens.
          </Typography>
          <Typography variant="body2" paragraph>
            • <strong>Synthèse personnalisée :</strong> Utilisez un prompt spécifique pour des analyses sur mesure.
          </Typography>
          <Alert severity="info" sx={{ mt: 2 }}>
            Les synthèses sont générées par intelligence artificielle et utilisent uniquement les documents
            auxquels vous avez accès selon vos permissions.
          </Alert>
        </CardContent>
      </CardComponent>
    </Box>
  );
};

export default Synthesis;