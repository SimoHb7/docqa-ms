import { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Grid,
  Typography,
  Button,
  Chip,
  TextField,
  InputAdornment,
  IconButton,
  Menu,
  MenuItem,

  alpha,
  useTheme,
  Tab,
  Tabs,
} from '@mui/material';
import {
  CloudUpload,
  Search,
  FilterList,
  GridView,
  ViewList,
  MoreVert,
  Download,
  Delete,
  Visibility,
  Description,
  PictureAsPdf,
  Article,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

interface Document {
  id: number;
  name: string;
  type: string;
  size: string;
  uploadedAt: string;
  status: 'processed' | 'processing' | 'failed';
  tags: string[];
  uploadedBy: string;
}

const mockDocuments: Document[] = [
  {
    id: 1,
    name: 'Rapport_Medical_Patient_001.pdf',
    type: 'PDF',
    size: '2.4 MB',
    uploadedAt: '2025-10-28 14:30',
    status: 'processed',
    tags: ['Cardiologie', 'Urgent'],
    uploadedBy: 'Dr. Martin',
  },
  {
    id: 2,
    name: 'Analyse_Biologique_Complete.pdf',
    type: 'PDF',
    size: '1.8 MB',
    uploadedAt: '2025-10-28 12:15',
    status: 'processed',
    tags: ['Laboratoire'],
    uploadedBy: 'Dr. Dubois',
  },
  {
    id: 3,
    name: 'IRM_Cerebrale_Jean_Dupont.pdf',
    type: 'PDF',
    size: '15.2 MB',
    uploadedAt: '2025-10-28 10:45',
    status: 'processing',
    tags: ['Imagerie', 'Neurologie'],
    uploadedBy: 'Dr. Bernard',
  },
  {
    id: 4,
    name: 'Ordonnance_Traitement.docx',
    type: 'DOCX',
    size: '0.5 MB',
    uploadedAt: '2025-10-27 16:20',
    status: 'processed',
    tags: ['Prescription'],
    uploadedBy: 'Dr. Martin',
  },
  {
    id: 5,
    name: 'Compte_Rendu_Chirurgie.pdf',
    type: 'PDF',
    size: '3.1 MB',
    uploadedAt: '2025-10-27 09:00',
    status: 'processed',
    tags: ['Chirurgie', 'Orthopédie'],
    uploadedBy: 'Dr. Leclerc',
  },
  {
    id: 6,
    name: 'ECG_Patient_M.pdf',
    type: 'PDF',
    size: '0.8 MB',
    uploadedAt: '2025-10-26 14:00',
    status: 'processed',
    tags: ['Cardiologie'],
    uploadedBy: 'Dr. Martin',
  },
];

function DocumentCard({ document, onMenuClick }: { document: Document; onMenuClick: (event: React.MouseEvent<HTMLElement>, doc: Document) => void }) {
  const theme = useTheme();

  const getFileIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'pdf':
        return <PictureAsPdf sx={{ fontSize: 40, color: '#d32f2f' }} />;
      case 'docx':
        return <Article sx={{ fontSize: 40, color: '#1976d2' }} />;
      default:
        return <Description sx={{ fontSize: 40, color: '#757575' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'processed':
        return 'success';
      case 'processing':
        return 'warning';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'processed':
        return 'Traité';
      case 'processing':
        return 'En cours';
      case 'failed':
        return 'Échec';
      default:
        return status;
    }
  };

  return (
    <Card
      sx={{
        height: '100%',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 12px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box
            sx={{
              width: 56,
              height: 56,
              borderRadius: 2,
              bgcolor: alpha(theme.palette.primary.main, 0.08),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {getFileIcon(document.type)}
          </Box>
          <IconButton size="small" onClick={(e) => onMenuClick(e, document)}>
            <MoreVert />
          </IconButton>
        </Box>

        <Typography variant="subtitle1" fontWeight={600} noWrap gutterBottom>
          {document.name}
        </Typography>

        <Box sx={{ display: 'flex', gap: 0.5, mb: 2, flexWrap: 'wrap' }}>
          {document.tags.map((tag) => (
            <Chip key={tag} label={tag} size="small" sx={{ height: 20, fontSize: '0.7rem' }} />
          ))}
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="caption" color="text.secondary">
            {document.size} • {document.type}
          </Typography>
          <Chip label={getStatusLabel(document.status)} color={getStatusColor(document.status)} size="small" />
        </Box>

        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
          {document.uploadedAt}
        </Typography>

        <Typography variant="caption" color="text.secondary">
          Par {document.uploadedBy}
        </Typography>
      </CardContent>
    </Card>
  );
}

export default function ModernDocuments() {
  const theme = useTheme();
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [tabValue, setTabValue] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);


  const handleMenuClick = (event: React.MouseEvent<HTMLElement>, doc: Document) => {
    setAnchorEl(event.currentTarget);
    setSelectedDoc(doc);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedDoc(null);
  };

  const filteredDocuments = mockDocuments.filter((doc) => {
    if (tabValue === 1) return doc.status === 'processed';
    if (tabValue === 2) return doc.status === 'processing';
    if (searchQuery) {
      return doc.name.toLowerCase().includes(searchQuery.toLowerCase()) || doc.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    }
    return true;
  });

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Mes Documents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Gérez et consultez tous vos documents médicaux
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<CloudUpload />}
          size="large"
          onClick={() => navigate('/upload')}
          sx={{
            borderRadius: 3,
            px: 3,
            py: 1.5,
            textTransform: 'none',
            fontWeight: 600,
            boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.3)}`,
          }}
        >
          Importer un document
        </Button>
      </Box>

      {/* Filters and Search */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
            {/* Search */}
            <TextField
              placeholder="Rechercher des documents..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
              sx={{ flex: 1, minWidth: 250 }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Search />
                  </InputAdornment>
                ),
              }}
            />

            {/* View Mode Toggle */}
            <Box sx={{ display: 'flex', gap: 1 }}>
              <IconButton
                onClick={() => setViewMode('grid')}
                sx={{
                  bgcolor: viewMode === 'grid' ? 'primary.main' : 'transparent',
                  color: viewMode === 'grid' ? 'white' : 'text.secondary',
                  '&:hover': {
                    bgcolor: viewMode === 'grid' ? 'primary.dark' : alpha(theme.palette.primary.main, 0.08),
                  },
                }}
              >
                <GridView />
              </IconButton>
              <IconButton
                onClick={() => setViewMode('list')}
                sx={{
                  bgcolor: viewMode === 'list' ? 'primary.main' : 'transparent',
                  color: viewMode === 'list' ? 'white' : 'text.secondary',
                  '&:hover': {
                    bgcolor: viewMode === 'list' ? 'primary.dark' : alpha(theme.palette.primary.main, 0.08),
                  },
                }}
              >
                <ViewList />
              </IconButton>
            </Box>

            {/* Filter Button */}
            <Button variant="outlined" startIcon={<FilterList />} sx={{ borderRadius: 2 }}>
              Filtrer
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Box sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
          <Tab label={`Tous (${mockDocuments.length})`} />
          <Tab label={`Traités (${mockDocuments.filter((d) => d.status === 'processed').length})`} />
          <Tab label={`En cours (${mockDocuments.filter((d) => d.status === 'processing').length})`} />
        </Tabs>
      </Box>

      {/* Documents Grid */}
      <Grid container spacing={3}>
        {filteredDocuments.map((doc) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={doc.id}>
            <DocumentCard document={doc} onMenuClick={handleMenuClick} />
          </Grid>
        ))}
      </Grid>

      {/* Empty State */}
      {filteredDocuments.length === 0 && (
        <Box
          sx={{
            textAlign: 'center',
            py: 8,
          }}
        >
          <Description sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Aucun document trouvé
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Essayez de modifier vos filtres ou d'importer un nouveau document
          </Typography>
          <Button variant="contained" startIcon={<CloudUpload />} onClick={() => navigate('/upload')}>
            Importer un document
          </Button>
        </Box>
      )}

      {/* Context Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleMenuClose}>
          <Visibility fontSize="small" sx={{ mr: 1 }} />
          Aperçu
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <Download fontSize="small" sx={{ mr: 1 }} />
          Télécharger
        </MenuItem>
        <MenuItem onClick={handleMenuClose} sx={{ color: 'error.main' }}>
          <Delete fontSize="small" sx={{ mr: 1 }} />
          Supprimer
        </MenuItem>
      </Menu>
    </Box>
  );
}
