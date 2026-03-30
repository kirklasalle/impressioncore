import React, { ErrorInfo, Suspense } from 'react';
import {
  Box,
  Paper,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { ModelBuilder } from './ModelBuilder';

// Styled components
const ErrorContainer = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  backgroundColor: 'rgba(239, 68, 68, 0.1)',
  borderColor: theme.palette.error.main,
}));

const LoadingContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(4),
  gap: theme.spacing(2),
  minHeight: 400,
  backgroundColor: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  borderRadius: theme.shape.borderRadius,
}));

interface Props {
  initialConfig?: any;
  onConfigChange?: (config: any) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ModelVisualizerWrapper extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ModelVisualizer error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorContainer>
          <Typography variant="h6" color="error" gutterBottom>
            Visualization Error
          </Typography>
          <Alert severity="error" sx={{ mb: 2 }}>
            {this.state.error?.message || 'An error occurred while rendering the model visualization.'}
          </Alert>
          <Typography variant="body2" color="textSecondary">
            Try reducing the model size or refreshing the page. If the problem persists, check the
            console for more details.
          </Typography>
        </ErrorContainer>
      );
    }

    return (
      <Suspense
        fallback={
          <LoadingContainer>
            <CircularProgress />
            <Typography variant="body2" color="textSecondary">
              Loading model visualization...
            </Typography>
          </LoadingContainer>
        }
      >
        <ModelBuilder
          initialConfig={this.props.initialConfig}
          onConfigChange={this.props.onConfigChange}
        />
      </Suspense>
    );
  }
}