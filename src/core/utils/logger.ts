import fs from 'fs';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

// Define log levels
type LogLevel = 'debug' | 'info' | 'warn' | 'error' | 'critical';

// Define log severity levels for alerting
const LOG_SEVERITY = {
    debug: 0,
    info: 1,
    warn: 2,
    error: 3,
    critical: 4
};

// Define log entry structure
interface LogEntry {
    id: string;
    timestamp: string;
    level: LogLevel;
    module: string;
    message: string;
    correlationId?: string;
    sessionId?: string;
    data?: any;
    metrics?: Record<string, number>;
    tags?: string[];
}

interface LogConfig {
    maxFileSizeMB?: number;
    rotationFileCount?: number;
    alertOnLevels?: LogLevel[];
    consoleOutput?: boolean;
}

const DEFAULT_CONFIG: LogConfig = {
    maxFileSizeMB: 10,
    rotationFileCount: 5,
    alertOnLevels: ['error', 'critical'],
    consoleOutput: true
};

// Global configuration
let globalConfig: LogConfig = { ...DEFAULT_CONFIG };

// Active alert subscribers
const alertSubscribers: Array<(entry: LogEntry) => void> = [];

// Ensure memlog directory structure exists
const createMemlogDirectories = (): void => {
    const memlogDir = path.join(process.cwd(), 'memlog');
    const dirs = [
        'state',
        'tasks',
        'persistence',
        'changelogs',
        'metrics',
        'alerts',
        'sessions',
        'audit'
    ];

    if (!fs.existsSync(memlogDir)) {
        fs.mkdirSync(memlogDir, { recursive: true });
    }

    dirs.forEach(dir => {
        const dirPath = path.join(memlogDir, dir);
        if (!fs.existsSync(dirPath)) {
            fs.mkdirSync(dirPath, { recursive: true });
        }
    });
};

// Verify memlog structure integrity
const verifyMemlogStructure = (): boolean => {
    const memlogDir = path.join(process.cwd(), 'memlog');
    const requiredDirs = [
        'state',
        'tasks',
        'persistence',
        'changelogs',
        'metrics',
        'alerts',
        'sessions',
        'audit'
    ];

    if (!fs.existsSync(memlogDir)) {
        return false;
    }

    return requiredDirs.every(dir => fs.existsSync(path.join(memlogDir, dir)));
};

// Initialize memlog
const initMemlog = (): void => {
    createMemlogDirectories();

    // Verify structure integrity
    if (!verifyMemlogStructure()) {
        throw new Error('Memlog structure integrity verification failed');
    }

    // Create initial changelog entry
    const initialLog: LogEntry = {
        id: uuidv4(),
        timestamp: new Date().toISOString(),
        level: 'info',
        module: 'system',
        message: 'Memlog initialized',
        tags: ['system', 'startup']
    };

    logToFile('changelogs/system.log', initialLog);

    // Create system health check file
    const healthCheck = {
        lastChecked: new Date().toISOString(),
        status: 'healthy',
        memlogIntegrityVerified: true
    };

    fs.writeFileSync(
        path.join(process.cwd(), 'memlog', 'health.json'),
        JSON.stringify(healthCheck, null, 2)
    );
};

// Update system health status
const updateHealthStatus = (status: 'healthy' | 'degraded' | 'unhealthy', details?: any): void => {
    const healthFilePath = path.join(process.cwd(), 'memlog', 'health.json');

    let currentHealth = { status: 'unknown', lastChecked: '' };
    if (fs.existsSync(healthFilePath)) {
        try {
            currentHealth = JSON.parse(fs.readFileSync(healthFilePath, 'utf8'));
        } catch (error) {
            // If health file is corrupted, create a new one
        }
    }

    const healthCheck = {
        ...currentHealth,
        lastChecked: new Date().toISOString(),
        status,
        details: details || currentHealth.details,
        memlogIntegrityVerified: verifyMemlogStructure()
    };

    fs.writeFileSync(healthFilePath, JSON.stringify(healthCheck, null, 2));
}

