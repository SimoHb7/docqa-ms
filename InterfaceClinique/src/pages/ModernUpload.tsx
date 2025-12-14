import { useCallback, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Grid,

  alpha,
  useTheme,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
} from '@mui/material';
import {
  CloudUpload,
  CheckCircle,
  Error as ErrorIcon,
  Description,
  Close,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useUploadStore } from '../store/pageStores';

interface UploadedFile {
  file: File;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  id: string;
}

export default function ModernUpload() {
  const theme = useTheme();
  const navigate = useNavigate();
  
  // Use Zustand store for persistent state across navigation
  const { files, setFiles, updateFile: updateFileInStore, removeFile: removeFileFromStore } = useUploadStore();

  // Extract progress update logic to reduce nesting
  const updateFileProgress = useCallback((fileId: string, interval: NodeJS.Timeout) => {
    const currentFile = files.find(f => f.id === fileId);
    if (!currentFile) return;
    
    if (currentFile.progress >= 100) {
      clearInterval(interval);
      updateFileInStore(fileId, { status: 'success', progress: 100 });
    } else {
      updateFileInStore(fileId, { progress: Math.min(currentFile.progress + 10, 100) });
    }
  }, [files, updateFileInStore]);

  // Extract interval creation to reduce nesting
  const startFileUpload = useCallback((uploadFile: UploadedFile) => {
    const interval = setInterval(() => {
      updateFileProgress(uploadFile.id, interval);
    }, 300);
  }, [updateFileProgress]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      file,
      progress: 0,
      status: 'uploading',
      id: crypto.randomUUID(),
    }));

    setFiles([...files, ...newFiles]);

    // Simulate upload progress
    newFiles.forEach(startFileUpload);
  }, [files, setFiles, startFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
  });

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
                      <IconButton edge="end" onClick={() => removeFileFromStore(uploadFile.id)}>
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
        <Grid size={{ xs: 12, md: 4 }}>
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
        <Grid size={{ xs: 12, md: 4 }}>
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
        <Grid size={{ xs: 12, md: 4 }}>
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
    </Box>
  );
}
