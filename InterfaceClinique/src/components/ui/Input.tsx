import React from 'react';
import {
  TextField,
  TextFieldProps,
  InputAdornment,
  IconButton,
} from '@mui/material';
import { Visibility, VisibilityOff } from '@mui/icons-material';

interface InputProps extends Omit<TextFieldProps, 'variant'> {
  variant?: 'outlined' | 'filled' | 'standard';
  showPasswordToggle?: boolean;
}

const Input: React.FC<InputProps> = ({
  showPasswordToggle = false,
  type = 'text',
  ...props
}) => {
  const [showPassword, setShowPassword] = React.useState(false);

  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };

  const inputType = showPasswordToggle
    ? (showPassword ? 'text' : 'password')
    : type;

  const endAdornment = showPasswordToggle ? (
    <InputAdornment position="end">
      <IconButton
        aria-label="toggle password visibility"
        onClick={handleTogglePassword}
        edge="end"
      >
        {showPassword ? <VisibilityOff /> : <Visibility />}
      </IconButton>
    </InputAdornment>
  ) : undefined;

  return (
    <TextField
      {...props}
      type={inputType}
      variant="outlined"
      className="input"
      InputProps={{
        ...props.InputProps,
        endAdornment,
      }}
    />
  );
};

export default Input;