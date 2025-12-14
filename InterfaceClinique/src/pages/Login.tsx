import React, { useState } from 'react';
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

  const handleGoogleLogin = () => {
    setIsSubmitting(true);
    loginWithRedirect({
      authorizationParams: {
        connection: 'google-oauth2',
      },
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
        bgcolor: 'background.default',
        overflow: 'hidden',
      }}
    >
      {/* Left Side - Branding (Hidden on Mobile) */}
      {!isMobile && (
        <Box
          sx={{
            flex: 1,
            background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            p: 4,
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
              opacity: 0.1,
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='80' height='80' viewBox='0 0 80 80' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M0 0h40v40H0V0zm40 40h40v40H40V40z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}
          />

          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ duration: 0.8, type: 'spring' }}
          >
            <Box
              sx={{
                width: 100,
                height: 100,
                borderRadius: '50%',
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(10px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mb: 3,
                boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
              }}
            >
              <MedicalIcon sx={{ fontSize: 50, color: 'white' }} />
            </Box>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
          >
            <Typography
              variant="h4"
              component="h1"
              gutterBottom
              fontWeight={700}
              sx={{ color: 'white', textAlign: 'center', mb: 1.5 }}
            >
              DocQA
            </Typography>
            <Typography
              variant="body1"
              sx={{ color: 'rgba(255,255,255,0.9)', textAlign: 'center', mb: 3, maxWidth: 450, fontSize: '1rem' }}
            >
              Plateforme intelligente de gestion et d'analyse de documents médicaux
            </Typography>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6, duration: 0.6 }}
          >
            <Box sx={{ display: 'flex', gap: 3, mt: 4 }}>
              <Box sx={{ textAlign: 'center' }}>
                <LocalHospital sx={{ fontSize: 36, color: 'rgba(255,255,255,0.9)', mb: 0.5 }} />
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.75rem' }}>
                  Documents Sécurisés
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Shield sx={{ fontSize: 36, color: 'rgba(255,255,255,0.9)', mb: 0.5 }} />
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.75rem' }}>
                  Authentification
                </Typography>
              </Box>
              <Box sx={{ textAlign: 'center' }}>
                <Timeline sx={{ fontSize: 36, color: 'rgba(255,255,255,0.9)', mb: 0.5 }} />
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.8)', fontSize: '0.75rem' }}>
                  Analyse IA
                </Typography>
              </Box>
            </Box>
          </motion.div>
        </Box>
      )}

      {/* Right Side - Login Form */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: { xs: 2, sm: 3, md: 4 },
          bgcolor: 'background.default',
          minHeight: { xs: '100vh', md: 'auto' },
        }}
      >
        <Box sx={{ width: '100%', maxWidth: 480 }}>
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Mobile Logo (Only on Mobile) */}
            {isMobile && (
              <Box textAlign="center" mb={3}>
                <Box
                  sx={{
                    width: 60,
                    height: 60,
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mx: 'auto',
                    mb: 2,
                  }}
                >
                  <MedicalIcon sx={{ fontSize: 30, color: 'white' }} />
                </Box>
                <Typography variant="h6" fontWeight={700} sx={{ 
                  background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}>
                  DocQA
                </Typography>
              </Box>
            )}

            {/* Welcome Text */}
            <Box mb={3}>
              <Typography variant="h5" fontWeight={700} gutterBottom color="text.primary">
                Bienvenue
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Connectez-vous pour accéder à votre espace
              </Typography>
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

            {/* Social Login Buttons */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
            >
              {/* Google Login Button */}
              <Button
                fullWidth
                variant="contained"
                size="large"
                onClick={handleGoogleLogin}
                disabled={isSubmitting}
                sx={{
                  py: 1.5,
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  background: '#fff',
                  color: '#3c4043',
                  border: '1.5px solid #dadce0',
                  boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
                  textTransform: 'none',
                  '&:hover': {
                    background: '#f8f9fa',
                    border: '1.5px solid #d0d0d0',
                    boxShadow: '0 2px 6px rgba(0,0,0,0.12)',
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                {isSubmitting ? (
                  <CircularProgress size={24} sx={{ color: '#1976d2' }} />
                ) : (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                    <svg width="20" height="20" viewBox="0 0 48 48">
                      <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                      <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                      <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
                      <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
                    </svg>
                    <span>Continuer avec Google</span>
                  </Box>
                )}
              </Button>

              {/* Auth0 Other Methods Button */}
              <Button
                fullWidth
                variant="outlined"
                size="large"
                onClick={handleAuth0Login}
                disabled={isSubmitting}
                sx={{
                  mt: 1.5,
                  py: 1.5,
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  borderColor: theme.palette.divider,
                  color: 'text.primary',
                  textTransform: 'none',
                  '&:hover': {
                    borderColor: theme.palette.primary.main,
                    background: `${theme.palette.primary.main}05`,
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                <Shield sx={{ mr: 1.5, fontSize: 20 }} />
                Autres méthodes de connexion
              </Button>
            </motion.div>

            {/* Divider */}
            <Box sx={{ display: 'flex', alignItems: 'center', my: 2.5 }}>
              <Divider sx={{ flex: 1 }} />
              <Typography variant="body2" color="text.secondary" sx={{ px: 2, fontWeight: 500, fontSize: '0.85rem' }}>
                ou avec email
              </Typography>
              <Divider sx={{ flex: 1 }} />
            </Box>

            {/* Email/Password Form */}
            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Adresse email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                margin="dense"
                autoComplete="email"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Email sx={{ color: 'text.secondary', fontSize: 20 }} />
                    </InputAdornment>
                  ),
                }}
                sx={{
                  mb: 2,
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    '&:hover .MuiOutlinedInput-notchedOutline': {
                      borderColor: 'primary.main',
                    },
                  },
                }}
              />

              <TextField
                fullWidth
                label="Mot de passe"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="dense"
                autoComplete="current-password"
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock sx={{ color: 'text.secondary', fontSize: 20 }} />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={togglePasswordVisibility}
                        edge="end"
                        size="small"
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

              <Box sx={{ textAlign: 'right', mt: 0.5, mb: 2 }}>
                <Link
                  href="#"
                  variant="body2"
                  color="primary"
                  underline="hover"
                  sx={{ fontWeight: 500, fontSize: '0.8rem' }}
                >
                  Mot de passe oublié ?
                </Link>
              </Box>

              <Button
                type="submit"
                fullWidth
                variant="contained"
                size="large"
                disabled={isSubmitting}
                sx={{
                  py: 1.5,
                  fontSize: '0.95rem',
                  fontWeight: 600,
                  borderRadius: 2,
                  textTransform: 'none',
                  boxShadow: `0 3px 10px ${theme.palette.primary.main}40`,
                  '&:hover': {
                    boxShadow: `0 4px 15px ${theme.palette.primary.main}50`,
                  },
                  transition: 'all 0.2s ease',
                }}
              >
                {isSubmitting ? <CircularProgress size={24} color="inherit" /> : 'Se connecter'}
              </Button>
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
                {/* <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  Nouveau sur DocQA ?{' '}
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
                </Typography> */}
              </Box>
            </motion.div>

            {/* Footer */}
            <Box textAlign="center" mt={3}>
              <Typography variant="body2" color="text.secondary">
                Nouveau sur DocQA ?{' '}
                <Link
                  href="#"
                  color="primary"
                  underline="hover"
                  sx={{ fontWeight: 600 }}
                >
                  Créer un compte
                </Link>
              </Typography>
              
              <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="caption" color="text.secondary" display="block" mb={1}>
                  © 2025 DocQA. Tous droits réservés.
                </Typography>
              </Box>
            </Box>
          </motion.div>
        </Box>
      </Box>
    </Box>
  );
};

export default Login;