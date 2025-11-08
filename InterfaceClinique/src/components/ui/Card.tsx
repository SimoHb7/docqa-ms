import React from 'react';
import {
  Card as MuiCard,
  CardProps as MuiCardProps,
  CardContent,
  CardHeader,
  CardActions,
  Typography,
} from '@mui/material';
import { clsx } from 'clsx';

interface CardProps extends MuiCardProps {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  actions?: React.ReactNode;
  noPadding?: boolean;
}

const Card: React.FC<CardProps> = ({
  children,
  title,
  subtitle,
  icon,
  actions,
  noPadding = false,
  className,
  ...props
}) => {
  return (
    <MuiCard className={clsx('card', className)} {...props}>
      {(title || subtitle) && (
        <CardHeader
          avatar={icon}
          title={title && (
            <Typography variant="h6" component="h2">
              {title}
            </Typography>
          )}
          subheader={subtitle && (
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
          )}
          action={actions}
        />
      )}
      <CardContent className={noPadding ? 'p-0' : ''}>
        {children}
      </CardContent>
      {actions && !title && !subtitle && (
        <CardActions>{actions}</CardActions>
      )}
    </MuiCard>
  );
};

export default Card;