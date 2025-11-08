import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  LinearProgress,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Delete as DeleteIcon,
  Description as FileIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { documentsApi } from '../services/api';
import { formatFileSize } from '../utils';
import { UploadProgress } from '../types';
import ButtonComponent from '../components/ui/Button';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB (increased to match backend)
const ACCEPTED_TYPES = {
  // Primary document formats
  'application/pdf': ['.pdf'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt'],
  // Medical standard formats
  'application/hl7-v2': ['.hl7'],
  'application/fhir+json': ['.fhir'],
  'application/json': ['.json'],
  'application/xml': ['.xml', '.hl7'],
  // Spreadsheets (for lab results)
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel': ['.xls'],
  'text/csv': ['.csv'],
  // Medical imaging formats
  'application/dicom': ['.dcm', '.dicom'],
  // Images (for scanned documents)
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
};

const Upload: React.FC = () => {
  const navigate = useNavigate();
  const [files, setFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<Record<string, UploadProgress>>({});
  const [metadataDialog, setMetadataDialog] = useState(false);
  const [bulkMetadataDialog, setBulkMetadataDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [metadata, setMetadata] = useState({
    patient_id: '',
    document_type: '',
  });
  const [bulkMetadata, setBulkMetadata] = useState({
    patient_id: '',
    document_type: '',
  });

  // Upload mutation - accepts metadata as parameter
  const uploadMutation = useMutation({
    mutationFn: async ({ file, fileMetadata }: { file: File; fileMetadata: { patient_id: string; document_type: string } }) => {
      const formData = new FormData();
      formData.append('file', file);

      // Add metadata if provided
      if (fileMetadata.patient_id) formData.append('patient_id', fileMetadata.patient_id);
      if (fileMetadata.document_type) formData.append('document_type', fileMetadata.document_type);

      console.log('Uploading file with metadata:', {
        filename: file.name,
        patient_id: fileMetadata.patient_id,
        document_type: fileMetadata.document_type
      });

      return documentsApi.upload(formData, (progress) => {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: {
            ...prev[file.name],
            progress,
          },
        }));
      });
    },
    onSuccess: (data, { file }) => {
      setUploadProgress(prev => ({
        ...prev,
        [file.name]: {
          ...prev[file.name],
          status: 'complete',
          document_id: data.data.document_id,
        },
      }));
    },
    onError: (_error, { file }) => {
      setUploadProgress(prev => ({
        ...prev,
        [file.name]: {
          ...prev[file.name],
          status: 'error',
          error: 'Erreur lors du téléchargement',
        },
      }));
    },
  });

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const validFiles = acceptedFiles.filter(file => {
      if (file.size > MAX_FILE_SIZE) {
        alert(`Le fichier ${file.name} est trop volumineux. Taille maximale: 10MB`);
        return false;
      }
      return true;
    });

    setFiles(prev => [...prev, ...validFiles]);

    // Initialize progress for new files
    const newProgress: Record<string, UploadProgress> = {};
    validFiles.forEach(file => {
      newProgress[file.name] = {
        file,
        progress: 0,
        status: 'pending',
      };
    });
    setUploadProgress(prev => ({ ...prev, ...newProgress }));
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxSize: MAX_FILE_SIZE,
    multiple: true,
  });

  const handleRemoveFile = (fileName: string) => {
    setFiles(prev => prev.filter(f => f.name !== fileName));
    setUploadProgress(prev => {
      const newProgress = { ...prev };
      delete newProgress[fileName];
      return newProgress;
    });
  };

  const handleUploadAll = () => {
    // Open bulk metadata dialog first
    setBulkMetadataDialog(true);
  };

  const handleBulkUpload = () => {
    // Upload all pending files with the bulk metadata
    files.forEach(file => {
      if (uploadProgress[file.name]?.status === 'pending') {
        setUploadProgress(prev => ({
          ...prev,
          [file.name]: {
            ...prev[file.name],
            status: 'uploading',
          },
        }));
        uploadMutation.mutate({ file, fileMetadata: bulkMetadata });
      }
    });
    setBulkMetadataDialog(false);
    // Reset bulk metadata after upload
    setBulkMetadata({ patient_id: '', document_type: '' });
  };

  const handleUploadSingle = (file: File) => {
    setUploadProgress(prev => ({
      ...prev,
      [file.name]: {
        ...prev[file.name],
        status: 'uploading',
      },
    }));
    uploadMutation.mutate({ file, fileMetadata: metadata });
  };

  const handleMetadataSubmit = () => {
    if (selectedFile) {
      handleUploadSingle(selectedFile);
    }
    setMetadataDialog(false);
    setSelectedFile(null);
    // Reset single file metadata after upload
    setMetadata({ patient_id: '', document_type: '' });
  };

  const allUploaded = files.length > 0 && files.every(file =>
    uploadProgress[file.name]?.status === 'complete'
  );

  const hasErrors = Object.values(uploadProgress).some(p => p.status === 'error');

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
        Téléchargement de documents
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Téléchargez vos documents médicaux pour les analyser avec l'IA
      </Typography>

      {/* Upload Zone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          bgcolor: isDragActive ? 'primary.50' : 'background.paper',
          cursor: 'pointer',
          textAlign: 'center',
          transition: 'all 0.2s ease',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'primary.50',
          },
        }}
      >
        <input {...getInputProps()} />
        <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Déposez les fichiers ici' : 'Glissez-déposez vos fichiers ici'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          ou cliquez pour sélectionner des fichiers
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          Formats acceptés: PDF, DOC, DOCX, TXT, JPG, PNG • Taille max: 10MB par fichier
        </Typography>
      </Paper>

      {/* File List */}
      {files.length > 0 && (
        <Paper sx={{ mb: 3 }}>
          <Box p={2}>
            <Typography variant="h6" gutterBottom>
              Fichiers sélectionnés ({files.length})
            </Typography>

            <List>
              {files.map((file) => {
                const progress = uploadProgress[file.name];
                return (
                  <ListItem key={file.name} divider>
                    <FileIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemText
                      primary={file.name}
                      secondary={
                        <>
                          <Typography variant="caption" display="block">
                            {formatFileSize(file.size)} • {file.type || 'Type inconnu'}
                          </Typography>
                          {progress?.status === 'uploading' && (
                            <LinearProgress
                              variant="determinate"
                              value={progress.progress}
                              sx={{ mt: 1, height: 4, borderRadius: 2 }}
                            />
                          )}
                        </>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Box display="flex" alignItems="center" gap={1}>
                        {progress?.status === 'complete' && (
                          <Chip
                            icon={<SuccessIcon />}
                            label="Téléchargé"
                            color="success"
                            size="small"
                          />
                        )}
                        {progress?.status === 'error' && (
                          <Chip
                            icon={<ErrorIcon />}
                            label="Erreur"
                            color="error"
                            size="small"
                          />
                        )}
                        {progress?.status === 'pending' && (
                          <ButtonComponent
                            size="small"
                            onClick={() => {
                              setSelectedFile(file);
                              setMetadataDialog(true);
                            }}
                          >
                            Télécharger
                          </ButtonComponent>
                        )}
                        <IconButton
                          onClick={() => handleRemoveFile(file.name)}
                          disabled={progress?.status === 'uploading'}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                );
              })}
            </List>

            {/* Bulk Actions */}
            {files.some(file => uploadProgress[file.name]?.status === 'pending') && (
              <Box display="flex" gap={2} mt={2}>
                <ButtonComponent
                  onClick={handleUploadAll}
                  disabled={uploadMutation.isPending}
                  loading={uploadMutation.isPending}
                >
                  Télécharger tout
                </ButtonComponent>
                <ButtonComponent
                  variant="outlined"
                  onClick={() => {
                    setFiles([]);
                    setUploadProgress({});
                  }}
                >
                  Effacer tout
                </ButtonComponent>
              </Box>
            )}
          </Box>
        </Paper>
      )}

      {/* Success Message */}
      {allUploaded && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Tous les fichiers ont été téléchargés avec succès ! Ils seront traités automatiquement.
        </Alert>
      )}

      {/* Error Message */}
      {hasErrors && (
        <Alert severity="error" sx={{ mb: 3 }}>
          Certains fichiers n'ont pas pu être téléchargés. Vérifiez les erreurs et réessayez.
        </Alert>
      )}

      {/* Navigation */}
      {allUploaded && (
        <Box display="flex" gap={2}>
          <ButtonComponent onClick={() => navigate('/documents')}>
            Voir les documents
          </ButtonComponent>
          <ButtonComponent variant="outlined" onClick={() => navigate('/qa')}>
            Poser des questions
          </ButtonComponent>
        </Box>
      )}

      {/* Single File Metadata Dialog */}
      <Dialog
        open={metadataDialog}
        onClose={() => setMetadataDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Ajouter des métadonnées (optionnel)</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="ID Patient"
            value={metadata.patient_id}
            onChange={(e) => setMetadata(prev => ({ ...prev, patient_id: e.target.value }))}
            margin="normal"
            placeholder="Ex: PAT-001"
          />
          <TextField
            fullWidth
            label="Type de document"
            value={metadata.document_type}
            onChange={(e) => setMetadata(prev => ({ ...prev, document_type: e.target.value }))}
            margin="normal"
            placeholder="Ex: medical_report, prescription"
            helperText="Laissez vide pour détection automatique"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setMetadataDialog(false)}>Annuler</Button>
          <Button onClick={handleMetadataSubmit} variant="contained">
            Télécharger
          </Button>
        </DialogActions>
      </Dialog>

      {/* Bulk Upload Metadata Dialog */}
      <Dialog
        open={bulkMetadataDialog}
        onClose={() => setBulkMetadataDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Métadonnées pour tous les fichiers</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mb: 2 }}>
            Ces métadonnées seront appliquées à tous les fichiers en attente de téléchargement.
          </Alert>
          <TextField
            fullWidth
            label="ID Patient"
            value={bulkMetadata.patient_id}
            onChange={(e) => setBulkMetadata(prev => ({ ...prev, patient_id: e.target.value }))}
            margin="normal"
            placeholder="Ex: PAT-001"
          />
          <TextField
            fullWidth
            label="Type de document"
            value={bulkMetadata.document_type}
            onChange={(e) => setBulkMetadata(prev => ({ ...prev, document_type: e.target.value }))}
            margin="normal"
            placeholder="Ex: medical_report, prescription"
            helperText="Laissez vide pour détection automatique"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setBulkMetadataDialog(false)}>Annuler</Button>
          <Button onClick={handleBulkUpload} variant="contained">
            Télécharger tout ({files.filter(f => uploadProgress[f.name]?.status === 'pending').length} fichiers)
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Upload;