// Get file size in MB
const getFileSizeInMB = (filePath: string): number => {
    try {
        const stats = fs.statSync(filePath);
        return stats.size / (1024 * 1024);
    } catch (error) {
        return 0;
    }
};

// Rotate log file if it exceeds max size
const rotateLogFileIfNeeded = (filePath: string): void => {
    const fullPath = path.join(process.cwd(), 'memlog', filePath);

    if (!fs.existsSync(fullPath)) {
        return;
    }

    const fileSizeMB = getFileSizeInMB(fullPath);

    if (fileSizeMB >= (globalConfig.maxFileSizeMB || DEFAULT_CONFIG.maxFileSizeMB)) {
        const maxRotationFiles = globalConfig.rotationFileCount || DEFAULT_CONFIG.rotationFileCount;

        // Delete oldest rotation file if it exists
        if (fs.existsSync(`${fullPath}.${maxRotationFiles}`)) {
            fs.unlinkSync(`${fullPath}.${maxRotationFiles}`);
        }

        // Shift rotation files
        for (let i = maxRotationFiles - 1; i >= 1; i--) {
            const oldFile = `${fullPath}.${i}`;
            const newFile = `${fullPath}.${i + 1}`;

            if (fs.existsSync(oldFile)) {
                fs.renameSync(oldFile, newFile);
            }
        }

        // Rename current log file to .1
        fs.renameSync(fullPath, `${fullPath}.1`);
    }
};

// Write log entry to file
const logToFile = (filePath: string, entry: LogEntry): void => {
    const memlogDir = path.join(process.cwd(), 'memlog');
    const fullPath = path.join(memlogDir, filePath);

    // Ensure directory exists
    const dir = path.dirname(fullPath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }

    // Check if file needs rotation
    rotateLogFileIfNeeded(filePath);

    // Append to log file
    fs.appendFileSync(fullPath, JSON.stringify(entry) + '\n');

    // If this is an alert level log, also write to alerts folder
    const alertLevels = globalConfig.alertOnLevels || DEFAULT_CONFIG.alertOnLevels;
    if (alertLevels?.includes(entry.level)) {
        const alertPath = `alerts/${entry.level}/${new Date().toISOString().split('T')[0]}.log`;
        fs.appendFileSync(path.join(memlogDir, alertPath), JSON.stringify(entry) + '\n');

        // Notify subscribers
        alertSubscribers.forEach(subscriber => subscriber(entry));
    }

    // Output to console if enabled
    if (globalConfig.consoleOutput) {
        const consoleColors = {
            debug: '\x1b[36m', // cyan
            info: '\x1b[32m',  // green
            warn: '\x1b[33m',  // yellow
            error: '\x1b[31m', // red
            critical: '\x1b[41m\x1b[37m' // white on red background
        };
        const resetColor = '\x1b[0m';

        console.log(
            `${consoleColors[entry.level]}[${entry.timestamp}] [${entry.level.toUpperCase()}] [${entry.module}] ${entry.message}${resetColor}`
        );

        if (entry.data) {
            console.log(entry.data);
        }
    }
};

// Configuration management
const configureLogging = (config: Partial<LogConfig>): void => {
    globalConfig = { ...DEFAULT_CONFIG, ...config };
};

// Register alert subscriber
const subscribeToAlerts = (callback: (entry: LogEntry) => void): () => void => {
    alertSubscribers.push(callback);

    // Return unsubscribe function
    return () => {
        const index = alertSubscribers.indexOf(callback);
        if (index !== -1) {
            alertSubscribers.splice(index, 1);
        }
    };
};

