/**
 * Model architecture visualization component using React Flow
 * Optimized for showing memory-efficient model configurations
 */

import React, { useCallback, useState, useEffect } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Box, Typography, Paper, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';

// Custom styled components
const VisualizerContainer = styled(Paper)(({ theme }) => ({
  height: '600px',
  width: '100%',
  backgroundColor: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(10px)',
  borderRadius: theme.spacing(2),
  overflow: 'hidden',
}));

const MemoryIndicator = styled(Box)(({ theme, memoryUsage }) => ({
  position: 'absolute',
  top: theme.spacing(2),
  right: theme.spacing(2),
  padding: theme.spacing(1, 2),
  borderRadius: theme.spacing(1),
  backgroundColor: memoryUsage > 3.5 ? theme.palette.error.main : 
                  memoryUsage > 2.5 ? theme.palette.warning.main :
                  theme.palette.success.main,
  color: theme.palette.common.white,
  zIndex: 1000,
}));

// Custom node types
const nodeTypes = {
  transformer: TransformerNode,
  attention: AttentionNode,
  mlp: MLPNode,
  embedding: EmbeddingNode,
  output: OutputNode,
};

// Node components
function TransformerNode({ data }) {
  return (
    <NodeContainer>
      <Typography variant="subtitle2">Transformer Block</Typography>
      <Typography variant="caption">
        {`Memory: ${data.memoryUsage.toFixed(2)}GB`}
      </Typography>
      {data.useCheckpointing && (
        <Tooltip title="Gradient checkpointing enabled">
          <Box className="memory-efficient-badge">✓</Box>
        </Tooltip>
      )}
    </NodeContainer>
  );
}

// Similar implementations for other node types...

interface ModelVisualizerProps {
  modelConfig: any;
  onConfigChange?: (config: any) => void;
  memoryOptimized?: boolean;
}

export function ModelVisualizer({
  modelConfig,
  onConfigChange,
  memoryOptimized = true,
}: ModelVisualizerProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [totalMemoryUsage, setTotalMemoryUsage] = useState(0);

  // Convert model config to visualization nodes
  const createNodesFromConfig = useCallback((config) => {
    const newNodes: Node[] = [];
    const newEdges: Edge[] = [];
    let yPos = 0;
    let totalMemory = 0;

    // Input embedding
    newNodes.push({
      id: 'input',
      type: 'embedding',
      position: { x: 250, y: yPos },
      data: { 
        label: 'Input Embedding',
        memoryUsage: config.embedding_size * 0.000004, // Approximate GB
      },
    });
    yPos += 100;

    // Transformer layers
    config.layers.forEach((layer, i) => {
      const layerMemory = calculateLayerMemory(layer, config);
      totalMemory += layerMemory;

      newNodes.push({
        id: `transformer_${i}`,
        type: 'transformer',
        position: { x: 250, y: yPos },
        data: {
          layer,
          memoryUsage: layerMemory,
          useCheckpointing: memoryOptimized && layerMemory > 0.5,
        },
      });

      if (i > 0) {
        newEdges.push({
          id: `edge_${i}`,
          source: `transformer_${i-1}`,
          target: `transformer_${i}`,
          type: 'smoothstep',
          markerEnd: { type: MarkerType.ArrowClosed },
        });
      } else {
        newEdges.push({
          id: 'edge_input',
          source: 'input',
          target: 'transformer_0',
          type: 'smoothstep',
          markerEnd: { type: MarkerType.ArrowClosed },
        });
      }
      yPos += 100;
    });

    // Output layer
    newNodes.push({
      id: 'output',
      type: 'output',
      position: { x: 250, y: yPos },
      data: { label: 'Output' },
    });

    newEdges.push({
      id: 'edge_output',
      source: `transformer_${config.layers.length - 1}`,
      target: 'output',
      type: 'smoothstep',
      markerEnd: { type: MarkerType.ArrowClosed },
    });

    setNodes(newNodes);
    setEdges(newEdges);
    setTotalMemoryUsage(totalMemory);
  }, [setNodes, setEdges]);

  // Update visualization when config changes
  useEffect(() => {
    createNodesFromConfig(modelConfig);
  }, [modelConfig, createNodesFromConfig]);

  // Memory usage calculation helpers
  const calculateLayerMemory = (layer: any, config: any) => {
    const seqLen = config.max_sequence_length || 1024;
    const hiddenSize = config.hidden_size || 768;
    const batchSize = config.batch_size || 1;
    
    // Calculate approximate memory usage in GB
    const attentionMem = (seqLen * seqLen * hiddenSize * 4) / (1024 * 1024 * 1024);
    const ffnMem = (seqLen * hiddenSize * 4 * 4) / (1024 * 1024 * 1024);
    const activationMem = (seqLen * hiddenSize * 4) / (1024 * 1024 * 1024);
    
    return (attentionMem + ffnMem + activationMem) * batchSize;
  };

  return (
    <VisualizerContainer>
      <MemoryIndicator memoryUsage={totalMemoryUsage}>
        {`Estimated VRAM: ${totalMemoryUsage.toFixed(2)}GB`}
      </MemoryIndicator>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
      </ReactFlow>
    </VisualizerContainer>
  );
}