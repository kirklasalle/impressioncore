import React from 'react';
import { Box, Typography, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Handle, Position } from 'reactflow';

// Base node container styling
const NodeContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1.5),
  backgroundColor: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(8px)',
  borderRadius: theme.spacing(1),
  border: '1px solid rgba(255, 255, 255, 0.2)',
  minWidth: 150,
  '&:hover': {
    backgroundColor: 'rgba(255, 255, 255, 0.15)',
  },
}));

const MemoryBadge = styled(Box)(({ theme, memoryUsage }) => ({
  position: 'absolute',
  top: -10,
  right: -10,
  padding: theme.spacing(0.5),
  borderRadius: '50%',
  width: 24,
  height: 24,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '0.75rem',
  backgroundColor: memoryUsage > 1.0 ? theme.palette.error.main :
                  memoryUsage > 0.5 ? theme.palette.warning.main :
                  theme.palette.success.main,
  color: theme.palette.common.white,
  border: `2px solid ${theme.palette.background.paper}`,
}));

// Node type implementations
export function TransformerNode({ data }) {
  return (
    <NodeContainer>
      <Handle type="target" position={Position.Top} />
      <Typography variant="subtitle2" sx={{ mb: 1 }}>Transformer</Typography>
      <Typography variant="caption" display="block">
        {`Hidden: ${data.layer.hidden_size}`}
      </Typography>
      <Typography variant="caption" display="block">
        {`Heads: ${data.layer.num_attention_heads}`}
      </Typography>
      {data.useCheckpointing && (
        <Tooltip title="Memory-efficient: Using gradient checkpointing">
          <Box className="optimization-badge" sx={{ position: 'absolute', left: -8, top: '50%' }}>
            ⚡
          </Box>
        </Tooltip>
      )}
      <MemoryBadge memoryUsage={data.memoryUsage}>
        {data.memoryUsage.toFixed(1)}
      </MemoryBadge>
      <Handle type="source" position={Position.Bottom} />
    </NodeContainer>
  );
}

export function AttentionNode({ data }) {
  return (
    <NodeContainer>
      <Handle type="target" position={Position.Top} />
      <Typography variant="subtitle2" sx={{ mb: 1 }}>Self-Attention</Typography>
      <Typography variant="caption" display="block">
        {`Heads: ${data.num_heads}`}
      </Typography>
      {data.memoryEfficient && (
        <Tooltip title="Using memory-efficient attention">
          <Box className="optimization-badge" sx={{ position: 'absolute', left: -8, top: '50%' }}>
            ⚡
          </Box>
        </Tooltip>
      )}
      <MemoryBadge memoryUsage={data.memoryUsage}>
        {data.memoryUsage.toFixed(1)}
      </MemoryBadge>
      <Handle type="source" position={Position.Bottom} />
    </NodeContainer>
  );
}

export function MLPNode({ data }) {
  return (
    <NodeContainer>
      <Handle type="target" position={Position.Top} />
      <Typography variant="subtitle2" sx={{ mb: 1 }}>MLP</Typography>
      <Typography variant="caption" display="block">
        {`Hidden: ${data.hidden_size}`}
      </Typography>
      {data.useActivationCheckpointing && (
        <Tooltip title="Using activation checkpointing">
          <Box className="optimization-badge" sx={{ position: 'absolute', left: -8, top: '50%' }}>
            ⚡
          </Box>
        </Tooltip>
      )}
      <MemoryBadge memoryUsage={data.memoryUsage}>
        {data.memoryUsage.toFixed(1)}
      </MemoryBadge>
      <Handle type="source" position={Position.Bottom} />
    </NodeContainer>
  );
}

export function EmbeddingNode({ data }) {
  return (
    <NodeContainer sx={{ backgroundColor: 'rgba(100, 200, 255, 0.1)' }}>
      <Typography variant="subtitle2" sx={{ mb: 1 }}>Embedding</Typography>
      <Typography variant="caption" display="block">
        {`Size: ${data.embedding_size}`}
      </Typography>
      <MemoryBadge memoryUsage={data.memoryUsage}>
        {data.memoryUsage.toFixed(1)}
      </MemoryBadge>
      <Handle type="source" position={Position.Bottom} />
    </NodeContainer>
  );
}

export function OutputNode({ data }) {
  return (
    <NodeContainer sx={{ backgroundColor: 'rgba(100, 255, 150, 0.1)' }}>
      <Handle type="target" position={Position.Top} />
      <Typography variant="subtitle2">Output</Typography>
      <Typography variant="caption" display="block">
        {data.output_size ? `Size: ${data.output_size}` : ''}
      </Typography>
    </NodeContainer>
  );
}

// Export container for use in other components
export { NodeContainer };