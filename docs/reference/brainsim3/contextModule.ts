/**
 * BrainSimIII Context Module
 * Provides contextual awareness and state tracking for BrainSimIII
 */
import logState from '../../../memlog/state/logState';
import trackTask from '../../../memlog/tasks/trackTask';

/**
 * Context object that holds current state information
 */
interface Context {
    id: string;
    sessionId: string;
    startTime: string;
    currentTopic?: string;
    history: HistoryItem[];
    entities: Map<string, ContextEntity>;
    activeEntities: string[];
    metadata: Record<string, any>;
}

interface HistoryItem {
    timestamp: string;
    action: string;
    data: any;
}

interface ContextEntity {
    id: string;
    type: string;
    importance: number;
    firstMentioned: string;
    lastMentioned: string;
    attributes: Record<string, any>;
}

/**
 * Context Module for BrainSimIII
 */
const contextModule = {
    activeContext: null as Context | null,
    contextHistory: [] as Context[],

    /**
     * Initialize a new context
     */
    createContext: function (sessionId: string, initialData: any = {}): Context {
        const taskId = `create-context-${sessionId}`;
        trackTask({
            id: taskId,
            status: 'in-progress',
            startTime: new Date().toISOString()
        });

        try {
            const now = new Date().toISOString();
            const contextId = `ctx-${now}-${Math.floor(Math.random() * 10000)}`;

            const context: Context = {
                id: contextId,
                sessionId,
                startTime: now,
                history: [],
                entities: new Map(),
                activeEntities: [],
                metadata: initialData.metadata || {}
            };

            // Add initial data to history if available
            if (initialData) {
                context.history.push({
                    timestamp: now,
                    action: 'initialize',
                    data: initialData
                });
            }

            // Store as active context
            this.activeContext = context;

            // Log state
            logState({
                type: 'context-created',
                contextId,
                sessionId,
                timestamp: now
            });

            trackTask({
                id: taskId,
                status: 'completed',
                endTime: new Date().toISOString()
            });

            return context;
        } catch (error: any) {
            logState({
                type: 'context-error',
                operation: 'createContext',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            trackTask({
                id: taskId,
                status: 'failed',
                error: error.message,
                endTime: new Date().toISOString()
            });

            throw error;
        }
    },

    /**
     * Add an entity to the current context
     */
    addEntity: function (entity: Partial<ContextEntity>): string {
        if (!this.activeContext) {
            throw new Error('No active context available');
        }

        try {
            const now = new Date().toISOString();
            const entityId = entity.id || `entity-${now}-${Math.floor(Math.random() * 10000)}`;

            // Create entity if it doesn't exist
            if (!this.activeContext.entities.has(entityId)) {
                this.activeContext.entities.set(entityId, {
                    id: entityId,
                    type: entity.type || 'generic',
                    importance: entity.importance || 0.5,
                    firstMentioned: now,
                    lastMentioned: now,
                    attributes: entity.attributes || {}
                });

                // Add to active entities
                this.activeContext.activeEntities.push(entityId);
            } else {
                // Update existing entity
                const existingEntity = this.activeContext.entities.get(entityId);
                if (existingEntity) {
                    existingEntity.lastMentioned = now;
                    existingEntity.importance = entity.importance || existingEntity.importance;

                    if (entity.attributes) {
                        existingEntity.attributes = {
                            ...existingEntity.attributes,
                            ...entity.attributes
                        };
                    }
                }
            }

            // Log state change
            logState({
                type: 'context-entity-added',
                contextId: this.activeContext.id,
                entityId,
                timestamp: now
            });

            return entityId;
        } catch (error: any) {
            logState({
                type: 'context-error',
                operation: 'addEntity',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            throw error;
        }
    },

    /**
     * Update the context with new information
     */
    updateContext: function (action: string, data: any): void {
        if (!this.activeContext) {
            throw new Error('No active context available');
        }

        try {
            const now = new Date().toISOString();

            // Add to history
            this.activeContext.history.push({
                timestamp: now,
                action,
                data
            });

            // Update topic if provided
            if (data.topic) {
                this.activeContext.currentTopic = data.topic;
            }

            // Update metadata if provided
            if (data.metadata) {
                this.activeContext.metadata = {
                    ...this.activeContext.metadata,
                    ...data.metadata
                };
            }

            // Log state change
            logState({
                type: 'context-updated',
                contextId: this.activeContext.id,
                action,
                timestamp: now
            });
        } catch (error: any) {
            logState({
                type: 'context-error',
                operation: 'updateContext',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            throw error;
        }
    },

    /**
     * Get the most relevant entities based on recency and importance
     */
    getRelevantEntities: function (limit: number = 5): ContextEntity[] {
        if (!this.activeContext) {
            throw new Error('No active context available');
        }

        try {
            // Calculate relevance score for each entity
            const entitiesWithScores: Array<{ entity: ContextEntity, score: number }> = [];

            const now = new Date();

            for (const entityId of this.activeContext.activeEntities) {
                const entity = this.activeContext.entities.get(entityId);

                if (entity) {
                    // Calculate recency (higher is more recent)
                    const lastMentionedDate = new Date(entity.lastMentioned);
                    const timeDiff = (now.getTime() - lastMentionedDate.getTime()) / 1000; // seconds
                    const recency = Math.max(0, 1 - (timeDiff / (60 * 60 * 24))); // Decay over 24 hours

                    // Calculate relevance score based on importance and recency
                    const score = entity.importance * 0.6 + recency * 0.4;

                    entitiesWithScores.push({ entity, score });
                }
            }

            // Sort by score and take the top entities
            return entitiesWithScores
                .sort((a, b) => b.score - a.score)
                .slice(0, limit)
                .map(item => item.entity);
        } catch (error: any) {
            logState({
                type: 'context-error',
                operation: 'getRelevantEntities',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            throw error;
        }
    },

    /**
     * Save the current context to history and start a new one
     */
    archiveContext: function (): string {
        if (!this.activeContext) {
            throw new Error('No active context available');
        }

        try {
            const contextId = this.activeContext.id;

            // Add to history
            this.contextHistory.push(this.activeContext);

            // Create new context with same session ID
            this.createContext(this.activeContext.sessionId, {
                previousContextId: contextId,
                metadata: {
                    previousTopic: this.activeContext.currentTopic
                }
            });

            logState({
                type: 'context-archived',
                contextId,
                timestamp: new Date().toISOString()
            });

            return contextId;
        } catch (error: any) {
            logState({
                type: 'context-error',
                operation: 'archiveContext',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            throw error;
        }
    }
};

export default contextModule;
