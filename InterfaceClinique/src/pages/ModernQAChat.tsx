import { useState, useRef, useEffect } from 'react';
import {
  Box,
  Card,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  alpha,
  useTheme,
  Paper,
  InputAdornment,
  CircularProgress,
} from '@mui/material';
import { Send, AttachFile, SmartToy, Person } from '@mui/icons-material';
import { useAuth0 } from '@auth0/auth0-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: Date;
  sources?: string[];
}

export default function ModernQAChat() {
  const theme = useTheme();
  const { user } = useAuth0();
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Bonjour! Je suis votre assistant médical IA. Comment puis-je vous aider aujourd\'hui?',
      sender: 'ai',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newMessage]);
    setInputValue('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Voici une réponse basée sur les documents médicaux disponibles. Je peux vous fournir des informations détaillées sur les diagnostics, traitements et analyses disponibles dans votre base de données.',
        sender: 'ai',
        timestamp: new Date(),
        sources: ['Rapport_Medical_001.pdf', 'Analyse_Biologique.pdf'],
      };
      setMessages((prev) => [...prev, aiResponse]);
      setIsTyping(false);
    }, 2000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ height: 'calc(100vh - 180px)', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Assistant Q&A Médical
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Posez vos questions sur vos documents médicaux
        </Typography>
      </Box>

      {/* Chat Container */}
      <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Messages Area */}
        <Box
          sx={{
            flex: 1,
            p: 3,
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
          }}
        >
          {messages.map((message) => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                gap: 2,
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
              }}
            >
              {message.sender === 'ai' && (
                <Avatar
                  sx={{
                    bgcolor: 'primary.main',
                    width: 40,
                    height: 40,
                  }}
                >
                  <SmartToy />
                </Avatar>
              )}

              <Box
                sx={{
                  maxWidth: '70%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 1,
                }}
              >
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 3,
                    bgcolor: message.sender === 'user' ? 'primary.main' : alpha(theme.palette.primary.main, 0.08),
                    color: message.sender === 'user' ? 'white' : 'text.primary',
                    border: message.sender === 'ai' ? `1px solid ${theme.palette.divider}` : 'none',
                  }}
                >
                  <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                    {message.content}
                  </Typography>
                </Paper>

                {/* Sources */}
                {message.sources && message.sources.length > 0 && (
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Typography variant="caption" color="text.secondary">
                      Sources:
                    </Typography>
                    {message.sources.map((source, idx) => (
                      <Chip
                        key={idx}
                        label={source}
                        size="small"
                        sx={{ height: 20, fontSize: '0.7rem' }}
                        clickable
                      />
                    ))}
                  </Box>
                )}

                <Typography variant="caption" color="text.secondary">
                  {message.timestamp.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                </Typography>
              </Box>

              {message.sender === 'user' && (
                <Avatar
                  src={user?.picture}
                  sx={{
                    width: 40,
                    height: 40,
                  }}
                >
                  <Person />
                </Avatar>
              )}
            </Box>
          ))}

          {/* Typing Indicator */}
          {isTyping && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Avatar
                sx={{
                  bgcolor: 'primary.main',
                  width: 40,
                  height: 40,
                }}
              >
                <SmartToy />
              </Avatar>
              <Paper
                elevation={0}
                sx={{
                  p: 2,
                  borderRadius: 3,
                  bgcolor: alpha(theme.palette.primary.main, 0.08),
                  border: `1px solid ${theme.palette.divider}`,
                  display: 'flex',
                  gap: 0.5,
                }}
              >
                <CircularProgress size={8} />
                <CircularProgress size={8} sx={{ animationDelay: '0.2s' }} />
                <CircularProgress size={8} sx={{ animationDelay: '0.4s' }} />
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        {/* Input Area */}
        <Box
          sx={{
            p: 3,
            borderTop: `1px solid ${theme.palette.divider}`,
            bgcolor: 'background.default',
          }}
        >
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Posez votre question médicale..."
              variant="outlined"
              sx={{
                '& .MuiOutlinedInput-root': {
                  borderRadius: 3,
                  bgcolor: 'background.paper',
                },
              }}
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small">
                      <AttachFile />
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <IconButton
              color="primary"
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isTyping}
              sx={{
                bgcolor: 'primary.main',
                color: 'white',
                width: 48,
                height: 48,
                '&:hover': {
                  bgcolor: 'primary.dark',
                },
                '&:disabled': {
                  bgcolor: 'action.disabledBackground',
                },
              }}
            >
              <Send />
            </IconButton>
          </Box>

          {/* Quick Actions */}
          <Box sx={{ display: 'flex', gap: 1, mt: 2, flexWrap: 'wrap' }}>
            <Chip
              label="Résumer ce document"
              size="small"
              clickable
              onClick={() => setInputValue('Peux-tu me faire un résumé de ce document?')}
            />
            <Chip
              label="Trouver des anomalies"
              size="small"
              clickable
              onClick={() => setInputValue('Y a-t-il des anomalies dans les résultats?')}
            />
            <Chip
              label="Recommandations"
              size="small"
              clickable
              onClick={() => setInputValue('Quelles sont les recommandations?')}
            />
          </Box>
        </Box>
      </Card>
    </Box>
  );
}
