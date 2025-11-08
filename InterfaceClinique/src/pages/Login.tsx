import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Link,
  Divider,
  useTheme,
  useMediaQuery,
  IconButton,
  InputAdornment,
  Fade,
  Grow,
  CircularProgress,
} from '@mui/material';
import {
  useAuth0
} from '@auth0/auth0-react';
import { Navigate } from 'react-router-dom';
import {
  MedicalServices as MedicalIcon,
  Visibility,
  VisibilityOff,
  Email,
  Lock,
  Shield,
  Settings,
  LocalHospital,
  Timeline,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import Auth0SetupGuide from '../components/ui/Auth0SetupGuide';

const Login: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const isTablet = useMediaQuery(theme.breakpoints.down('lg'));
  const { loginWithRedirect, isAuthenticated, isLoading, error } = useAuth0();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSetupGuide, setShowSetupGuide] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoginError('');
    setIsSubmitting(true);

    if (!email || !password) {
      setLoginError('Veuillez saisir votre email et mot de passe.');
      setIsSubmitting(false);
      return;
    }

    try {
      await loginWithRedirect({
        appState: {
          returnTo: '/dashboard',
        },
      });
    } catch (err) {
      setLoginError('Erreur de connexion. Veuillez réessayer.');
      setIsSubmitting(false);
    }
  };

  const handleAuth0Login = () => {
    setIsSubmitting(true);
    loginWithRedirect({
      appState: {
        returnTo: '/dashboard',
      },
    });
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Show setup guide if Auth0 is not configured
  const domain = import.meta.env.VITE_AUTH0_DOMAIN;
  const clientId = import.meta.env.VITE_AUTH0_CLIENT_ID;

  if (!domain || !clientId || domain === 'your-domain.auth0.com' || clientId === 'your-client-id') {
    return <Auth0SetupGuide onComplete={() => setShowSetupGuide(false)} />;
  }

  if (isLoading) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        bgcolor="background.default"
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main}15 0%, ${theme.palette.secondary.main}15 100%)`,
        }}
      >
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <MedicalIcon
            sx={{
              fontSize: 64,
              color: 'primary.main',
              mb: 2,
            }}
          />
        </motion.div>
        <CircularProgress size={40} sx={{ mb: 2 }} />
        <Typography variant="h6" color="text.secondary">
          Connexion en cours...
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
        p: { xs: 2, sm: 3 },
        background: `linear-gradient(135deg, ${theme.palette.primary.main}08 0%, ${theme.palette.secondary.main}08 100%)`,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background Pattern */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.03,
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23000000' fill-opacity='1'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
      />

      {/* Floating Icons */}
      <Box sx={{ position: 'absolute', top: '10%', right: '10%', opacity: 0.1 }}>
        <LocalHospital sx={{ fontSize: 48, color: 'primary.main' }} />
      </Box>
      <Box sx={{ position: 'absolute', bottom: '15%', left: '8%', opacity: 0.1 }}>
        <Shield sx={{ fontSize: 40, color: 'secondary.main' }} />
      </Box>
      <Box sx={{ position: 'absolute', top: '60%', right: '15%', opacity: 0.1 }}>
        <Timeline sx={{ fontSize: 36, color: 'success.main' }} />
      </Box>

      <Box
        sx={{
          width: '100%',
          maxWidth: isMobile ? 380 : 450,
          zIndex: 1,
        }}
      >
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <Paper
            elevation={isMobile ? 4 : 12}
            sx={{
              p: { xs: 3, sm: 4, md: 5 },
              borderRadius: isMobile ? 3 : 4,
              position: 'relative',
              overflow: 'hidden',
              background: `linear-gradient(145deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.paper}F0 100%)`,
              backdropFilter: 'blur(10px)',
              border: `1px solid ${theme.palette.divider}40`,
            }}
          >
            {/* Logo and Title */}
            <Box textAlign="center" mb={4}>
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, duration: 0.5 }}
              >
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.light})`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 3,
                    boxShadow: `0 8px 32px ${theme.palette.primary.main}30`,
                  }}
                >
                  <MedicalIcon sx={{ fontSize: 40, color: 'white' }} />
                </Box>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                <Typography
                  variant={isMobile ? "h5" : "h4"}
                  component="h1"
                  gutterBottom
                  fontWeight={700}
                  sx={{
                    background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  InterfaceClinique
                </Typography>
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ fontSize: isMobile ? '0.9rem' : '1rem' }}
                >
                  Système professionnel de Q&R sur documents médicaux
                </Typography>
              </motion.div>
            </Box>

            {/* Error Messages */}
            <Fade in={!!(error || loginError)} timeout={500}>
              <Alert
                severity="error"
                sx={{
                  mb: 3,
                  borderRadius: 2,
                  '& .MuiAlert-icon': {
                    color: 'error.main',
                  },
                }}
              >
                {error?.message || loginError}
              </Alert>
            </Fade>

            {/* Auth0 Login Button */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleAuth0Login}
                disabled={isSubmitting}
                sx={{
                  mb: 3,
                  py: isMobile ? 1.5 : 2,
                  fontSize: isMobile ? '1rem' : '1.1rem',
                  fontWeight: 600,
                  borderRadius: 3,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                  boxShadow: `0 4px 20px ${theme.palette.primary.main}40`,
                  '&:hover': {
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark}, ${theme.palette.primary.main})`,
                    boxShadow: `0 6px 25px ${theme.palette.primary.main}50`,
                    transform: 'translateY(-2px)',
                  },
                  transition: 'all 0.3s ease',
                }}
              >
                {isSubmitting ? (
                  <CircularProgress size={24} color="inherit" />
                ) : (
                  <>
                    <Shield sx={{ mr: 1, fontSize: 20 }} />
                    Se connecter avec Auth0
                  </>
                )}
              </Button>
            </motion.div>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5, duration: 0.5 }}
            >
              <Divider sx={{ mb: 3, '&::before, &::after': { borderColor: 'divider' } }}>
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{
                    px: 2,
                    backgroundColor: 'background.paper',
                    fontSize: '0.85rem',
                  }}
                >
                  ou continuer avec
                </Typography>
              </Divider>
            </motion.div>

            {/* Traditional Login Form */}
            <Box component="form" onSubmit={handleSubmit}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6, duration: 0.5 }}
              >
                <TextField
                  fullWidth
                  label="Adresse email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  margin="normal"
                  required
                  autoComplete="email"
                  autoFocus={!isMobile}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Email color="action" />
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'primary.main',
                      },
                    },
                  }}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7, duration: 0.5 }}
              >
                <TextField
                  fullWidth
                  label="Mot de passe"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  margin="normal"
                  required
                  autoComplete="current-password"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          aria-label="toggle password visibility"
                          onClick={togglePasswordVisibility}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                      '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'primary.main',
                      },
                    },
                  }}
                />
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8, duration: 0.5 }}
              >
                <Button
                  type="submit"
                  fullWidth
                  variant="outlined"
                  size="large"
                  disabled={isSubmitting}
                  sx={{
                    mt: 3,
                    mb: 2,
                    py: isMobile ? 1.5 : 2,
                    fontSize: isMobile ? '1rem' : '1.1rem',
                    fontWeight: 600,
                    borderRadius: 3,
                    borderWidth: 2,
                    '&:hover': {
                      borderWidth: 2,
                      backgroundColor: 'primary.main',
                      color: 'primary.contrastText',
                      transform: 'translateY(-1px)',
                      boxShadow: `0 4px 20px ${theme.palette.primary.main}30`,
                    },
                    transition: 'all 0.3s ease',
                  }}
                >
                  {isSubmitting ? (
                    <CircularProgress size={24} />
                  ) : (
                    'Se connecter'
                  )}
                </Button>
              </motion.div>
            </Box>

            {/* Footer Links */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.9, duration: 0.5 }}
            >
              <Box textAlign="center" mt={3}>
                <Typography variant="body2" color="text.secondary">
                  <Link
                    href="#"
                    color="primary"
                    underline="hover"
                    sx={{
                      fontWeight: 500,
                      '&:hover': {
                        color: 'primary.dark',
                      },
                    }}
                  >
                    Mot de passe oublié ?
                  </Link>
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Nouveau sur InterfaceClinique ?{' '}
                  <Link
                    href="#"
                    color="primary"
                    underline="hover"
                    sx={{
                      fontWeight: 500,
                      '&:hover': {
                        color: 'primary.dark',
                      },
                    }}
                  >
                    Créer un compte
                  </Link>
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                  <Button
                    variant="text"
                    size="small"
                    startIcon={<Settings />}
                    onClick={() => setShowSetupGuide(true)}
                    sx={{
                      fontSize: '0.8rem',
                      textTransform: 'none',
                      p: 0,
                      minHeight: 'auto',
                      '&:hover': {
                        backgroundColor: 'transparent',
                        textDecoration: 'underline',
                      },
                    }}
                  >
                    Configuration Auth0
                  </Button>
                </Typography>
              </Box>
            </motion.div>

            {/* Footer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1.0, duration: 0.5 }}
            >
              <Box
                textAlign="center"
                mt={4}
                pt={2}
                borderTop={1}
                borderColor="divider"
                sx={{ opacity: 0.7 }}
              >
                <Typography variant="caption" color="text.secondary">
                  © 2025 InterfaceClinique. Tous droits réservés.
                </Typography>
              </Box>
            </motion.div>
          </Paper>
        </motion.div>
      </Box>
    </Box>
  );
};

export default Login;