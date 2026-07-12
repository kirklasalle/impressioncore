import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import App from './App';
import './index.css';

// Pages — lazy loaded
import HomePage from './pages/HomePage';
import IntroductionPage from './pages/IntroductionPage';
import SystemSetupPage from './pages/SystemSetupPage';
import DataPrepPage from './pages/DataPrepPage';
import TokenizerPage from './pages/TokenizerPage';
import ModelDefinitionPage from './pages/ModelDefinitionPage';
import TrainingPage from './pages/TrainingPage';
import EvaluationPage from './pages/EvaluationPage';
import InferencePage from './pages/InferencePage';
import DeploymentPage from './pages/DeploymentPage';
import WalkthroughPage from './pages/WalkthroughPage';
import KnowledgePage from './pages/KnowledgePage';
import RuleEnginePage from './pages/RuleEnginePage';
import InheritancePage from './pages/InheritancePage';
import UnifiedBuilderPage from './pages/UnifiedBuilderPage';
import GpuSetupPage from './pages/GpuSetupPage';
import ArchitecturePage from './pages/ArchitecturePage';
import CheckpointsPage from './pages/CheckpointsPage';
import ChatPage from './pages/ChatPage';
import DocumentationPage from './pages/DocumentationPage';
import StorageControlPage from './pages/StorageControlPage';

// Error Boundary
class ErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null, errorInfo: null };
    }
    static getDerivedStateFromError(error) {
        return { hasError: true };
    }
    componentDidCatch(error, errorInfo) {
        console.error('[Builder] Crash:', error, errorInfo.componentStack);
        this.setState({ error, errorInfo });
    }
    render() {
        if (this.state.hasError) {
            return (
                <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center p-8">
                    <div className="max-w-lg text-center">
                        <h1 className="text-3xl font-bold text-red-400 mb-4">Builder Crashed</h1>
                        <pre className="text-left text-sm text-amber-300 bg-[#111827] rounded-lg p-4 overflow-auto mb-4">
                            {this.state.error?.toString()}
                        </pre>
                        <button
                            onClick={() => window.location.reload()}
                            className="btn-primary"
                        >
                            Reload
                        </button>
                    </div>
                </div>
            );
        }
        return this.props.children;
    }
}

const router = createBrowserRouter([
    {
        path: '/',
        element: <App />,
        children: [
            { index: true, element: <HomePage /> },
            { path: 'introduction', element: <IntroductionPage /> },
            { path: 'system-setup', element: <SystemSetupPage /> },
            { path: 'system_requirements', element: <SystemSetupPage /> },
            { path: 'data-prep', element: <DataPrepPage /> },
            { path: 'data_prep', element: <DataPrepPage /> },
            { path: 'tokenizer', element: <TokenizerPage /> },
            { path: 'model-definition', element: <ModelDefinitionPage /> },
            { path: 'define_model', element: <ModelDefinitionPage /> },
            { path: 'training', element: <TrainingPage /> },
            { path: 'evaluation', element: <EvaluationPage /> },
            { path: 'inference', element: <InferencePage /> },
            { path: 'deployment', element: <DeploymentPage /> },
            { path: 'walkthrough', element: <WalkthroughPage /> },
            { path: 'knowledge', element: <KnowledgePage /> },
            { path: 'uks_introduction', element: <KnowledgePage /> },
            { path: 'rule-engine', element: <RuleEnginePage /> },
            { path: 'rule_engine', element: <RuleEnginePage /> },
            { path: 'inheritance', element: <InheritancePage /> },
            { path: 'unified-builder', element: <UnifiedBuilderPage /> },
            { path: 'unified_builder', element: <UnifiedBuilderPage /> },
            { path: 'gpu-setup', element: <GpuSetupPage /> },
            { path: 'gpu_setup', element: <GpuSetupPage /> },
            { path: 'architecture', element: <ArchitecturePage /> },
            { path: 'model_architecture', element: <ArchitecturePage /> },
            { path: 'checkpoints', element: <CheckpointsPage /> },
            { path: 'checkpoint', element: <CheckpointsPage /> },
            { path: 'chat', element: <ChatPage /> },
            { path: 'documentation', element: <DocumentationPage /> },
            { path: 'storage-control', element: <StorageControlPage /> },
        ],
    },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
    <React.StrictMode>
        <ErrorBoundary>
            <RouterProvider router={router} />
        </ErrorBoundary>
    </React.StrictMode>,
);