// Query logs with filtering
const queryLogs = (
    folder: string,
    options: {
        level?: LogLevel,
        module?: string,
        startDate?: Date,
        endDate?: Date,
        limit?: number
    } = {}
): LogEntry[] => {
    try {
        const memlogDir = path.join(process.cwd(), 'memlog');
        const targetDir = path.join(memlogDir, folder);

        if (!fs.existsSync(targetDir)) {
            return [];
        }

        // Get all log files in the directory
        const files = fs.readdirSync(targetDir)
            .filter(file => file.endsWith('.log'))
            .map(file => path.join(targetDir, file));

        let entries: LogEntry[] = [];

        // Read and parse log entries from each file
        for (const file of files) {
            const content = fs.readFileSync(file, 'utf8');
            const lines = content.trim().split('\n');

            for (const line of lines) {
                try {
                    const entry: LogEntry = JSON.parse(line);

                    // Apply filters
                    if (options.level && entry.level !== options.level) continue;
                    if (options.module && entry.module !== options.module) continue;

                    if (options.startDate && new Date(entry.timestamp) < options.startDate) continue;
                    if (options.endDate && new Date(entry.timestamp) > options.endDate) continue;

                    entries.push(entry);
                } catch (e) {
                    // Skip invalid log entries
                }
            }
        }

        // Sort by timestamp descending (newest first)
        entries.sort((a, b) =>
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );

        // Apply limit if specified
        if (options.limit && options.limit > 0) {
            entries = entries.slice(0, options.limit);
        }

        return entries;
    } catch (error) {
        console.error('Error querying logs:', error);
        return [];
    }
};

