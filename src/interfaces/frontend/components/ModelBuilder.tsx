import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Alert,
  Button,
  Grid,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { ModelVisualizer } from './ModelVisualizer';
import { useHardwareInfo } from '../hooks/useHardwareInfo';

// Styled components
const BuilderContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(10px)',
  borderRadius: theme.spacing(2),
}));

const ConfigSection = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(3),
}));

interface ModelBuilderProps {
  onConfigChange?: (config: any) => void;
  initialConfig?: any;
}

export function ModelBuilder({ onConfigChange, initialConfig }: ModelBuilderProps) {
  // Hardware detection hook
  const { hardwareInfo, isLoading: isHardwareLoading } = useHardwareInfo();

  // Model configuration state
  const [config, setConfig] = useState({
    model_type: 'transformer',
    hidden_size: 768,
    num_layers: 12,
    num_attention_heads: 12,
    intermediate_size: 3072,
    max_sequence_length: 1024,
    batch_size: 1,
    use_gradient_checkpointing: true,
    use_attention_optimization: true,
    use_fp16: true,
    ...initialConfig,
  });

  // Memory warnings state
  const [memoryWarning, setMemoryWarning] = useState<string | null>(null);

  // Update configuration and check memory constraints
  const updateConfig = (updates: Partial<typeof config>) => {
    const newConfig = { ...config, ...updates };
    setConfig(newConfig);

    // Calculate approximate memory usage
    const seqLen = newConfig.max_sequence_length;
    const hiddenSize = newConfig.hidden_size;
    const batchSize = newConfig.batch_size;
    const numLayers = newConfig.num_layers;

    // Rough memory estimation in GB
    const memoryPerLayer = (
      // Self-attention
      (seqLen * seqLen * hiddenSize * 4) +
      // FFN
      (seqLen * hiddenSize * 4 * 4) +
      // Layer activations
      (seqLen * hiddenSize * 4)
    ) / (1024 * 1024 * 1024);

    const totalMemory = memoryPerLayer * numLayers * batchSize;
    const effectiveMemory = newConfig.use_fp16 ? totalMemory / 2 : totalMemory;

    // Set warnings based on hardware constraints
    if (hardwareInfo?.vramGB && effectiveMemory > hardwareInfo.vramGB * 0.9) {
      setMemoryWarning(
        `Warning: Estimated memory usage (${effectiveMemory.toFixed(1)}GB) exceeds available VRAM (${hardwareInfo.vramGB}GB). Enable memory optimizations or reduce model size.`
      );
    } else if (effectiveMemory > 3.5) { // Conservative limit for 4GB cards
      setMemoryWarning(
        `Warning: Configuration may be unstable on GPUs with 4GB VRAM. Consider enabling memory optimizations.`
      );
    } else {
      setMemoryWarning(null);
    }

    // Notify parent of changes
    if (onConfigChange) {
      onConfigChange(newConfig);
    }
  };

  // Initialize with hardware-specific defaults
  useEffect(() => {
    if (hardwareInfo && !initialConfig) {
      const isLowVram = hardwareInfo.vramGB <= 4;
      updateConfig({
        batch_size: isLowVram ? 1 : 2,
        hidden_size: isLowVram ? 768 : 1024,
        num_layers: isLowVram ? 12 : 24,
        use_gradient_checkpointing: isLowVram,
        use_fp16: isLowVram,
      });
    }
  }, [hardwareInfo, initialConfig]);

  return (
    <BuilderContainer>
      <Typography variant="h5" gutterBottom>
        Model Configuration
      </Typography>

      {memoryWarning && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {memoryWarning}
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ConfigSection>
            <Typography variant="h6" gutterBottom>
              Architecture
            </Typography>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Model Type</InputLabel>
              <Select
                value={config.model_type}
                label="Model Type"
                onChange={(e) => updateConfig({ model_type: e.target.value })}
              >
                <MenuItem value="transformer">Transformer</MenuItem>
                <MenuItem value="diffusion">Diffusion Transformer</MenuItem>
              </Select>
            </FormControl>

            <Typography gutterBottom>Hidden Size</Typography>
            <Slider
              value={config.hidden_size}
              min={128}
              max={2048}
              step={128}
              marks={[
                { value: 128, label: '128' },
                { value: 768, label: '768' },
                { value: 2048, label: '2048' },
              ]}
              onChange={(_, value) => updateConfig({ hidden_size: value })}
            />

            <Typography gutterBottom>Number of Layers</Typography>
            <Slider
              value={config.num_layers}
              min={2}
              max={48}
              step={2}
              marks={[
                { value: 2, label: '2' },
                { value: 12, label: '12' },
                { value: 48, label: '48' },
              ]}
              onChange={(_, value) => updateConfig({ num_layers: value })}
            />

            <Typography gutterBottom>Attention Heads</Typography>
            <Slider
              value={config.num_attention_heads}
              min={4}
              max={32}
              step={4}
              marks={[
                { value: 4, label: '4' },
                { value: 12, label: '12' },
                { value: 32, label: '32' },
              ]}
              onChange={(_, value) => updateConfig({ num_attention_heads: value })}
            />
          </ConfigSection>

          <ConfigSection>
            <Typography variant="h6" gutterBottom>
              Training Settings
            </Typography>

            <Typography gutterBottom>Batch Size</Typography>
            <Slider
              value={config.batch_size}
              min={1}
              max={32}
              step={1}
              marks={[
                { value: 1, label: '1' },
                { value: 8, label: '8' },
                { value: 32, label: '32' },
              ]}
              onChange={(_, value) => updateConfig({ batch_size: value })}
            />

            <Typography gutterBottom>Sequence Length</Typography>
            <Slider
              value={config.max_sequence_length}
              min={128}
              max={4096}
              step={128}
              marks={[
                { value: 128, label: '128' },
                { value: 1024, label: '1K' },
                { value: 4096, label: '4K' },
              ]}
              onChange={(_, value) => updateConfig({ max_sequence_length: value })}
            />
          </ConfigSection>

          <ConfigSection>
            <Typography variant="h6" gutterBottom>
              Memory Optimizations
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={config.use_gradient_checkpointing}
                  onChange={(e) =>
                    updateConfig({ use_gradient_checkpointing: e.target.checked })
                  }
                />
              }
              label="Gradient Checkpointing"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={config.use_attention_optimization}
                  onChange={(e) =>
                    updateConfig({ use_attention_optimization: e.target.checked })
                  }
                />
              }
              label="Memory-Efficient Attention"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={config.use_fp16}
                  onChange={(e) => updateConfig({ use_fp16: e.target.checked })}
                />
              }
              label="Use FP16 Precision"
            />
          </ConfigSection>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="h6" gutterBottom>
            Model Visualization
          </Typography>
          <ModelVisualizer
            modelConfig={config}
            onConfigChange={updateConfig}
            memoryOptimized={
              config.use_gradient_checkpointing || config.use_attention_optimization
            }
          />
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={() => onConfigChange?.(config)}
        >
          Apply Configuration
        </Button>
      </Box>
    </BuilderContainer>
  );
}