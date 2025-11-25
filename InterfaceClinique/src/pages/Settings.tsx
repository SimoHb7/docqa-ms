import React, { useState } from 'react';
import {
  Box,
  Typography,

  CardContent,
  Switch,
  FormControlLabel,
  Button,
  Divider,
  Avatar,

  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Person as PersonIcon,
  Notifications as NotificationsIcon,
  Security as SecurityIcon,
  Palette as PaletteIcon,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useAuth0 } from '@auth0/auth0-react';
import { useAppStore } from '../store';
import ButtonComponent from '../components/ui/Button';
import CardComponent from '../components/ui/Card';

const Settings: React.FC = () => {
  const { user, logout } = useAuth0();
  const {
    theme,
    setTheme,
    sidebarOpen,
    setSidebarOpen,
    notifications,
    clearNotifications,
  } = useAppStore();

  const [confirmLogout, setConfirmLogout] = useState(false);

  const handleThemeChange = (newTheme: 'light' | 'dark' | 'system') => {
    setTheme(newTheme);
  };

  const handleLogout = () => {
    logout({ logoutParams: { returnTo: window.location.origin } });
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom fontWeight={700}>
        Paramètres
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Gérez vos préférences et paramètres de compte
      </Typography>

      <Box display="flex" flexDirection="column" gap={3}>
        {/* Profile Section */}
        <CardComponent title="Profil utilisateur" icon={<PersonIcon />}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={3} mb={3}>
              <Avatar
                src={user?.picture}
                alt={user?.name || 'User'}
                sx={{ width: 80, height: 80 }}
              >
                {user?.name?.charAt(0)?.toUpperCase()}
              </Avatar>
              <Box>
                <Typography variant="h6">{user?.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {user?.email}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {user?.role === 'admin' && 'Administrateur'}
                  {user?.role === 'doctor' && 'Médecin'}
                  {user?.role === 'researcher' && 'Chercheur'}
                  {user?.role === 'quality_manager' && 'Responsable Qualité'}
                </Typography>
              </Box>
            </Box>
          </CardContent>
        </CardComponent>

        {/* Appearance Section */}
        <CardComponent title="Apparence" icon={<PaletteIcon />}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Thème
            </Typography>
            <Box display="flex" gap={2} mb={2}>
              <ButtonComponent
                variant={theme === 'light' ? 'contained' : 'outlined'}
                onClick={() => handleThemeChange('light')}
              >
                Clair
              </ButtonComponent>
              <ButtonComponent
                variant={theme === 'dark' ? 'contained' : 'outlined'}
                onClick={() => handleThemeChange('dark')}
              >
                Sombre
              </ButtonComponent>
              <ButtonComponent
                variant={theme === 'system' ? 'contained' : 'outlined'}
                onClick={() => handleThemeChange('system')}
              >
                Système
              </ButtonComponent>
            </Box>

            <Divider sx={{ my: 3 }} />

            <FormControlLabel
              control={
                <Switch
                  checked={sidebarOpen}
                  onChange={(e) => setSidebarOpen(e.target.checked)}
                />
              }
              label="Barre latérale ouverte par défaut"
            />
          </CardContent>
        </CardComponent>

        {/* Notifications Section */}
        <CardComponent title="Notifications" icon={<NotificationsIcon />}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Box>
                <Typography variant="h6">Notifications</Typography>
                <Typography variant="body2" color="text.secondary">
                  {unreadCount} notification{unreadCount !== 1 ? 's' : ''} non lue{unreadCount !== 1 ? 's' : ''}
                </Typography>
              </Box>
              {notifications.length > 0 && (
                <ButtonComponent
                  variant="outlined"
                  size="small"
                  onClick={clearNotifications}
                >
                  Tout effacer
                </ButtonComponent>
              )}
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              Les notifications incluent les mises à jour de traitement des documents,
              les rappels de sécurité, et les alertes système importantes.
            </Alert>
          </CardContent>
        </CardComponent>

        {/* Security Section */}
        <CardComponent title="Sécurité" icon={<SecurityIcon />}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Session active
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Vous êtes connecté avec Auth0. Votre session est automatiquement gérée et sécurisée.
            </Typography>

            <Alert severity="success" sx={{ mb: 3 }}>
              ✅ Authentification multi-facteurs activée
            </Alert>

            <ButtonComponent
              variant="outlined"
              color="error"
              startIcon={<LogoutIcon />}
              onClick={() => setConfirmLogout(true)}
            >
              Se déconnecter
            </ButtonComponent>
          </CardContent>
        </CardComponent>

        {/* System Information */}
        <CardComponent title="Informations système">
          <CardContent>
            <Box display="flex" flexDirection="column" gap={1}>
              <Typography variant="body2">
                <strong>Version:</strong> InterfaceClinique v1.0.0
              </Typography>
              <Typography variant="body2">
                <strong>Backend:</strong> DocQA-MS API Gateway
              </Typography>
              <Typography variant="body2">
                <strong>Navigateur:</strong> {navigator.userAgent.split(' ').pop()}
              </Typography>
              <Typography variant="body2">
                <strong>Dernière connexion:</strong> {new Date().toLocaleString('fr-FR')}
              </Typography>
            </Box>
          </CardContent>
        </CardComponent>
      </Box>

      {/* Logout Confirmation Dialog */}
      <Dialog
        open={confirmLogout}
        onClose={() => setConfirmLogout(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Confirmer la déconnexion</DialogTitle>
        <DialogContent>
          <Typography>
            Êtes-vous sûr de vouloir vous déconnecter ? Vous devrez vous reconnecter pour accéder à nouveau à l'application.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmLogout(false)}>Annuler</Button>
          <Button onClick={handleLogout} color="error" variant="contained">
            Se déconnecter
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;