import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Box,
  Divider,
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  Memory as MemoryIcon,
  RestartAlt as RestartIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { ErrorDetails, ModelError, getMemoryErrorRecoverySteps, suggestHardwareUpgrades } from '../utils/errorHandling';

const StyledDialog = styled(Dialog)(({ theme }) => ({
  '& .MuiDialog-paper': {
    backgroundColor: 'rgba(17, 24, 39, 0.95)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: theme.shape.borderRadius * 2,
    maxWidth: 600,
  },
}));

const ErrorHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(2),
  marginBottom: theme.spacing(2),
}));

const ErrorIcon = styled(ErrorIcon)(({ theme }) => ({
  color: theme.palette.error.main,
  fontSize: 40,
}));

interface Props {
  open: boolean;
  error: ModelError | null;
  modelConfig?: any;
  onClose: () => void;
  onApplyFix?: (fix: any) => void;
}

export function ErrorDialog({ open, error, modelConfig, onClose, onApplyFix }: Props) {
  if (!error) return null;

  const details = error.details;
  const memorySteps = error.isMemoryRelated() && modelConfig 
    ? getMemoryErrorRecoverySteps(modelConfig)
    : [];
  const hardwareUpgrades = error.isMemoryRelated()
    ? suggestHardwareUpgrades(error)
    : [];

  const handleApplyFix = (fix: string) => {
    if (onApplyFix) {
      // Parse the fix description and create configuration updates
      if (fix.includes('batch size')) {
        const newBatchSize = Math.max(1, (modelConfig?.batch_size || 2) - 1);
        onApplyFix({ batch_size: newBatchSize });
      } else if (fix.includes('FP16')) {
        onApplyFix({ use_fp16: true });
      } else if (fix.includes('hidden size')) {
        onApplyFix({ hidden_size: 768 });
      } else if (fix.includes('layers')) {
        onApplyFix({ num_layers: 12 });
      }
    }
  };

  return (
    <StyledDialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      aria-labelledby="error-dialog-title"
    >
      <DialogTitle id="error-dialog-title">
        <ErrorHeader>
          <ErrorIcon />
          <Box>
            <Typography variant="h6" component="span">
              {error.name}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {error.message}
            </Typography>
          </Box>
        </ErrorHeader>
      </DialogTitle>

      <DialogContent>
        {/* Immediate fixes */}
        {memorySteps.length > 0 && (
          <>
            <Typography variant="subtitle1" gutterBottom>
              <RestartIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
              Recommended Actions
            </Typography>
            <List>
              {memorySteps.map((step, index) => (
                <ListItem
                  key={index}
                  secondaryAction={
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={() => handleApplyFix(step)}
                    >
                      Apply
                    </Button>
                  }
                >
                  <ListItemIcon>
                    <CheckIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary={step} />
                </ListItem>
              ))}
            </List>
            <Divider sx={{ my: 2 }} />
          </>
        )}

        {/* General suggestions */}
        <Typography variant="subtitle1" gutterBottom>
          <WarningIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
          Suggestions
        </Typography>
        <List>
          {details.suggestions.map((suggestion, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                <WarningIcon color="warning" />
              </ListItemIcon>
              <ListItemText primary={suggestion} />
            </ListItem>
          ))}
        </List>

        {/* Hardware upgrade suggestions */}
        {hardwareUpgrades.length > 0 && (
          <>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" gutterBottom>
              <MemoryIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
              Hardware Considerations
            </Typography>
            <List>
              {hardwareUpgrades.map((upgrade, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <MemoryIcon />
                  </ListItemIcon>
                  <ListItemText primary={upgrade} />
                </ListItem>
              ))}
            </List>
          </>
        )}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
        {error.isRecoverable() && (
          <Button
            variant="contained"
            color="primary"
            onClick={() => {
              if (memorySteps.length > 0) {
                handleApplyFix(memorySteps[0]);
              }
              onClose();
            }}
          >
            Apply Recommended Fix
          </Button>
        )}
      </DialogActions>
    </StyledDialog>
  );
}