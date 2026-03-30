import { logState } from '../../memlog/state/logState';
import { trackTask } from '../../memlog/tasks/trackTask';
import { storeData } from '../../memlog/persistence/storeData';
import { maintainChangelog } from '../../memlog/changelogs/maintainChangelog';

/**
 * Universal Knowledge Store (UKS)
 * 
 * A graph-based knowledge representation system that supports:
 * - Adding and retrieving facts
 * - Inheritance and relationships between entities
 * - Querying with support for logical constraints
 * - Persistence and versioning
 */
export class UniversalKnowledgeStore {
    private nodes: Map<string, Node> = new Map();
    private relationships: Map<string, Relationship[]> = new Map();

    constructor() {
        trackTask({
            type: 'uks_initialization',
            timestamp: new Date().toISOString()
        });

        logState({
            operation: 'uks_initialization',
            timestamp: new Date().toISOString(),
            result: 'success'
        });
    }

    /**
     * Add a node to the knowledge store
     */
    add_node(id: string, type: string = 'entity', attributes: Record<string, any> = {}): Node {
        trackTask({
            type: 'uks_add_node',
            timestamp: new Date().toISOString(),
            nodeId: id,
            nodeType: type
        });

        try {
            const node: Node = {
                id,
                type,
                attributes,
                created: new Date().toISOString(),
                updated: new Date().toISOString()
            };

            this.nodes.set(id, node);

            logState({
                operation: 'uks_add_node',
                timestamp: new Date().toISOString(),
                result: 'success',
                nodeId: id
            });

            maintainChangelog({
                type: 'node_added',
                timestamp: new Date().toISOString(),
                data: { nodeId: id, nodeType: type }
            });

            return node;
        } catch (error) {
            logState({
                operation: 'uks_add_node',
                timestamp: new Date().toISOString(),
                result: 'error',
                error: error.message
            });

            throw new Error(`Failed to add node: ${error.message}`);
        }
    }

    /**
     * Add a fact about an entity
     */
    add_fact(subject: string, predicate: string, object: any): boolean {
        trackTask({
            type: 'uks_add_fact',
            timestamp: new Date().toISOString(),
            subject,
            predicate,
            object
        });

        try {
            // Create subject node if it doesn't exist
            if (!this.nodes.has(subject)) {
                this.add_node(subject);
            }

            const node = this.nodes.get(subject);
            node.attributes[predicate] = object;
            node.updated = new Date().toISOString();

            logState({
                operation: 'uks_add_fact',
                timestamp: new Date().toISOString(),
                result: 'success',
                fact: { subject, predicate, object }
            });

            maintainChangelog({
                type: 'fact_added',
                timestamp: new Date().toISOString(),
                data: { subject, predicate, object }
            });

            return true;
        } catch (error) {
            logState({
                operation: 'uks_add_fact',
                timestamp: new Date().toISOString(),
                result: 'error',
                error: error.message
            });

            throw new Error(`Failed to add fact: ${error.message}`);
        }
    }

    /**
     * Add a relationship between two entities
     */
    add_relationship(from: string, type: string, to: string, attributes: Record<string, any> = {}): boolean {
        trackTask({
            type: 'uks_add_relationship',
            timestamp: new Date().toISOString(),
            from,
            type,
            to
        });

        try {
            // Create nodes if they don't exist
            if (!this.nodes.has(from)) {
                this.add_node(from);
            }

            if (!this.nodes.has(to)) {
                this.add_node(to);
            }

            const relationship: Relationship = {
                id: `${from}_${type}_${to}_${Date.now()}`,
                from,
                to,
                type,
                attributes,
                created: new Date().toISOString()
            };

            if (!this.relationships.has(from)) {
                this.relationships.set(from, []);
            }

            this.relationships.get(from).push(relationship);

            logState({
                operation: 'uks_add_relationship',
                timestamp: new Date().toISOString(),
                result: 'success',
                relationship: { from, type, to }
            });

            maintainChangelog({
                type: 'relationship_added',
                timestamp: new Date().toISOString(),
                data: { from, type, to }
            });

            return true;
        } catch (error) {
            logState({
                operation: 'uks_add_relationship',
                timestamp: new Date().toISOString(),
                result: 'error',
                error: error.message
            });

            throw new Error(`Failed to add relationship: ${error.message}`);
        }
    }

    /**
     * Get a node by ID
     */
    get_node(id: string): Node | null {
        try {
            return this.nodes.get(id) || null;
        } catch (error) {
            logState({
                operation: 'uks_get_node',
                timestamp: new Date().toISOString(),
                result: 'error',
                error: error.message
            });

            throw new Error(`Failed to get node: ${error.message}`);
        }
    }

    /**
     * Query for nodes that match certain criteria
     */
    query(criteria: {
        attributes?: Record<string, any>,
        type?: string,
        relationshipFrom?: string,
        relationshipType?: string,
        limit?: number
    }): Node[] {
        trackTask({
            type: 'uks_query',
            timestamp: new Date().toISOString(),
            criteria
        });

        try {
            let results: Node[] = [];

            for (const node of this.nodes.values()) {
                let match = true;

                // Match node type if specified
                if (criteria.type && node.type !== criteria.type) {
                    match = false;
                }

                // Match attributes if specified
                if (match && criteria.attributes) {
                    for (const [key, value] of Object.entries(criteria.attributes)) {
                        if (node.attributes[key] !== value) {
                            match = false;
                            break;
                        }
                    }
                }

                if (match) {
                    results.push(node);
                }
            }

            // Filter by relationship if needed
            if (criteria.relationshipFrom || criteria.relationshipType) {
                results = results.filter(node => {
                    const relationships = this.relationships.get(criteria.relationshipFrom) || [];
                    return relationships.some(rel =>
                        rel.to === node.id &&
                        (!criteria.relationshipType || rel.type === criteria.relationshipType)
                    );
                });
            }

            // Apply limit if needed
            if (criteria.limit && results.length > criteria.limit) {
                results = results.slice(0, criteria.limit);
            }

            logState({
                operation: 'uks_query',
                timestamp: new Date().toISOString(),
                result: 'success',
                count: results.length
            });

            return results;
        } catch (error) {
            logState({
                operation: 'uks_query',
                timestamp: new Date().toISOString(),
                result: 'error',
                error: error.message
            });

            throw new Error(`Failed to query knowledge store: ${error.message}`);
        }
    }

    /**
     * Persist the current state of the knowledge store
     */
    persist(): boolean {
        trackTask({
            type: 'uks_persist',
            timestamp: new Date().toISOString()
        });

        try {
            const data = {
                nodes: Array.from(this.nodes.entries()),
                relationships: Array.from(this.relationships.entries()),
                timestamp: new Date().toISOString()
            };

            storeData({
                type: 'uks_snapshot',
                timestamp: new Date().toISOString(),
                data
            });

            logState({
                operation: 'uks_persist',
                timestamp: new Date().toISOString(),
                result: 'success'
            });

            return true;
        } catch (error) {
            logState({
                operation: 'uks_persist',
                timestamp: new Date().toISOString(),
                result: 'error',
                error: error.message
            });

            throw new Error(`Failed to persist knowledge store: ${error.message}`);
        }
    }
}

interface Node {
    id: string;
    type: string;
    attributes: Record<string, any>;
    created: string;
    updated: string;
}

interface Relationship {
    id: string;
    from: string;
    to: string;
    type: string;
    attributes: Record<string, any>;
    created: string;
}
