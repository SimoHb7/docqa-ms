import { AppBar, Toolbar, IconButton, Box, Avatar, useTheme, Tooltip, alpha } from '@mui/material';
import { Menu as MenuIcon, Brightness4, Brightness7, Settings as SettingsIcon } from '@mui/icons-material';
import { useAuth0 } from '@auth0/auth0-react';
import { useAppStore } from '../../store';
import { useNavigate } from 'react-router-dom';

interface ProfessionalHeaderProps {
  onMenuClick: () => void;
}

export default function ProfessionalHeader({ onMenuClick }: ProfessionalHeaderProps) {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user } = useAuth0();
  const { theme: appTheme, setTheme } = useAppStore();

  const toggleTheme = () => {
    setTheme(appTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        borderBottom: `1px solid ${theme.palette.divider}`,
      }}
    >
      <Toolbar sx={{ minHeight: { xs: 64, sm: 70 }, px: { xs: 2, sm: 3 }, justifyContent: 'space-between' }}>
        {/* Left Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={onMenuClick}
            sx={{
              color: 'text.primary',
              '&:hover': {
                bgcolor: alpha(theme.palette.primary.main, 0.08),
              },
            }}
          >
            <MenuIcon />
          </IconButton>
        </Box>

        {/* Right Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          {/* Theme Toggle */}
          <Tooltip title={appTheme === 'light' ? 'Mode sombre' : 'Mode clair'}>
            <IconButton
              onClick={toggleTheme}
              sx={{
                color: 'text.primary',
                '&:hover': {
                  bgcolor: alpha(theme.palette.primary.main, 0.08),
                },
              }}
            >
              {appTheme === 'light' ? <Brightness4 /> : <Brightness7 />}
            </IconButton>
          </Tooltip>

          {/* Settings */}
          <Tooltip title="Paramètres">
            <IconButton
              onClick={() => navigate('/settings')}
              sx={{
                color: 'text.primary',
                '&:hover': {
                  bgcolor: alpha(theme.palette.primary.main, 0.08),
                },
              }}
            >
              <SettingsIcon />
            </IconButton>
          </Tooltip>

          {/* User Avatar */}
          <Tooltip title={user?.name || user?.email || 'Profil'}>
            <IconButton
              onClick={() => navigate('/settings')}
              sx={{
                p: 0.5,
                ml: 1,
              }}
            >
              <Avatar
                src={user?.picture}
                alt={user?.name}
                sx={{
                  width: 40,
                  height: 40,
                  border: `2px solid ${theme.palette.primary.main}`,
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    transform: 'scale(1.05)',
                    boxShadow: `0 0 0 3px ${alpha(theme.palette.primary.main, 0.2)}`,
                  },
                }}
              >
                {user?.name?.charAt(0)}
              </Avatar>
            </IconButton>
          </Tooltip>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
