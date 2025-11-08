import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Paper,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Autocomplete,
  IconButton,
  Tooltip,
  Badge,
  Fade,
  Slide,
  alpha,
  Snackbar,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  Description as DocumentIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
  Close as CloseIcon,
  Help as HelpIcon,
  Lightbulb as LightbulbIcon,
  TrendingUp as TrendingUpIcon,
} from '@mui/icons-material';
import { useMutation, useQuery } from '@tanstack/react-query';
import { qaApi, documentsApi } from '../services/api';
import { formatDate, getConfidenceColor, getConfidenceLabel } from '../utils';
import { ChatMessage, QARequest, QAResponse, Document } from '../types';
import ButtonComponent from '../components/ui/Button';
import { useAppStore } from '../store';

const QAChat: React.FC = () => {
  // Use Zustand store for persistent chat messages
  const currentChatSession = useAppStore((state) => state.currentChatSession);
  const setCurrentChatSession = useAppStore((state) => state.setCurrentChatSession);
  const chatMessages = useAppStore((state) => state.chatMessages);
  const addChatMessage = useAppStore((state) => state.addChatMessage);
  const clearChatSession = useAppStore((state) => state.clearChatSession);
  const selectedDocumentsStore = useAppStore((state) => state.selectedDocuments);
  const setSelectedDocumentsStore = useAppStore((state) => state.setSelectedDocuments);
  
  const [currentMessage, setCurrentMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDocumentError, setShowDocumentError] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session on mount if not exists
  useEffect(() => {
    if (!currentChatSession) {
      const newSessionId = crypto.randomUUID();
      setCurrentChatSession(newSessionId);
    }
  }, [currentChatSession, setCurrentChatSession]);

  // Get messages and selected documents for current session from store
  const messages = currentChatSession ? (chatMessages[currentChatSession] || []) : [];
  const selectedDocuments = currentChatSession ? (selectedDocumentsStore[currentChatSession] || []) : [];
  
  // Update selected documents in store
  const setSelectedDocuments = (docs: Document[]) => {
    if (currentChatSession) {
      setSelectedDocumentsStore(currentChatSession, docs);
    }
  };

  // Sample suggestions
  const suggestions = [
    "Quel est le diagnostic du patient ?",
    "Quels sont les résultats des analyses de laboratoire ?",
    "Quel traitement a été prescrit ?",
    "Y a-t-il des antécédents médicaux importants ?",
  ];

  // Fetch available documents
  const { data: documentsData, isLoading: isLoadingDocuments } = useQuery({
    queryKey: ['documents-list'],
    queryFn: () => documentsApi.list({ limit: 100 }),
    refetchInterval: 10000, // Refresh every 10 seconds to catch newly processed documents
  });

  const availableDocuments = documentsData?.data || [];

  // Send question mutation
  const askMutation = useMutation({
    mutationFn: (request: QARequest) => qaApi.ask(request),
    onSuccess: (data: QAResponse) => {
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: data.answer,
        timestamp: new Date().toISOString(),
        sources: data.sources.map(source => ({
          document_id: source.document_id,
          filename: source.filename || `Document ${source.document_id.slice(-8)}`,
          excerpt: source.content,
        })),
        confidence: data.confidence_score,
      };

      // Add message to store (persisted automatically)
      if (currentChatSession) {
        addChatMessage(currentChatSession, assistantMessage);
      }
      
      // Update session ID from server response if needed
      if (data.session_id && data.session_id !== currentChatSession) {
        setCurrentChatSession(data.session_id);
      }
    },
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (!currentMessage.trim()) return;
    if (!currentChatSession) return; // Ensure we have a session
    
    // Require document selection before sending message
    if (selectedDocuments.length === 0) {
      setShowDocumentError(true);
      return;
    }

    setShowSuggestions(false);
    setIsExpanded(true); // Expand to full screen when first message is sent

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: currentMessage,
      timestamp: new Date().toISOString(),
    };

    // Add user message to store
    addChatMessage(currentChatSession, userMessage);

    const request: QARequest = {
      question: currentMessage,
      session_id: currentChatSession,
      context_documents: selectedDocuments.map(doc => doc.id), // Always send selected documents
    };

    askMutation.mutate(request);
    setCurrentMessage('');
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    if (currentChatSession) {
      clearChatSession(currentChatSession);
    }
    // Create a new session for the next conversation
    const newSessionId = crypto.randomUUID();
    setCurrentChatSession(newSessionId);
    
    setShowSuggestions(true);
    setIsExpanded(false); // Return to compact mode
  };

  const handleSuggestionClick = (suggestion: string) => {
    setCurrentMessage(suggestion);
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <>
      {/* Backdrop overlay when expanded to cover everything behind */}
      {isExpanded && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            bgcolor: 'background.default',
            zIndex: 9998,
          }}
        />
      )}
      
      {/* Main Chat Container */}
      <Box sx={{ 
        height: isExpanded ? '100vh' : 'calc(100vh - 100px)', 
        width: isExpanded ? '100vw' : 'auto',
        display: 'flex', 
        flexDirection: 'column',
        background: isExpanded 
          ? 'background.default'
          : (theme) => `linear-gradient(135deg, ${alpha(theme.palette.primary.light, 0.05)} 0%, ${alpha(theme.palette.secondary.light, 0.05)} 100%)`,
        position: isExpanded ? 'fixed' : 'relative',
        top: isExpanded ? 0 : 'auto',
        left: isExpanded ? 0 : 'auto',
        right: isExpanded ? 0 : 'auto',
        bottom: isExpanded ? 0 : 'auto',
        zIndex: isExpanded ? 9999 : 'auto',
        p: isExpanded ? 2 : 0,
        transition: 'all 0.3s ease-in-out',
        overflow: 'hidden',
      }}>
      {/* Modern Header */}
      <Paper 
        elevation={isExpanded ? 4 : 0}
        sx={{ 
          p: isExpanded ? 1.5 : 2, 
          mb: isExpanded ? 1.5 : 1.5,
          background: (theme) => `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          borderRadius: isExpanded ? 2 : 2,
          flexShrink: 0,
        }}
      >
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box display="flex" alignItems="center" gap={isExpanded ? 1.5 : 1.5}>
            <Avatar 
              sx={{ 
                width: isExpanded ? 36 : 40, 
                height: isExpanded ? 36 : 40, 
                bgcolor: 'rgba(255,255,255,0.2)',
                backdropFilter: 'blur(10px)',
              }}
            >
              <PsychologyIcon sx={{ fontSize: isExpanded ? 20 : 24 }} />
            </Avatar>
            <Box>
              <Typography variant={isExpanded ? "subtitle1" : "h6"} component="h1" fontWeight={700} sx={{ mb: 0 }}>
                Assistant Médical IA
              </Typography>
              {!isExpanded && (
                <Typography variant="caption" sx={{ opacity: 0.9 }}>
                  Posez vos questions en langage naturel • Alimenté par l'IA
                </Typography>
              )}
            </Box>
          </Box>
          
          <Box display="flex" gap={1}>
            {messages.length > 0 && (
              <>
                <Tooltip title={isExpanded ? "Réduire" : "Agrandir"}>
                  <IconButton 
                    onClick={toggleExpanded}
                    size={isExpanded ? "small" : "medium"}
                    sx={{ 
                      bgcolor: 'rgba(255,255,255,0.2)', 
                      color: 'white',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                    }}
                  >
                    {isExpanded ? <CloseIcon fontSize="small" /> : <ExpandMoreIcon sx={{ transform: 'rotate(-90deg)' }} />}
                  </IconButton>
                </Tooltip>
                <Tooltip title="Nouvelle conversation">
                  <IconButton 
                    onClick={clearChat}
                    size={isExpanded ? "small" : "medium"}
                    sx={{ 
                      bgcolor: 'rgba(255,255,255,0.2)', 
                      color: 'white',
                      '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                    }}
                  >
                    <RefreshIcon fontSize={isExpanded ? "small" : "medium"} />
                  </IconButton>
                </Tooltip>
              </>
            )}
            {!isExpanded && (
              <Tooltip title="Aide">
                <IconButton 
                  sx={{ 
                    bgcolor: 'rgba(255,255,255,0.2)', 
                    color: 'white',
                    '&:hover': { bgcolor: 'rgba(255,255,255,0.3)' }
                  }}
                >
                  <HelpIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Box>
      </Paper>

      {/* Document Selector - Only show when not expanded or no messages */}
      {(!isExpanded || messages.length === 0) && (
        <Fade in timeout={500}>
          <Paper 
            elevation={0}
            sx={{ 
              p: 2, 
              mb: 1.5,
              borderRadius: 2,
              border: '1px solid',
              borderColor: 'divider',
            }}
          >
            <Box display="flex" alignItems="center" gap={1} mb={1.5}>
              <DocumentIcon color="primary" sx={{ fontSize: 20 }} />
              <Typography variant="body2" fontWeight={600}>
                Documents à analyser
              </Typography>
              <Chip 
                label={selectedDocuments.length === 0 ? "Tous" : selectedDocuments.length}
                size="small"
                color={selectedDocuments.length > 0 ? "primary" : "default"}
                sx={{ ml: 'auto' }}
              />
            </Box>

            {availableDocuments.length === 0 && !isLoadingDocuments && (
              <Alert severity="info" icon={<LightbulbIcon />} sx={{ borderRadius: 2 }}>
                Aucun document disponible. Commencez par télécharger vos documents médicaux.
              </Alert>
            )}

            <Autocomplete
              multiple
              options={availableDocuments}
              getOptionLabel={(option) => {
                const date = new Date(option.created_at).toLocaleDateString('fr-FR', { 
                  day: '2-digit', 
                  month: '2-digit', 
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                });
                const patientInfo = option.metadata?.patient_id ? ` • Patient: ${option.metadata.patient_id}` : '';
                const docType = option.document_type ? ` • ${option.document_type}` : '';
                return `${option.filename} (${date}${patientInfo}${docType})`;
              }}
              value={selectedDocuments}
              onChange={(_, newValue) => setSelectedDocuments(newValue)}
              loading={isLoadingDocuments}
              disabled={availableDocuments.length === 0}
              renderInput={(params) => (
                <TextField
                  {...params}
                  placeholder={selectedDocuments.length === 0 ? "Tous les documents indexés" : "Ajouter des documents"}
                  variant="outlined"
                  size="small"
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      borderRadius: 2,
                    },
                  }}
                />
              )}
              renderOption={(props, option) => {
                const { key, ...otherProps } = props;
                const patientId = option.metadata?.patient_id;
                const uploadDate = new Date(option.created_at).toLocaleDateString('fr-FR', {
                  day: '2-digit',
                  month: '2-digit', 
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                });
                
                return (
                  <Box 
                    component="li" 
                    key={key} 
                    {...otherProps}
                    sx={{ 
                      borderRadius: 1,
                      mb: 0.5,
                      '&:hover': {
                        bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                      }
                    }}
                  >
                    <Avatar 
                      sx={{ 
                        mr: 1.5, 
                        bgcolor: 'primary.light',
                        width: 36,
                        height: 36,
                      }}
                    >
                      <DocumentIcon fontSize="small" />
                    </Avatar>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {option.filename}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {uploadDate}
                        {patientId && ` • Patient: ${patientId}`}
                        {option.document_type && ` • ${option.document_type}`}
                      </Typography>
                    </Box>
                    {option.processing_status === 'indexed' && (
                      <Chip 
                        label="✓ Indexé" 
                        size="small" 
                        sx={{ 
                          borderColor: 'success.main',
                          color: 'success.main',
                        }} 
                        variant="outlined" 
                      />
                    )}
                  </Box>
                );
              }}
              renderTags={(value, getTagProps) =>
                value.map((option, index) => {
                  const { key, ...tagProps } = getTagProps({ index });
                  const patientLabel = option.metadata?.patient_id ? ` (${option.metadata.patient_id})` : '';
                  return (
                    <Chip
                      key={option.id}
                      {...tagProps}
                      icon={<DocumentIcon />}
                      label={`${option.filename}${patientLabel}`}
                      size="small"
                      sx={{ borderRadius: 1.5 }}
                    />
                  );
                })
              }
            />
          </Paper>
        </Fade>
      )}

      {/* Compact info when expanded with messages */}
      {isExpanded && messages.length > 0 && selectedDocuments.length > 0 && (
        <Box sx={{ mb: 1.5, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {selectedDocuments.map((doc) => (
            <Chip
              key={doc.id}
              icon={<DocumentIcon />}
              label={doc.filename}
              size="small"
              variant="outlined"
              sx={{ borderRadius: 1.5 }}
            />
          ))}
        </Box>
      )}

      {/* Chat Messages Area */}
      <Paper
        elevation={0}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          mb: 1.5,
          overflow: 'hidden',
          borderRadius: 2,
          border: '1px solid',
          borderColor: 'divider',
          minHeight: 0, // Important: allows flex child to shrink below content size
        }}
      >
        <Box
          sx={{
            flex: 1,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 2.5,
            p: 2,
            minHeight: 0, // Important: enables scrolling when content exceeds available space
            '&::-webkit-scrollbar': {
              width: '8px',
            },
            '&::-webkit-scrollbar-track': {
              background: 'transparent',
            },
            '&::-webkit-scrollbar-thumb': {
              background: (theme) => alpha(theme.palette.primary.main, 0.3),
              borderRadius: '4px',
              '&:hover': {
                background: (theme) => alpha(theme.palette.primary.main, 0.5),
              },
            },
          }}
        >
          {/* Empty State with Suggestions */}
          {messages.length === 0 && showSuggestions ? (
            <Fade in timeout={800}>
              <Box
                display="flex"
                flexDirection="column"
                alignItems="center"
                justifyContent="center"
                sx={{ flex: 1, textAlign: 'center', py: 4 }}
              >
                <Avatar
                  sx={{
                    width: 80,
                    height: 80,
                    bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                    mb: 3,
                  }}
                >
                  <PsychologyIcon sx={{ fontSize: 48, color: 'primary.main' }} />
                </Avatar>
                <Typography variant="h5" fontWeight={600} gutterBottom>
                  Comment puis-je vous aider aujourd'hui ?
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 4, maxWidth: 500 }}>
                  Je suis votre assistant médical intelligent. Posez-moi des questions sur vos documents,
                  analyses, diagnostics ou traitements.
                </Typography>

                <Box display="flex" flexWrap="wrap" gap={1.5} justifyContent="center" sx={{ maxWidth: 700 }}>
                  {suggestions.map((suggestion, index) => (
                    <Slide key={index} direction="up" in timeout={300 + index * 100}>
                      <Chip
                        icon={<LightbulbIcon />}
                        label={suggestion}
                        onClick={() => handleSuggestionClick(suggestion)}
                        clickable
                        sx={{
                          py: 2.5,
                          px: 1,
                          fontSize: '0.875rem',
                          borderRadius: 2,
                          border: '1px solid',
                          borderColor: 'divider',
                          '&:hover': {
                            bgcolor: (theme) => alpha(theme.palette.primary.main, 0.1),
                            borderColor: 'primary.main',
                            transform: 'translateY(-2px)',
                            boxShadow: 2,
                          },
                          transition: 'all 0.3s',
                        }}
                      />
                    </Slide>
                  ))}
                </Box>
              </Box>
            </Fade>
          ) : (
            messages.map((message) => (
              <Slide key={message.id} direction="up" in timeout={300}>
                <Box
                  display="flex"
                  gap={2}
                  alignItems="flex-start"
                  sx={{
                    flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  <Avatar
                    sx={{
                      bgcolor: message.role === 'user' 
                        ? 'primary.main' 
                        : (theme) => alpha(theme.palette.secondary.main, 0.9),
                      width: 42,
                      height: 42,
                      boxShadow: 2,
                    }}
                  >
                    {message.role === 'user' ? <PersonIcon /> : <AIIcon />}
                  </Avatar>

                  <Box sx={{ flex: 1, maxWidth: '75%' }}>
                    {/* Message Bubble */}
                    <Paper
                      elevation={message.role === 'user' ? 3 : 1}
                      sx={{
                        p: 2.5,
                        bgcolor: message.role === 'user' 
                          ? 'primary.main' 
                          : 'background.paper',
                        color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                        borderRadius: 3,
                        border: message.role === 'assistant' ? '1px solid' : 'none',
                        borderColor: 'divider',
                        position: 'relative',
                        '&::before': message.role === 'user' ? {
                          content: '""',
                          position: 'absolute',
                          top: 12,
                          right: -8,
                          width: 0,
                          height: 0,
                          borderLeft: '8px solid',
                          borderLeftColor: 'primary.main',
                          borderTop: '8px solid transparent',
                          borderBottom: '8px solid transparent',
                        } : {
                          content: '""',
                          position: 'absolute',
                          top: 12,
                          left: -8,
                          width: 0,
                          height: 0,
                          borderRight: '8px solid',
                          borderRightColor: 'divider',
                          borderTop: '8px solid transparent',
                          borderBottom: '8px solid transparent',
                        },
                      }}
                    >
                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.7 }}>
                        {message.content}
                      </Typography>

                      {message.confidence && (
                        <Box mt={2} display="flex" alignItems="center" gap={1}>
                          <TrendingUpIcon sx={{ fontSize: 16, opacity: 0.7 }} />
                          <Chip
                            label={`Confiance: ${(message.confidence * 100).toFixed(0)}%`}
                            size="small"
                            sx={{
                              bgcolor: message.role === 'user' 
                                ? 'rgba(255,255,255,0.2)' 
                                : alpha(getConfidenceColor(message.confidence), 0.2),
                              color: message.role === 'user' ? 'inherit' : getConfidenceColor(message.confidence),
                              fontWeight: 600,
                            }}
                          />
                        </Box>
                      )}
                    </Paper>

                    {/* Sources Accordion */}
                    {message.sources && message.sources.length > 0 && (
                      <Accordion 
                        sx={{ 
                          mt: 1.5, 
                          boxShadow: 'none',
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: '12px !important',
                          '&:before': { display: 'none' },
                        }}
                      >
                        <AccordionSummary
                          expandIcon={<ExpandMoreIcon />}
                          sx={{
                            minHeight: 48,
                            borderRadius: 1.5,
                            px: 2,
                            '&:hover': {
                              bgcolor: (theme) => alpha(theme.palette.primary.main, 0.05),
                            },
                          }}
                        >
                          <Box display="flex" alignItems="center" gap={1}>
                            <DocumentIcon fontSize="small" color="primary" />
                            <Typography variant="body2" fontWeight={600}>
                              {message.sources.length} source{message.sources.length > 1 ? 's' : ''} référencée{message.sources.length > 1 ? 's' : ''}
                            </Typography>
                          </Box>
                        </AccordionSummary>
                        <AccordionDetails sx={{ px: 2, pb: 2 }}>
                          {message.sources?.map((source, idx) => (
                            <Box key={idx} sx={{ mb: idx < (message.sources?.length ?? 0) - 1 ? 2.5 : 0 }}>
                              <Box display="flex" alignItems="center" gap={1} mb={1}>
                                <Chip 
                                  label={`Source ${idx + 1}`} 
                                  size="small" 
                                  color="primary" 
                                  variant="outlined"
                                />
                                <Typography variant="caption" fontWeight={600} color="text.secondary">
                                  {source.filename}
                                </Typography>
                              </Box>
                              <Paper
                                sx={{
                                  p: 2,
                                  bgcolor: (theme) => alpha(theme.palette.grey[100], 0.5),
                                  borderRadius: 2,
                                  borderLeft: '3px solid',
                                  borderLeftColor: 'primary.main',
                                }}
                              >
                                <Typography variant="body2" sx={{ fontStyle: 'italic', lineHeight: 1.6 }}>
                                  {source.excerpt}
                                </Typography>
                              </Paper>
                              {idx < (message.sources?.length ?? 0) - 1 && (
                                <Divider sx={{ mt: 2.5 }} />
                              )}
                            </Box>
                          ))}
                        </AccordionDetails>
                      </Accordion>
                    )}

                    <Typography 
                      variant="caption" 
                      color="text.secondary" 
                      sx={{ mt: 1, display: 'block', opacity: 0.7 }}
                    >
                      {formatDate(message.timestamp)}
                    </Typography>
                  </Box>
                </Box>
              </Slide>
            ))
          )}

          {/* Loading Indicator */}
          {askMutation.isPending && (
            <Slide direction="up" in timeout={300}>
              <Box display="flex" gap={2} alignItems="flex-start">
                <Avatar 
                  sx={{ 
                    bgcolor: (theme) => alpha(theme.palette.secondary.main, 0.9), 
                    width: 42, 
                    height: 42,
                    boxShadow: 2,
                  }}
                >
                  <AIIcon />
                </Avatar>
                <Paper 
                  sx={{ 
                    p: 2.5, 
                    bgcolor: 'background.paper', 
                    borderRadius: 3,
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                >
                  <Box display="flex" alignItems="center" gap={2}>
                    <CircularProgress size={20} thickness={4} />
                    <Box>
                      <Typography variant="body2" fontWeight={600}>
                        Analyse en cours...
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Recherche dans les documents et génération de la réponse
                      </Typography>
                    </Box>
                  </Box>
                </Paper>
              </Box>
            </Slide>
          )}

          <div ref={messagesEndRef} />
        </Box>
      </Paper>

      {/* Error Message */}
      {askMutation.error && (
        <Fade in>
          <Alert 
            severity="error" 
            sx={{ mb: 2, borderRadius: 2 }}
            action={
              <IconButton size="small" onClick={() => askMutation.reset()}>
                <CloseIcon fontSize="small" />
              </IconButton>
            }
          >
            Erreur lors de l'analyse de la question. Veuillez réessayer.
          </Alert>
        </Fade>
      )}

      {/* Modern Input Area */}
      <Paper
        elevation={isExpanded ? 2 : 2}
        sx={{
          p: isExpanded ? 1.5 : 1.5,
          borderRadius: isExpanded ? 2 : 2,
          background: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          flexShrink: 0,
        }}
      >
        <Box display="flex" gap={isExpanded ? 1.5 : 1.5} alignItems="flex-end">
          <TextField
            fullWidth
            multiline
            maxRows={isExpanded ? 3 : 3}
            placeholder="Posez votre question médicale ici..."
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={askMutation.isPending}
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                bgcolor: 'background.default',
                '&:hover': {
                  bgcolor: 'background.paper',
                },
                '&.Mui-focused': {
                  bgcolor: 'background.paper',
                },
              },
            }}
          />
          <Tooltip title={!currentMessage.trim() ? "Saisissez une question" : "Envoyer (Entrée)"}>
            <span>
              <ButtonComponent
                onClick={handleSendMessage}
                disabled={!currentMessage.trim() || askMutation.isPending}
                loading={askMutation.isPending}
                variant="contained"
                size="small"
                sx={{ 
                  minWidth: 90,
                  height: 40,
                  borderRadius: 2,
                  boxShadow: 2,
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 4,
                  },
                  transition: 'all 0.3s',
                }}
              >
                <SendIcon sx={{ mr: 0.5, fontSize: 18 }} />
                Envoyer
              </ButtonComponent>
            </span>
          </Tooltip>
        </Box>

        {!isExpanded && (
          <Box display="flex" alignItems="center" justifyContent="space-between" mt={1}>
            <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontSize: '0.7rem' }}>
              <Tooltip title="Appuyez sur Maj+Entrée pour un saut de ligne">
                <HelpIcon sx={{ fontSize: 12 }} />
              </Tooltip>
              Entrée pour envoyer
            </Typography>
            <Box display="flex" gap={1}>
              <Chip 
                icon={<DocumentIcon sx={{ fontSize: 14 }} />}
                label={`${availableDocuments.length} doc${availableDocuments.length > 1 ? 's' : ''}`}
                size="small"
                variant="outlined"
                sx={{ height: 20, fontSize: '0.7rem' }}
              />
              {messages.length > 0 && (
                <Chip 
                  label={`${messages.length} msg${messages.length > 1 ? 's' : ''}`}
                  size="small"
                  variant="outlined"
                  color="primary"
                  sx={{ height: 20, fontSize: '0.7rem' }}
                />
              )}
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
    
    {/* Error Snackbar for document selection requirement */}
    <Snackbar
      open={showDocumentError}
      autoHideDuration={4000}
      onClose={() => setShowDocumentError(false)}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
    >
      <Alert 
        onClose={() => setShowDocumentError(false)} 
        severity="warning" 
        variant="filled"
        sx={{ width: '100%' }}
      >
        Veuillez sélectionner au moins un document avant de poser une question
      </Alert>
    </Snackbar>
    </>
  );
};

export default QAChat;