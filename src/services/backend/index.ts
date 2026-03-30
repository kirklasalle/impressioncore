import express from 'express';
import path from 'path';
import { createLogger } from '../utils/logger';
import { apiRouter } from './routes';

// Initialize logger
const logger = createLogger('backend');

// Initialize express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files from the React app
app.use(express.static(path.join(__dirname, '../../build')));

// API routes
app.use('/api', apiRouter);

// The "catchall" handler: for any request that doesn't match the ones above,
// send back React's index.html file.
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../../build/index.html'));
});

// Start server
app.listen(PORT, () => {
    logger.info(`Server running on port ${PORT}`);
});

export default app;
