import React, { useState, useMemo, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  TextField,
  InputAdornment,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Paper,
  IconButton,
  Menu,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  MoreVert as MoreIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Upload as UploadIcon,
} from '@mui/icons-material';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { documentsApi } from '../services/api';
import {
  formatDate,
  formatFileSize,
  getProcessingStatusLabel,
  getProcessingStatusColor,
  getDocumentTypeLabel,
} from '../utils';
import { Document, FilterOptions } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import ButtonComponent from '../components/ui/Button';
import CardComponent from '../components/ui/Card';

const Documents: React.FC = () => {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [filters, setFilters] = useState<FilterOptions>({});
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [viewDocument, setViewDocument] = useState<Document | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);

  // Debounce search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchQuery);
      setPage(0); // Reset to first page when search changes
    }, 500); // Wait 500ms after user stops typing

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Fetch documents
  const { data: documentsData, isLoading, error } = useQuery({
    queryKey: ['documents', page, rowsPerPage, filters, debouncedSearch],
    queryFn: async () => {
      console.log('🔍 Fetching documents with params:', {
        filters,
        search: debouncedSearch || undefined,
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      });
      const result = await documentsApi.list({
        ...filters,
        search: debouncedSearch || undefined,
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      });
      console.log('📄 Documents API response:', result);
      console.log('📊 Total documents:', result.total);
      console.log('📦 Documents in data array:', result.data?.length);
      return result;
    },
    placeholderData: (previousData) => previousData, // Keep previous data while loading
    staleTime: 30000, // Cache for 30 seconds
  });

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: (documentId: string) => documentsApi.delete(documentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setDeleteDialogOpen(false);
      setSelectedDocument(null);
    },
  });

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    // Don't reset page here - it will be reset by the useEffect when debounced search updates
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, document: Document) => {
    setMenuAnchorEl(event.currentTarget);
    setSelectedDocument(document);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    // Don't clear selectedDocument immediately - wait for menu animation to complete
    setTimeout(() => {
      setSelectedDocument(null);
    }, 200);
  };

  const handleViewDocument = () => {
    if (selectedDocument) {
      setViewDocument(selectedDocument);
      setViewDialogOpen(true);
    }
    handleMenuClose();
  };

  const handleDownloadDocument = async () => {
    const docToDownload = selectedDocument;
    if (docToDownload) {
      try {
        // Try to download via the API endpoint
        const link = document.createElement('a');
        link.href = `http://localhost:8000/api/v1/documents/${docToDownload.id}/download`;
        link.download = docToDownload.filename;
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        console.log('Download initiated:', docToDownload.filename);
      } catch (error) {
        console.error('Download failed:', error);
        alert('Le fichier original n\'est plus disponible sur le serveur. Le contenu textuel est disponible dans la base de données pour la recherche.');
      }
    }
    handleMenuClose();
  };

  const handleDeleteDocument = () => {
    if (selectedDocument) {
      setDeleteDialogOpen(true);
    }
    handleMenuClose();
  };

  const confirmDelete = () => {
    if (selectedDocument) {
      deleteMutation.mutate(selectedDocument.id);
    }
  };

  const filteredDocuments = useMemo(() => {
    if (!documentsData?.data) {
      console.log('⚠️ No documents data available');
      return [];
    }
    
    let filtered = documentsData.data;
    
    // Client-side search filtering (since backend doesn't filter)
    if (debouncedSearch) {
      const searchLower = debouncedSearch.toLowerCase();
      filtered = filtered.filter(doc => 
        doc.filename.toLowerCase().includes(searchLower) ||
        doc.patient_id?.toLowerCase().includes(searchLower) ||
        doc.document_type?.toLowerCase().includes(searchLower) ||
        doc.file_type?.toLowerCase().includes(searchLower)
      );
    }
    
    console.log('✅ Filtered documents count:', filtered.length);
    return filtered;
  }, [documentsData, debouncedSearch]);

  if (isLoading) {
    console.log('⏳ Loading documents...');
    return <LoadingSpinner message="Chargement des documents..." />;
  }

  if (error) {
    console.error('❌ Error loading documents:', error);
    return (
      <Box textAlign="center" py={4}>
        <Typography color="error">
          Erreur lors du chargement des documents
        </Typography>
      </Box>
    );
  }

  console.log('📋 Rendering documents page with:', {
    totalDocuments: documentsData?.total,
    filteredCount: filteredDocuments.length,
    isLoading,
    hasError: !!error
  });

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
            Documents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gérez vos documents médicaux et consultez leur statut de traitement
          </Typography>
        </Box>
        <ButtonComponent
          startIcon={<UploadIcon />}
          onClick={() => navigate('/upload')}
        >
          Télécharger
        </ButtonComponent>
      </Box>

      {/* Search and Filters */}
      <CardComponent sx={{ mb: 3 }}>
        <Box p={2}>
          <Box display="flex" gap={2} alignItems="center" flexWrap="wrap">
            <TextField
              placeholder="Rechercher des documents..."
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

            <ButtonComponent
              variant="outlined"
              startIcon={<FilterIcon />}
              onClick={() => {
                // Implement advanced filters dialog
                console.log('Open filters');
              }}
            >
              Filtres
            </ButtonComponent>

            {/* Active filters */}
            {filters.document_type && (
              <Chip
                label={`Type: ${filters.document_type}`}
                onDelete={() => setFilters({ ...filters, document_type: undefined })}
                size="small"
              />
            )}
            {filters.status && (
              <Chip
                label={`Statut: ${filters.status}`}
                onDelete={() => setFilters({ ...filters, status: undefined })}
                size="small"
              />
            )}
          </Box>
        </Box>
      </CardComponent>

      {/* Documents Table */}
      <CardComponent>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nom du fichier</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Taille</TableCell>
                <TableCell>Statut</TableCell>
                <TableCell>Date d'upload</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredDocuments.map((document) => (
                <TableRow key={document.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {document.filename}
                    </Typography>
                    {document.patient_id && (
                      <Typography variant="caption" color="text.secondary">
                        Patient: {document.patient_id}
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {getDocumentTypeLabel(document.document_type || 'other')}
                  </TableCell>
                  <TableCell>{formatFileSize(document.file_size)}</TableCell>
                  <TableCell>
                    <Chip
                      label={getProcessingStatusLabel(document.processing_status)}
                      size="small"
                      sx={{
                        bgcolor: getProcessingStatusColor(document.processing_status),
                        color: 'white',
                      }}
                    />
                  </TableCell>
                  <TableCell>{formatDate(document.created_at)}</TableCell>
                  <TableCell align="right">
                    <IconButton
                      onClick={(event) => handleMenuOpen(event, document)}
                      size="small"
                    >
                      <MoreIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {filteredDocuments.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      Aucun document trouvé
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>

        <TablePagination
          component="div"
          count={documentsData?.total || 0}
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

      {/* Context Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleViewDocument}>
          <ViewIcon sx={{ mr: 1 }} />
          Voir les détails
        </MenuItem>
        <MenuItem onClick={handleDownloadDocument}>
          <DownloadIcon sx={{ mr: 1 }} />
          Télécharger
        </MenuItem>
        <MenuItem onClick={handleDeleteDocument} sx={{ color: 'error.main' }}>
          <DeleteIcon sx={{ mr: 1 }} />
          Supprimer
        </MenuItem>
      </Menu>

      {/* View Document Details Dialog */}
      <Dialog
        open={viewDialogOpen}
        onClose={() => {
          setViewDialogOpen(false);
          setViewDocument(null);
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle sx={{ pb: 1 }}>Détails du document</DialogTitle>
        <DialogContent>
          {viewDocument && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="h6" gutterBottom sx={{ mb: 3, color: 'primary.main' }}>
                {viewDocument.filename}
              </Typography>
              
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Type
                  </Typography>
                  <Chip
                    label={`${getDocumentTypeLabel(viewDocument.document_type || 'other')} • ${viewDocument.file_type?.toUpperCase()}`}
                    size="small"
                    variant="outlined"
                  />
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Taille
                  </Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {formatFileSize(viewDocument.file_size)}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Statut
                  </Typography>
                  <Chip
                    label={getProcessingStatusLabel(viewDocument.processing_status)}
                    size="small"
                    sx={{
                      bgcolor: getProcessingStatusColor(viewDocument.processing_status),
                      color: 'white',
                      fontWeight: 500,
                    }}
                  />
                </Box>

                {viewDocument.patient_id && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Patient
                    </Typography>
                    <Typography variant="body2" fontWeight={500} sx={{ fontFamily: 'monospace' }}>
                      {viewDocument.patient_id}
                    </Typography>
                  </Box>
                )}

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Date d'upload
                  </Typography>
                  <Typography variant="body2" fontWeight={500}>
                    {formatDate(viewDocument.created_at)}
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    Anonymisation
                  </Typography>
                  <Chip
                    label={viewDocument.is_anonymized ? 'Anonymisé' : 'En attente'}
                    size="small"
                    color={viewDocument.is_anonymized ? 'success' : 'warning'}
                    variant="outlined"
                  />
                </Box>
              </Box>

              {!viewDocument.is_anonymized && (
                <Alert severity="info" sx={{ mt: 3 }}>
                  Ce document sera automatiquement anonymisé lors du traitement pour protéger les données sensibles.
                </Alert>
              )}
              
              <Alert severity="warning" sx={{ mt: 2 }}>
                <strong>Note:</strong> Le téléchargement du fichier original n'est disponible que pour les documents récemment uploadés. Le contenu textuel est conservé dans la base de données pour la recherche et l'analyse IA.
              </Alert>
            </Box>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2 }}>
          <Button onClick={() => {
            setViewDialogOpen(false);
            setViewDocument(null);
          }}>
            Fermer
          </Button>
          <Button
            onClick={() => {
              if (viewDocument) {
                // Try to download
                const link = document.createElement('a');
                link.href = `http://localhost:8000/api/v1/documents/${viewDocument.id}/download`;
                link.download = viewDocument.filename;
                link.target = '_blank';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
              }
            }}
            variant="outlined"
            startIcon={<DownloadIcon />}
          >
            Télécharger (si disponible)
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Confirmer la suppression</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir supprimer le document "{selectedDocument?.filename}" ?
            Cette action est irréversible.
          </Typography>
          {selectedDocument?.processing_status === 'indexed' && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              Ce document a déjà été traité. Sa suppression entraînera la perte de toutes les données d'indexation associées.
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Annuler</Button>
          <Button
            onClick={confirmDelete}
            color="error"
            variant="contained"
            disabled={deleteMutation.isPending}
          >
            {deleteMutation.isPending ? 'Suppression...' : 'Supprimer'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Documents;