// Create logger for a specific module
export const createLogger = (module: string, correlationId?: string) => {
    // Initialize memlog if it doesn't exist
    if (!verifyMemlogStructure()) {
        initMemlog();
    }

    // Automatically generate correlation ID if not provided
    const loggerCorrelationId = correlationId || uuidv4();

    // Create session ID for this logger instance
    const sessionId = uuidv4();

    const createLogEntry = (
        level: LogLevel,
        message: string,
        data?: any,
        options?: {
            tags?: string[],
            metrics?: Record<string, number>,
            correlationId?: string
        }
    ): LogEntry => {
        return {
            id: uuidv4(),
            timestamp: new Date().toISOString(),
            level,
            module,
            message,
            data,
            correlationId: options?.correlationId || loggerCorrelationId,
            sessionId,
            metrics: options?.metrics,
            tags: options?.tags || []
        };
    };

    return {
        debug: (message: string, data?: any, options?: { tags?: string[], metrics?: Record<string, number> }) => {
            const entry = createLogEntry('debug', message, data, options);
            logToFile(`state/${module}.log`, entry);
        },

        info: (message: string, data?: any, options?: { tags?: string[], metrics?: Record<string, number> }) => {
            const entry = createLogEntry('info', message, data, options);
            logToFile(`state/${module}.log`, entry);
        },

        warn: (message: string, data?: any, options?: { tags?: string[], metrics?: Record<string, number> }) => {
            const entry = createLogEntry('warn', message, data, options);
            logToFile(`state/${module}.log`, entry);
        },

        error: (message: string, data?: any, options?: { tags?: string[], metrics?: Record<string, number> }) => {
            const entry = createLogEntry('error', message, data, options);
            logToFile(`state/${module}.log`, entry);
            updateHealthStatus('degraded', { module, message, timestamp: entry.timestamp });
        },

        critical: (message: string, data?: any, options?: { tags?: string[], metrics?: Record<string, number> }) => {
            const entry = createLogEntry('critical', message, data, options);
            logToFile(`state/${module}.log`, entry);
            updateHealthStatus('unhealthy', { module, message, timestamp: entry.timestamp });
        },

        trackTask: (taskId: string, status: 'started' | 'in-progress' | 'completed' | 'failed', details?: any) => {
            const entry = createLogEntry('info', `Task ${taskId} ${status}`, {
                taskId,
                status,
                details,
                progress: details?.progress
            }, { tags: ['task', status] });

            logToFile(`tasks/${taskId}.log`, entry);

            // Also log task status to a consolidated tasks file by date
            const dateStr = new Date().toISOString().split('T')[0];
            logToFile(`tasks/daily/${dateStr}.log`, entry);
        },

        trackTaskProgress: (
            taskId: string,
            progress: number,
            status: 'in-progress' | 'completed' | 'failed' = 'in-progress',
            details?: any
        ) => {
            const entry = createLogEntry('info', `Task ${taskId} progress: ${progress}%`, {
                taskId,
                status,
                progress,
                details
            }, {
                tags: ['task', 'progress', status],
                metrics: { progress }
            });

            logToFile(`tasks/${taskId}.log`, entry);
        },

        persistData: (key: string, data: any, tags?: string[]) => {
            const entry = createLogEntry('info', `Persisting data for ${key}`, data, {
                tags: ['persistence', ...(tags || [])]
            });

            // Write to JSON file in persistence folder
            fs.writeFileSync(
                path.join(process.cwd(), 'memlog', 'persistence', `${key}.json`),
                JSON.stringify(data, null, 2)
            );

            // Also log the persistence operation
            logToFile(`persistence/${key}.log`, entry);
        },

        logStateChange: (component: string, prevState: any, nextState: any, action?: string) => {
            const entry = createLogEntry('info', `State change in ${component}${action ? ` due to ${action}` : ''}`, {
                component,
                action,
                prevState,
                nextState,
                diff: generateStateDiff(prevState, nextState)
            }, { tags: ['state-change', component] });

            logToFile(`state/changes/${component}.log`, entry);
        },

        logMetric: (metricName: string, value: number, unit?: string, context?: any) => {
            const entry = createLogEntry('info', `Metric ${metricName}: ${value}${unit ? ` ${unit}` : ''}`, {
                metricName,
                value,
                unit,
                context
            }, {
                tags: ['metric', metricName],
                metrics: { [metricName]: value }
            });

            const dateStr = new Date().toISOString().split('T')[0];
            logToFile(`metrics/${dateStr}.log`, entry);
        },

        logAudit: (action: string, user: string, resource: string, success: boolean, details?: any) => {
            const entry = createLogEntry(success ? 'info' : 'warn',
                `Audit: ${user} ${success ? 'successfully' : 'failed to'} ${action} ${resource}`,
                {
                    action,
                    user,
                    resource,
                    success,
                    details
                },
                { tags: ['audit', action, success ? 'success' : 'failure'] }
            );

            const dateStr = new Date().toISOString().split('T')[0];
            logToFile(`audit/${dateStr}.log`, entry);
        },

        // Get the correlation ID being used by this logger
        getCorrelationId: () => loggerCorrelationId,

        // Create a child logger with the same correlation ID
        createChildLogger: (childModule: string) => {
            return createLogger(`${module}.${childModule}`, loggerCorrelationId);
        }
    };
};

// Helper function to generate a diff between two state objects
const generateStateDiff = (prevState: any, nextState: any): Record<string, { previous: any, current: any }> => {
    if (!prevState || !nextState) {
        return {
            _complete: {
                previous: prevState,
                current: nextState
            }
        };
    }

    const diff: Record<string, { previous: any, current: any }> = {};

    // Get all keys from both objects
    const allKeys = new Set([
        ...Object.keys(prevState),
        ...Object.keys(nextState)
    ]);

    for (const key of allKeys) {
        // If value changed or key doesn't exist in one of the states
        if (prevState[key] !== nextState[key]) {
            diff[key] = {
                previous: prevState[key],
                current: nextState[key]
            };
        }
    }

    return diff;
};

// Export utility functions
export const memlogUtils = {
    createMemlogDirectories,
    verifyMemlogStructure,
    initMemlog,
    configureLogging,
    queryLogs,
    subscribeToAlerts,
    updateHealthStatus
};
