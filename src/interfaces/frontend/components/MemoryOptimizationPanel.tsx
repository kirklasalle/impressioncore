import React from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  Divider,
  Stack,
  Tooltip,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Warning as WarningIcon,
  CheckCircle as CheckIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import {
  MemoryEstimate,
  MemoryOptimizationSuggestion,
  estimateModelMemory,
  suggestMemoryOptimizations,
} from '../utils/memoryUtils';

const OptimizationContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  borderRadius: theme.shape.borderRadius,
}));

const MemoryIndicator = styled(Box)(({ theme, memoryUsage }) => ({
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: memoryUsage > 3.8 ? theme.palette.error.dark :
                  memoryUsage > 3.0 ? theme.palette.warning.dark :
                  theme.palette.success.dark,
  color: theme.palette.common.white,
}));

const MetricBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  backgroundColor: 'rgba(255, 255, 255, 0.1)',
  borderRadius: theme.shape.borderRadius,
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
}));

interface Props {
  modelConfig: any;
  onOptimizationApply: (optimizations: Partial<any>) => void;
}

export function MemoryOptimizationPanel({ modelConfig, onOptimizationApply }: Props) {
  // Calculate memory estimates
  const memoryEstimate = estimateModelMemory(modelConfig);
  const suggestions = suggestMemoryOptimizations(modelConfig, memoryEstimate);

  const applyOptimization = (suggestion: MemoryOptimizationSuggestion) => {
    const updates = {
      [suggestion.type]: suggestion.suggestedValue,
    };
    onOptimizationApply(updates);
  };

  return (
    <OptimizationContainer>
      <Typography variant="h6" gutterBottom>
        Memory Analysis
      </Typography>

      {/* Memory usage overview */}
      <MemoryIndicator memoryUsage={memoryEstimate.totalGb}>
        <Stack direction="row" spacing={2} alignItems="center">
          <MemoryIcon />
          <div>
            <Typography variant="subtitle1">
              Estimated VRAM Usage: {memoryEstimate.totalGb.toFixed(1)}GB
            </Typography>
            <Typography variant="caption">
              {memoryEstimate.isWithinBudget 
                ? '✓ Within 4GB budget'
                : '⚠️ Exceeds recommended limit for 4GB GPUs'}
            </Typography>
          </div>
        </Stack>
      </MemoryIndicator>

      {/* Memory breakdown */}
      <Box sx={{ my: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Memory Breakdown
        </Typography>
        <Stack direction="row" spacing={1} sx={{ mb: 2 }}>
          <Tooltip title="Attention mechanism memory usage">
            <MetricBox>
              <Typography variant="caption">Attention</Typography>
              <Typography variant="body2">
                {memoryEstimate.attentionGb.toFixed(1)}GB
              </Typography>
            </MetricBox>
          </Tooltip>
          <Tooltip title="Feed-forward network memory usage">
            <MetricBox>
              <Typography variant="caption">FFN</Typography>
              <Typography variant="body2">
                {memoryEstimate.ffnGb.toFixed(1)}GB
              </Typography>
            </MetricBox>
          </Tooltip>
          <Tooltip title="Model activations memory usage">
            <MetricBox>
              <Typography variant="caption">Activations</Typography>
              <Typography variant="body2">
                {memoryEstimate.activationsGb.toFixed(1)}GB
              </Typography>
            </MetricBox>
          </Tooltip>
        </Stack>
      </Box>

      {/* Warnings */}
      {memoryEstimate.warnings.length > 0 && (
        <Box sx={{ mb: 2 }}>
          <Typography variant="subtitle2" color="warning.main" gutterBottom>
            <WarningIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
            Warnings
          </Typography>
          <List dense>
            {memoryEstimate.warnings.map((warning, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <WarningIcon color="warning" />
                </ListItemIcon>
                <ListItemText primary={warning} />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Optimization suggestions */}
      {suggestions.length > 0 && (
        <>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>
            <SpeedIcon sx={{ mr: 1, verticalAlign: 'bottom' }} />
            Suggested Optimizations
          </Typography>
          <List>
            {suggestions.map((suggestion, index) => (
              <ListItem
                key={index}
                secondaryAction={
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => applyOptimization(suggestion)}
                    startIcon={<TrendingDownIcon />}
                  >
                    Apply
                  </Button>
                }
              >
                <ListItemText
                  primary={suggestion.description}
                  secondary={
                    <Stack direction="row" spacing={1} sx={{ mt: 0.5 }}>
                      <Chip
                        size="small"
                        label={`Impact: ${suggestion.impact.toFixed(1)}GB`}
                        color="success"
                      />
                    </Stack>
                  }
                />
              </ListItem>
            ))}
          </List>
        </>
      )}

      {/* Success message when within budget */}
      {memoryEstimate.isWithinBudget && (
        <Box sx={{ mt: 2, p: 2, bgcolor: 'success.dark', borderRadius: 1 }}>
          <Stack direction="row" spacing={1} alignItems="center">
            <CheckIcon color="inherit" />
            <Typography>
              Configuration is optimized for your 4GB GPU
            </Typography>
          </Stack>
        </Box>
      )}
    </OptimizationContainer>
  );
}