import { AppBar, Toolbar, IconButton, Typography, Box, Avatar, Menu, MenuItem, Badge, useTheme, alpha, Tooltip } from '@mui/material';
import { Menu as MenuIcon, Notifications as NotificationsIcon, Search as SearchIcon, Brightness4, Brightness7 } from '@mui/icons-material';
import { useAuth0 } from '@auth0/auth0-react';
import { useState } from 'react';
import { useAppStore } from '../../store';

interface ModernHeaderProps {
  onMenuClick: () => void;
}

export default function ModernHeader({ onMenuClick }: ModernHeaderProps) {
  const theme = useTheme();
  const { user } = useAuth0();
  const { theme: appTheme, setTheme } = useAppStore();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const toggleTheme = () => {
    setTheme(appTheme === 'light' ? 'dark' : 'light');
  };

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: theme.palette.mode === 'dark' ? 'grey.900' : 'white',
        borderBottom: `1px solid ${theme.palette.divider}`,
        color: 'text.primary',
      }}
    >
      <Toolbar sx={{ minHeight: { xs: 64, sm: 70 }, px: { xs: 2, sm: 3 } }}>
        {/* Menu Button */}
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          onClick={onMenuClick}
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        {/* Search Bar (Desktop) */}
        <Box
          sx={{
            display: { xs: 'none', md: 'flex' },
            alignItems: 'center',
            flex: 1,
            maxWidth: 600,
            bgcolor: alpha(theme.palette.primary.main, 0.04),
            borderRadius: 3,
            px: 2,
            py: 1,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.08)}`,
            '&:hover': {
              bgcolor: alpha(theme.palette.primary.main, 0.08),
            },
          }}
        >
          <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
          <input
            type="text"
            placeholder="Rechercher des documents, patients..."
            style={{
              border: 'none',
              outline: 'none',
              background: 'transparent',
              width: '100%',
              fontSize: '0.95rem',
              color: theme.palette.text.primary,
            }}
          />
        </Box>

        {/* Spacer */}
        <Box sx={{ flex: 1, display: { md: 'none' } }} />

        {/* Right Section */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Search Icon (Mobile) */}
          <IconButton
            color="inherit"
            sx={{ display: { xs: 'flex', md: 'none' } }}
          >
            <SearchIcon />
          </IconButton>

          {/* Theme Toggle */}
          <Tooltip title={appTheme === 'light' ? 'Mode sombre' : 'Mode clair'}>
            <IconButton onClick={toggleTheme} color="inherit">
              {appTheme === 'light' ? <Brightness4 /> : <Brightness7 />}
            </IconButton>
          </Tooltip>

          {/* Notifications */}
          <Tooltip title="Notifications">
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* User Profile */}
          <IconButton onClick={handleMenu} sx={{ ml: 1, p: 0.5 }}>
            <Avatar
              src={user?.picture}
              alt={user?.name}
              sx={{
                width: 40,
                height: 40,
                border: `2px solid ${theme.palette.primary.main}`,
              }}
            >
              {user?.name?.charAt(0)}
            </Avatar>
          </IconButton>

          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
            transformOrigin={{ horizontal: 'right', vertical: 'top' }}
            anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          >
            <MenuItem onClick={handleClose}>Profile</MenuItem>
            <MenuItem onClick={handleClose}>Paramètres</MenuItem>
            <MenuItem onClick={handleClose}>Aide</MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
