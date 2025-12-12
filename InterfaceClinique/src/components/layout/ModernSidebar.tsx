import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography, Avatar, Divider, useTheme, alpha, IconButton } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import {
  Dashboard as DashboardIcon,
  Description as DocumentsIcon,
  CloudUpload as UploadIcon,
  Chat as ChatIcon,
  Assessment as AnalyticsIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  LocalHospital as HospitalIcon,
  Close as CloseIcon,
  AutoAwesome as MLIcon,
} from '@mui/icons-material';

interface ModernSidebarProps {
  open: boolean;
  onClose: () => void;
  isMobile: boolean;
}

const menuItems = [
  { title: 'Tableau de bord', path: '/dashboard', icon: <DashboardIcon /> },
  { title: 'Documents', path: '/documents', icon: <DocumentsIcon /> },
  { title: 'Importer', path: '/upload', icon: <UploadIcon /> },
  { title: 'Q&A Chat', path: '/qa', icon: <ChatIcon /> },
  { title: 'Analyses', path: '/synthesis', icon: <AnalyticsIcon /> },
  { title: 'ML Analytics', path: '/ml-analytics', icon: <MLIcon /> },
  { title: 'Paramètres', path: '/settings', icon: <SettingsIcon /> },
];

export default function ModernSidebar({ open, onClose, isMobile }: ModernSidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { user, logout } = useAuth0();

  const handleNavigation = (path: string) => {
    navigate(path);
    if (isMobile) {
      onClose();
    }
  };

  const handleLogout = () => {
    logout({ logoutParams: { returnTo: window.location.origin } });
  };

  const drawerWidth = 280;

  const sidebarContent = (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'background.paper',
        borderRight: `1px solid ${theme.palette.divider}`,
      }}
    >
      {/* Logo & Close Button */}
      <Box
        sx={{
          p: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              bgcolor: 'primary.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <HospitalIcon sx={{ color: 'white', fontSize: 24 }} />
          </Box>
          <Typography variant="h6" fontWeight={700} color="primary">
            InterfaceClinique
          </Typography>
        </Box>
        {isMobile && (
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        )}
      </Box>

      <Divider />

      {/* User Profile */}
      <Box sx={{ p: 3 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            p: 2,
            borderRadius: 3,
            bgcolor: alpha(theme.palette.primary.main, 0.08),
            border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
            transition: 'all 0.2s',
            '&:hover': {
              bgcolor: alpha(theme.palette.primary.main, 0.12),
              transform: 'translateY(-2px)',
            },
          }}
        >
          <Avatar
            src={user?.picture}
            alt={user?.name}
            sx={{
              width: 48,
              height: 48,
              border: `2px solid ${theme.palette.primary.main}`,
            }}
          >
            {user?.name?.charAt(0)}
          </Avatar>
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="subtitle2"
              fontWeight={600}
              noWrap
              sx={{ overflow: 'hidden', textOverflow: 'ellipsis' }}
            >
              {user?.name || user?.email}
            </Typography>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'normal',
                wordBreak: 'break-word',
                fontSize: '0.72rem',
              }}
            >
              {user?.email}
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Navigation Menu */}
      <List sx={{ flex: 1, px: 2 }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.path} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigation(item.path)}
                sx={{
                  borderRadius: 3,
                  py: 1.5,
                  px: 2.5,
                  ...(isActive && {
                    bgcolor: 'primary.main',
                    color: 'white',
                    boxShadow: `0 4px 12px ${alpha(theme.palette.primary.main, 0.4)}`,
                    '&:hover': {
                      bgcolor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'white',
                    },
                  }),
                  ...(!isActive && {
                    '&:hover': {
                      bgcolor: alpha(theme.palette.primary.main, 0.08),
                      transform: 'translateX(4px)',
                    },
                  }),
                  transition: 'all 0.2s',
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive ? 'white' : 'text.secondary',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.title}
                  primaryTypographyProps={{
                    fontSize: '0.95rem',
                    fontWeight: isActive ? 600 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider />

      {/* Logout Button */}
      <Box sx={{ p: 2 }}>
        <ListItemButton
          onClick={handleLogout}
          sx={{
            borderRadius: 2,
            py: 1.5,
            px: 2,
            color: 'error.main',
            '&:hover': {
              bgcolor: alpha(theme.palette.error.main, 0.08),
            },
          }}
        >
          <ListItemIcon sx={{ minWidth: 40, color: 'error.main' }}>
            <LogoutIcon />
          </ListItemIcon>
          <ListItemText
            primary="Déconnexion"
            primaryTypographyProps={{
              fontSize: '0.95rem',
              fontWeight: 500,
            }}
          />
        </ListItemButton>
      </Box>
    </Box>
  );

  return isMobile ? (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      ModalProps={{ keepMounted: true }}
      PaperProps={{
        sx: { width: drawerWidth },
      }}
    >
      {sidebarContent}
    </Drawer>
  ) : (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      PaperProps={{
        sx: {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      {sidebarContent}
    </Drawer>
  );
}
