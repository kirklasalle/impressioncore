import { Router } from 'express';
import { modelsRouter } from './models';
import { datasetsRouter } from './datasets';
import { authRouter } from './auth';

export const apiRouter = Router();

// Register route handlers
apiRouter.use('/models', modelsRouter);
apiRouter.use('/datasets', datasetsRouter);
apiRouter.use('/auth', authRouter);

// Health check endpoint
apiRouter.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: new Date() });
});
