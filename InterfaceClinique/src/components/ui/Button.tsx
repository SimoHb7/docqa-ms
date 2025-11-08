import React from 'react';
import {
  Button as MuiButton,
  ButtonProps as MuiButtonProps,
  CircularProgress,
} from '@mui/material';
import { clsx } from 'clsx';

interface ButtonProps extends Omit<MuiButtonProps, 'color'> {
  loading?: boolean;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
}

const Button: React.FC<ButtonProps> = ({
  children,
  loading = false,
  disabled,
  className,
  startIcon,
  endIcon,
  ...props
}) => {
  return (
    <MuiButton
      {...props}
      disabled={disabled || loading}
      className={clsx('btn', className)}
      startIcon={
        loading ? (
          <CircularProgress size={16} color="inherit" />
        ) : (
          startIcon
        )
      }
      endIcon={loading ? undefined : endIcon}
    >
      {children}
    </MuiButton>
  );
};

export default Button;