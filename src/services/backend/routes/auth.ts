import { Router } from 'express';
import { AuthService } from '../../services/auth';
import { createLogger } from '../../utils/logger';
import { authenticate } from '../../middleware/auth.middleware';

const logger = createLogger('auth.api');
export const authRouter = Router();

// POST /api/auth/login - User login
authRouter.post('/login', async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        logger.warn('Login attempt with missing credentials');
        return res.status(400).json({ error: 'Email and password are required' });
    }

    try {
        const result = await AuthService.login(email, password);

        if (!result.success) {
            return res.status(401).json({ error: result.error });
        }

        logger.info(`User ${email} authenticated successfully`);
        return res.json({
            token: result.token,
            user: {
                id: result.user?.id,
                email: result.user?.email,
                displayName: result.user?.displayName,
                roles: result.user?.roles,
            },
        });
    } catch (error) {
        logger.error('Login error', { error });
        return res.status(500).json({ error: 'Authentication failed' });
    }
});

// POST /api/auth/logout - User logout
authRouter.post('/logout', authenticate, async (req, res) => {
    try {
        if (!req.user || !req.token) {
            return res.status(400).json({ error: 'Invalid request' });
        }

        await AuthService.logout(req.user.userId, req.token);
        logger.info(`User ${req.user.userId} logged out successfully`);

        return res.json({ success: true });
    } catch (error) {
        logger.error('Logout error', { error });
        return res.status(500).json({ error: 'Logout failed' });
    }
});

// GET /api/auth/me - Get current user profile
authRouter.get('/me', authenticate, (req, res) => {
    if (!req.user) {
        return res.status(401).json({ error: 'Unauthorized' });
    }

    // In a real implementation, this would fetch the user from the database
    // using the ID from the token

    logger.info(`User profile requested for ${req.user.userId}`);
    return res.json({
        id: req.user.userId,
        roles: req.user.roles,
        identityId: req.user.identityId,
    });
});
