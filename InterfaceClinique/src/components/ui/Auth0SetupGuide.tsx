import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
} from '@mui/material';
import {
  CheckCircle,
  RadioButtonUnchecked,
  Launch,
  Security,
  Settings,
  Code,
} from '@mui/icons-material';

interface Auth0SetupGuideProps {
  onComplete?: () => void;
}

const Auth0SetupGuide: React.FC<Auth0SetupGuideProps> = () => {
  const [completedSteps, setCompletedSteps] = React.useState<Set<number>>(new Set());

  const steps = [
    {
      title: "Créer un compte Auth0",
      description: "Rendez-vous sur auth0.com et créez un compte gratuit",
      action: "https://auth0.com",
      icon: <Launch />,
    },
    {
      title: "Créer une application",
      description: "Dans le dashboard Auth0, créez une 'Single Page Application'",
      details: [
        "Nom: DocQA",
        "Type: Single Page Application",
      ],
    },
    {
      title: "Configurer les URLs",
      description: "Définissez les URLs de callback et de logout",
      details: [
        "Allowed Callback URLs: http://localhost:3000",
        "Allowed Logout URLs: http://localhost:3000",
        "Allowed Web Origins: http://localhost:3000",
      ],
    },
    {
      title: "Activer les flux d'authentification",
      description: "Activez les types de connexion nécessaires",
      details: [
        "Authorization Code: ✅ Activé",
        "Implicit: ✅ Activé",
        "Refresh Token: ✅ Activé",
      ],
    },
    {
      title: "Récupérer les clés",
      description: "Copiez le Domain et Client ID depuis les paramètres",
      details: [
        "Domain: votre-app.auth0.com",
        "Client ID: votre-client-id",
      ],
    },
    {
      title: "Mettre à jour la configuration",
      description: "Modifiez le fichier .env avec vos clés Auth0",
      code: `VITE_AUTH0_DOMAIN=votre-domain.auth0.com
VITE_AUTH0_CLIENT_ID=votre-client-id
VITE_AUTH0_AUDIENCE=https://api.interfaceclinique.com`,
    },
  ];

  const handleStepComplete = (stepIndex: number) => {
    const newCompleted = new Set(completedSteps);
    if (newCompleted.has(stepIndex)) {
      newCompleted.delete(stepIndex);
    } else {
      newCompleted.add(stepIndex);
    }
    setCompletedSteps(newCompleted);
  };

  const allStepsCompleted = completedSteps.size === steps.length;

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Paper sx={{ p: 4, borderRadius: 3 }}>
        <Box textAlign="center" mb={4}>
          <Security sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" gutterBottom fontWeight={600}>
            Configuration Auth0
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Suivez ces étapes pour configurer l'authentification Auth0 pour DocQA
          </Typography>
        </Box>

        <Alert severity="info" sx={{ mb: 4 }}>
          <Typography variant="body2">
            <strong>Pourquoi Auth0 ?</strong> Auth0 fournit une authentification sécurisée,
            des autorisations basées sur les rôles, et une gestion des utilisateurs pour les applications médicales.
          </Typography>
        </Alert>

        <List sx={{ mb: 4 }}>
          {steps.map((step, index) => (
            <React.Fragment key={index}>
              <ListItem
                sx={{
                  alignItems: 'flex-start',
                  py: 3,
                  cursor: 'pointer',
                  '&:hover': { bgcolor: 'action.hover' },
                }}
                onClick={() => handleStepComplete(index)}
              >
                <ListItemIcon sx={{ mt: 0.5 }}>
                  {completedSteps.has(index) ? (
                    <CheckCircle color="success" />
                  ) : (
                    <RadioButtonUnchecked color="action" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="h6" fontWeight={500}>
                        {index + 1}. {step.title}
                      </Typography>
                      {completedSteps.has(index) && (
                        <Chip label="Terminé" color="success" size="small" />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {step.description}
                      </Typography>

                      {step.action && (
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<Launch />}
                          href={step.action}
                          target="_blank"
                          sx={{ mr: 1, mb: 1 }}
                        >
                          Ouvrir Auth0
                        </Button>
                      )}

                      {step.details && (
                        <Box component="ul" sx={{ pl: 2, mt: 1 }}>
                          {step.details.map((detail, detailIndex) => (
                            <Typography
                              key={detailIndex}
                              component="li"
                              variant="body2"
                              color="text.secondary"
                              sx={{ mb: 0.5 }}
                            >
                              {detail}
                            </Typography>
                          ))}
                        </Box>
                      )}

                      {step.code && (
                        <Box
                          component="pre"
                          sx={{
                            bgcolor: 'grey.100',
                            p: 2,
                            borderRadius: 1,
                            fontSize: '0.8rem',
                            overflow: 'auto',
                            mt: 1,
                          }}
                        >
                          {step.code}
                        </Box>
                      )}
                    </Box>
                  }
                />
              </ListItem>
              {index < steps.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>

        <Box textAlign="center">
          <Typography variant="h6" gutterBottom color="primary">
            Progrès: {completedSteps.size}/{steps.length} étapes terminées
          </Typography>

          {allStepsCompleted && (
            <Alert severity="success" sx={{ mb: 3 }}>
              <Typography variant="body2">
                🎉 Configuration Auth0 terminée ! Vous pouvez maintenant tester l'authentification.
              </Typography>
            </Alert>
          )}

          <Box display="flex" gap={2} justifyContent="center">
            <Button
              variant="outlined"
              startIcon={<Settings />}
              onClick={() => window.open('https://manage.auth0.com', '_blank')}
            >
              Ouvrir Dashboard Auth0
            </Button>

            <Button
              variant="contained"
              startIcon={<Code />}
              onClick={() => window.location.reload()}
              disabled={!allStepsCompleted}
            >
              Tester la connexion
            </Button>
          </Box>
        </Box>

        <Box mt={4} p={2} bgcolor="grey.50" borderRadius={2}>
          <Typography variant="h6" gutterBottom color="primary">
            📋 Checklist rapide
          </Typography>
          <Box component="ul" sx={{ pl: 2 }}>
            <li>✅ Compte Auth0 créé</li>
            <li>✅ Application SPA configurée</li>
            <li>✅ URLs de callback définies</li>
            <li>✅ Domain et Client ID copiés</li>
            <li>✅ Variables d'environnement mises à jour</li>
            <li>✅ Application redémarrée</li>
          </Box>
        </Box>

        <Box mt={3} p={2} bgcolor="info.50" borderRadius={2}>
          <Typography variant="body2" color="info.main">
            <strong>💡 Conseil:</strong> Pour un environnement de production, configurez également
            des règles d'autorisation et des connexions sociales dans Auth0.
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default Auth0SetupGuide;