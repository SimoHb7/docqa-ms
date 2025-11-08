import { useState, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Grid,
  Chip,
  alpha,
  useTheme,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
} from '@mui/material';
import {
  CloudUpload,
  CheckCircle,
  Error as ErrorIcon,
  Description,
  Close,
  Person,
  LocalHospital,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { documentsApi } from '../services/api';

interface DocumentMetadata {
  patient_id?: string;
  patient_name?: string;
  department?: string;
  document_date?: string;
  notes?: string;
}

interface UploadedFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  id: string;
  metadata?: DocumentMetadata;
}

export default function ModernUpload() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [metadataDialogOpen, setMetadataDialogOpen] = useState(false);
  const [currentMetadata, setCurrentMetadata] = useState<DocumentMetadata>({
    patient_id: '',
    patient_name: '',
    department: '',
    document_date: new Date().toISOString().split('T')[0],
    notes: '',
  });

  const handleMetadataSubmit = async () => {
    setMetadataDialogOpen(false);
    
    const newFiles: UploadedFile[] = pendingFiles.map((file) => ({
      file,
      progress: 0,
      status: 'uploading',
      id: Math.random().toString(36).substr(2, 9),
      metadata: currentMetadata,
    }));

    setFiles((prev) => [...prev, ...newFiles]);

    // Upload each file with metadata
    for (const uploadFile of newFiles) {
      try {
        const formData = new FormData();
        formData.append('file', uploadFile.file);
        
        // Add metadata fields
        if (currentMetadata.patient_id) formData.append('patient_id', currentMetadata.patient_id);
        if (currentMetadata.patient_name) formData.append('patient_name', currentMetadata.patient_name);
        if (currentMetadata.department) formData.append('department', currentMetadata.department);
        if (currentMetadata.document_date) formData.append('document_date', currentMetadata.document_date);
        if (currentMetadata.notes) formData.append('notes', currentMetadata.notes);

        await documentsApi.upload(formData, (progress) => {
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uploadFile.id ? { ...f, progress } : f
            )
          );
        });

        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id ? { ...f, status: 'success', progress: 100 } : f
          )
        );
      } catch (error) {
        setFiles((prev) =>
          prev.map((f) =>
            f.id === uploadFile.id ? { ...f, status: 'error' } : f
          )
        );
      }
    }

    // Reset pending files and metadata
    setPendingFiles([]);
    setCurrentMetadata({
      patient_id: '',
      patient_name: '',
      department: '',
      document_date: new Date().toISOString().split('T')[0],
      notes: '',
    });
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setPendingFiles(acceptedFiles);
    setMetadataDialogOpen(true);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
  });

  const removeFile = (id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const getFileIcon = (filename: string) => {
    if (filename.endsWith('.pdf')) return '#d32f2f';
    if (filename.endsWith('.docx')) return '#1976d2';
    return '#757575';
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Importer des documents
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Glissez-déposez vos documents médicaux ou cliquez pour les sélectionner
        </Typography>
      </Box>

      {/* Upload Zone */}
      <Card
        {...getRootProps()}
        sx={{
          mb: 4,
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          border: `2px dashed ${isDragActive ? theme.palette.primary.main : theme.palette.divider}`,
          bgcolor: isDragActive ? alpha(theme.palette.primary.main, 0.08) : 'background.paper',
          '&:hover': {
            borderColor: theme.palette.primary.main,
            bgcolor: alpha(theme.palette.primary.main, 0.04),
          },
        }}
      >
        <CardContent>
          <input {...getInputProps()} />
          <Box
            sx={{
              py: 8,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <CloudUpload sx={{ fontSize: 40, color: 'primary.main' }} />
            </Box>

            <Typography variant="h6" fontWeight={600}>
              {isDragActive ? 'Déposez vos fichiers ici' : 'Glissez vos fichiers ici'}
            </Typography>

            <Typography variant="body2" color="text.secondary" textAlign="center">
              ou cliquez pour parcourir vos fichiers
              <br />
              <Box component="span" sx={{ fontWeight: 600 }}>
                PDF, DOCX, TXT
              </Box>{' '}
              • Max 50 MB par fichier
            </Typography>

            <Button
              variant="contained"
              sx={{
                mt: 2,
                borderRadius: 3,
                px: 4,
                textTransform: 'none',
                fontWeight: 600,
              }}
            >
              Sélectionner des fichiers
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Uploaded Files */}
      {files.length > 0 && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" fontWeight={600}>
                Fichiers en cours d'import ({files.length})
              </Typography>
              {files.every((f) => f.status === 'success') && (
                <Button variant="contained" onClick={() => navigate('/documents')}>
                  Voir mes documents
                </Button>
              )}
            </Box>

            <List>
              {files.map((uploadFile) => (
                <ListItem
                  key={uploadFile.id}
                  sx={{
                    mb: 2,
                    p: 2,
                    borderRadius: 2,
                    bgcolor: 'background.default',
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                  secondaryAction={
                    uploadFile.status === 'success' && (
                      <IconButton edge="end" onClick={() => removeFile(uploadFile.id)}>
                        <Close />
                      </IconButton>
                    )
                  }
                >
                  <ListItemIcon>
                    <Box
                      sx={{
                        width: 48,
                        height: 48,
                        borderRadius: 2,
                        bgcolor: alpha(getFileIcon(uploadFile.file.name), 0.1),
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Description sx={{ color: getFileIcon(uploadFile.file.name) }} />
                    </Box>
                  </ListItemIcon>

                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="subtitle2" fontWeight={600}>
                          {uploadFile.file.name}
                        </Typography>
                        {uploadFile.status === 'success' && (
                          <CheckCircle sx={{ fontSize: 20, color: 'success.main' }} />
                        )}
                        {uploadFile.status === 'error' && (
                          <ErrorIcon sx={{ fontSize: 20, color: 'error.main' }} />
                        )}
                      </Box>
                    }
                    secondary={
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          {(uploadFile.file.size / 1024 / 1024).toFixed(2)} MB
                        </Typography>
                        {uploadFile.status === 'uploading' && (
                          <Box sx={{ mt: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={uploadFile.progress}
                              sx={{ height: 6, borderRadius: 3 }}
                            />
                            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                              {uploadFile.progress}%
                            </Typography>
                          </Box>
                        )}
                        {uploadFile.status === 'success' && (
                          <Typography variant="caption" color="success.main" sx={{ fontWeight: 600 }}>
                            ✓ Import réussi
                          </Typography>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}

      {/* Tips */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                📄 Formats acceptés
              </Typography>
              <Typography variant="body2" color="text.secondary">
                PDF, DOCX, TXT, HL7, FHIR
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                🔒 Sécurité
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Vos documents sont chiffrés et conformes RGPD
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                ⚡ Traitement rapide
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Analyse automatique et indexation en quelques secondes
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Metadata Dialog */}
      <Dialog 
        open={metadataDialogOpen} 
        onClose={() => setMetadataDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Person color="primary" />
            <Typography variant="h6" fontWeight={600}>
              Informations sur le document
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 2 }}>
            <TextField
              label="ID Patient"
              placeholder="PAT-12345"
              value={currentMetadata.patient_id}
              onChange={(e) => setCurrentMetadata({ ...currentMetadata, patient_id: e.target.value })}
              helperText="Identifiant unique du patient (optionnel)"
              InputProps={{
                startAdornment: <Person sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />

            <TextField
              label="Nom du Patient"
              placeholder="Nom Prénom"
              value={currentMetadata.patient_name}
              onChange={(e) => setCurrentMetadata({ ...currentMetadata, patient_name: e.target.value })}
              helperText="Nom complet du patient (optionnel)"
            />

            <TextField
              select
              label="Service / Département"
              value={currentMetadata.department}
              onChange={(e) => setCurrentMetadata({ ...currentMetadata, department: e.target.value })}
              helperText="Service médical concerné (optionnel)"
              InputProps={{
                startAdornment: <LocalHospital sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            >
              <MenuItem value="">Aucun</MenuItem>
              <MenuItem value="cardiologie">Cardiologie</MenuItem>
              <MenuItem value="urgences">Urgences</MenuItem>
              <MenuItem value="pediatrie">Pédiatrie</MenuItem>
              <MenuItem value="chirurgie">Chirurgie</MenuItem>
              <MenuItem value="radiologie">Radiologie</MenuItem>
              <MenuItem value="laboratoire">Laboratoire</MenuItem>
              <MenuItem value="medecine-generale">Médecine générale</MenuItem>
              <MenuItem value="autre">Autre</MenuItem>
            </TextField>

            <TextField
              label="Date du Document"
              type="date"
              value={currentMetadata.document_date}
              onChange={(e) => setCurrentMetadata({ ...currentMetadata, document_date: e.target.value })}
              InputLabelProps={{ shrink: true }}
              helperText="Date de création du document médical"
            />

            <TextField
              label="Notes"
              multiline
              rows={3}
              placeholder="Notes supplémentaires sur ce document..."
              value={currentMetadata.notes}
              onChange={(e) => setCurrentMetadata({ ...currentMetadata, notes: e.target.value })}
              helperText="Informations complémentaires (optionnel)"
            />

            <Box sx={{ p: 2, bgcolor: 'info.lighter', borderRadius: 2 }}>
              <Typography variant="caption" color="info.dark">
                💡 Ces informations vous aideront à identifier et retrouver facilement vos documents, 
                surtout si vous avez plusieurs fichiers avec le même nom.
              </Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 3, pt: 0 }}>
          <Button 
            onClick={() => setMetadataDialogOpen(false)}
            variant="outlined"
          >
            Annuler
          </Button>
          <Button 
            onClick={handleMetadataSubmit}
            variant="contained"
            startIcon={<CloudUpload />}
          >
            Importer {pendingFiles.length} fichier(s)
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
