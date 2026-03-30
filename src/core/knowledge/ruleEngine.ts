/**
 * Rule Engine for Universal Knowledge Store
 * Provides dynamic rule-based reasoning capabilities
 */
import logState from '../../memlog/state/logState';
import trackTask from '../../memlog/tasks/trackTask';
import knowledgeStore from './uks';

// Define rule types and interfaces
interface Condition {
    type: 'attribute' | 'relationship' | 'existence';
    subject?: string;
    predicate?: string;
    object?: any;
    operator?: 'equals' | 'notEquals' | 'contains' | 'greaterThan' | 'lessThan';
}

interface Action {
    type: 'create' | 'update' | 'delete';
    target: 'node' | 'relationship';
    data: any;
}

interface Rule {
    id: string;
    name: string;
    description: string;
    conditions: Condition[];
    actions: Action[];
    priority: number;
    isActive: boolean;
}

/**
 * Rule Engine for applying rules to the knowledge store
 */
const ruleEngine = {
    rules: new Map<string, Rule>(),

    /**
     * Add a new rule to the engine
     */
    addRule: function (rule: Rule): string {
        try {
            const taskId = `add-rule-${rule.id}`;
            trackTask({
                id: taskId,
                status: 'in-progress',
                startTime: new Date().toISOString()
            });

            // Validate rule structure
            if (!rule.id || !rule.conditions || !rule.actions) {
                throw new Error('Invalid rule: missing required properties');
            }

            this.rules.set(rule.id, rule);

            logState({
                type: 'rule-added',
                ruleId: rule.id,
                timestamp: new Date().toISOString()
            });

            trackTask({
                id: taskId,
                status: 'completed',
                endTime: new Date().toISOString()
            });

            return rule.id;
        } catch (error: any) {
            logState({
                type: 'rule-error',
                operation: 'addRule',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            throw error;
        }
    },

    /**
     * Check if conditions are met for a given rule
     */
    evaluateConditions: function (conditions: Condition[]): boolean {
        try {
            return conditions.every(condition => {
                switch (condition.type) {
                    case 'attribute': {
                        // Check if node has attribute with specific value
                        if (!condition.subject || !condition.predicate) return false;

                        try {
                            const node = knowledgeStore.getNode(condition.subject);

                            if (!node || !condition.operator) return false;

                            const attributeValue = node.attributes[condition.predicate];

                            switch (condition.operator) {
                                case 'equals': return attributeValue === condition.object;
                                case 'notEquals': return attributeValue !== condition.object;
                                case 'contains':
                                    return Array.isArray(attributeValue)
                                        ? attributeValue.includes(condition.object)
                                        : String(attributeValue).includes(String(condition.object));
                                case 'greaterThan': return attributeValue > condition.object;
                                case 'lessThan': return attributeValue < condition.object;
                                default: return false;
                            }
                        } catch (error) {
                            return false;
                        }
                    }

                    case 'relationship': {
                        // Check if specific relationship exists
                        if (!condition.subject || !condition.predicate) return false;

                        const relationships = knowledgeStore.relationships.get(condition.subject) || [];
                        return relationships.some(rel =>
                            rel.type === condition.predicate &&
                            (!condition.object || rel.to === condition.object)
                        );
                    }

                    case 'existence': {
                        // Check if node exists
                        if (!condition.subject) return false;
                        return knowledgeStore.nodes.has(condition.subject);
                    }

                    default:
                        return false;
                }
            });
        } catch (error: any) {
            logState({
                type: 'rule-error',
                operation: 'evaluateConditions',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            return false;
        }
    },

    /**
     * Execute actions for a rule
     */
    executeActions: function (actions: Action[]): boolean {
        try {
            return actions.every(action => {
                switch (action.type) {
                    case 'create': {
                        if (action.target === 'node') {
                            knowledgeStore.addNode(action.data);
                            return true;
                        } else if (action.target === 'relationship') {
                            const { from, to, type, attributes } = action.data;
                            knowledgeStore.addRelationship(from, to, type, attributes);
                            return true;
                        }
                        return false;
                    }

                    case 'update': {
                        if (action.target === 'node' && action.data.id) {
                            try {
                                const node = knowledgeStore.getNode(action.data.id);

                                // Update node attributes
                                Object.entries(action.data.attributes || {}).forEach(([key, value]) => {
                                    knowledgeStore.addFact(action.data.id, key, value);
                                });

                                return true;
                            } catch (error) {
                                return false;
                            }
                        }
                        return false;
                    }

                    case 'delete': {
                        // Implement delete actions when needed
                        return false;
                    }

                    default:
                        return false;
                }
            });
        } catch (error: any) {
            logState({
                type: 'rule-error',
                operation: 'executeActions',
                error: error.message,
                timestamp: new Date().toISOString()
            });

            return false;
        }
    },

    /**
     * Apply all active rules to the knowledge store
     */
    applyRules: function (): { applied: string[], failed: string[] } {
        const taskId = `apply-rules-${Date.now()}`;
        trackTask({
            id: taskId,
            status: 'in-progress',
            startTime: new Date().toISOString()
        });

        const result = { applied: [] as string[], failed: [] as string[] };

        try {
            // Sort rules by priority (higher first)
            const sortedRules = Array.from(this.rules.values())
                .filter(rule => rule.isActive)
                .sort((a, b) => b.priority - a.priority);

            // Apply each rule
            for (const rule of sortedRules) {
                try {
                    const conditionsMet = this.evaluateConditions(rule.conditions);

                    if (conditionsMet) {
                        const actionsExecuted = this.executeActions(rule.actions);

                        if (actionsExecuted) {
                            result.applied.push(rule.id);

                            logState({
                                type: 'rule-applied',
                                ruleId: rule.id,
                                timestamp: new Date().toISOString()
                            });
                        } else {
                            result.failed.push(rule.id);
                        }
                    }
                } catch (error) {
                    result.failed.push(rule.id);

                    logState({
                        type: 'rule-error',
                        operation: 'applyRule',
                        ruleId: rule.id,
                        timestamp: new Date().toISOString()
                    });
                }
            }

            trackTask({
                id: taskId,
                status: 'completed',
                applied: result.applied.length,
                failed: result.failed.length,
                endTime: new Date().toISOString()
            });

            return result;
        } catch (error: any) {
            logState({
                type: 'rule-error',
                operation: 'applyRules',
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
    }
};

export default ruleEngine;
