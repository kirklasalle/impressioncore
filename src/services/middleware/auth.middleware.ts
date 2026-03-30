import { Request, Response, NextFunction } from 'express';
import { AuthService } from '../services/auth';
import { createLogger } from '../utils/logger';

// Initialize logger
const logger = createLogger('auth.middleware');

// Extend Express Request interface to include user information
declare global {
    namespace Express {
        interface Request {
            user?: any;
            token?: string;
        }
    }
}

/**
 * Authentication middleware to protect routes
 */
export const authenticate = (req: Request, res: Response, next: NextFunction) => {
    // Get the authorization header
    const authHeader = req.headers.authorization;

    if (!authHeader || !authHeader.startsWith('Bearer ')) {
        logger.warn('Authentication failed - No valid auth header');
        return res.status(401).json({ error: 'Authentication required' });
    }

    // Extract the token
    const token = authHeader.split(' ')[1];

    // Validate the token
    const validation = AuthService.validateToken(token);

    if (!validation.isValid || !validation.data) {
        logger.warn('Authentication failed - Invalid token');
        return res.status(401).json({ error: 'Invalid or expired token' });
    }

    // Attach user data to the request for downstream use
    req.user = validation.data;
    req.token = token;

    logger.debug('User authenticated successfully', { userId: validation.data.userId });

    // Continue to the next middleware or route handler
    next();
};

/**
 * Authorization middleware to restrict routes to specific roles
 */
export const authorize = (requiredRole: string) => {
    return (req: Request, res: Response, next: NextFunction) => {
        // Check if user is authenticated
        if (!req.user) {
            logger.warn('Authorization failed - User not authenticated');
            return res.status(401).json({ error: 'Authentication required' });
        }

        // Check if user has the required role
        if (!req.user.roles.includes(requiredRole)) {
            logger.warn(`Authorization failed - User lacks role: ${requiredRole}`, {
                userId: req.user.userId,
                roles: req.user.roles,
            });
            return res.status(403).json({ error: 'Permission denied' });
        }

        logger.debug(`User authorized with role: ${requiredRole}`, { userId: req.user.userId });

        // User has the required role, continue
        next();
    };
};
