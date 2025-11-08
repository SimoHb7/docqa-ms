import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Description as DocumentsIcon,
  Upload as UploadIcon,
  Search as SearchIcon,
  Chat as ChatIcon,
  Assessment as SynthesisIcon,
  Security as AuditIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppStore } from '../../store';

const drawerWidth = 280;

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAppStore();

  const menuItems = [
    {
      text: 'Tableau de bord',
      icon: <DashboardIcon />,
      path: '/dashboard',
      roles: ['admin', 'doctor', 'researcher', 'quality_manager'],
    },
    {
      text: 'Documents',
      icon: <DocumentsIcon />,
      path: '/documents',
      roles: ['admin', 'doctor', 'researcher', 'quality_manager'],
    },
    {
      text: 'Téléchargement',
      icon: <UploadIcon />,
      path: '/upload',
      roles: ['admin', 'doctor'],
    },
    {
      text: 'Recherche',
      icon: <SearchIcon />,
      path: '/search',
      roles: ['admin', 'doctor', 'researcher', 'quality_manager'],
    },
    {
      text: 'Q&R Médical',
      icon: <ChatIcon />,
      path: '/qa',
      roles: ['admin', 'doctor', 'researcher', 'quality_manager'],
    },
    {
      text: 'Synthèse',
      icon: <SynthesisIcon />,
      path: '/synthesis',
      roles: ['admin', 'doctor', 'researcher'],
    },
    {
      text: 'Audit',
      icon: <AuditIcon />,
      path: '/audit',
      roles: ['admin', 'quality_manager'],
    },
    {
      text: 'Paramètres',
      icon: <SettingsIcon />,
      path: '/settings',
      roles: ['admin', 'doctor', 'researcher', 'quality_manager'],
    },
  ];

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const filteredMenuItems = menuItems.filter(item =>
    user?.role && item.roles.includes(user.role)
  );

  const drawerContent = (
    <Box sx={{ width: drawerWidth, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Logo/Brand */}
      <Box sx={{ p: 3, borderBottom: `1px solid ${theme.palette.divider}` }}>
        <Typography variant="h6" component="div" sx={{ fontWeight: 700, color: 'primary.main' }}>
          InterfaceClinique
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Système Q&R Médical
        </Typography>
      </Box>

      {/* Navigation Menu */}
      <List sx={{ flex: 1, pt: 2 }}>
        {filteredMenuItems.map((item) => {
          const isActive = location.pathname === item.path;

          return (
            <ListItem key={item.path} disablePadding>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                selected={isActive}
                sx={{
                  mx: 1,
                  mb: 0.5,
                  borderRadius: 2,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    },
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: isActive ? 'primary.contrastText' : 'text.secondary',
                    minWidth: 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.95rem',
                    fontWeight: isActive ? 600 : 400,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider />

      {/* User Info */}
      <Box sx={{ p: 2 }}>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Connecté en tant que :
        </Typography>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {user?.name || 'Utilisateur'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {user?.role === 'admin' && 'Administrateur'}
          {user?.role === 'doctor' && 'Médecin'}
          {user?.role === 'researcher' && 'Chercheur'}
          {user?.role === 'quality_manager' && 'Responsable Qualité'}
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'permanent'}
      open={isMobile ? open : true}
      onClose={onClose}
      ModalProps={{
        keepMounted: true, // Better open performance on mobile
      }}
      sx={{
        width: isMobile ? 0 : drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          borderRight: `1px solid ${theme.palette.divider}`,
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar;