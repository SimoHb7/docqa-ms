import { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Error as ErrorIcon, Refresh as RefreshIcon } from '@mui/icons-material';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Here you could send the error to an error reporting service
    // logErrorToService(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="400px"
          p={3}
        >
          <Paper
            elevation={0}
            sx={{
              p: 4,
              textAlign: 'center',
              maxWidth: 500,
              border: '1px solid',
              borderColor: 'error.light',
            }}
          >
            <ErrorIcon color="error" sx={{ fontSize: 64, mb: 2 }} />
            <Typography variant="h5" color="error" gutterBottom>
              Une erreur inattendue s'est produite
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Nous nous excusons pour la gêne occasionnée. Veuillez réessayer ou contacter le support si le problème persiste.
            </Typography>

            <Box display="flex" gap={2} justifyContent="center">
              <Button
                variant="contained"
                color="primary"
                startIcon={<RefreshIcon />}
                onClick={this.handleRetry}
              >
                Réessayer
              </Button>
              <Button
                variant="outlined"
                onClick={() => window.location.reload()}
              >
                Actualiser la page
              </Button>
            </Box>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Box mt={3} textAlign="left">
                <Typography variant="h6" color="error" gutterBottom>
                  Détails de l'erreur (développement) :
                </Typography>
                <Typography
                  variant="body2"
                  component="pre"
                  sx={{
                    bgcolor: 'grey.100',
                    p: 2,
                    borderRadius: 1,
                    fontSize: '0.75rem',
                    overflow: 'auto',
                    maxHeight: 200,
                  }}
                >
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </Typography>
              </Box>
            )}
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;