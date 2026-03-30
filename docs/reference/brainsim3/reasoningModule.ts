/**
 * BrainSimIII Reasoning Module
 * Provides advanced reasoning capabilities with uncertainty quantification
 */
import logState from '../../../memlog/state/logState';
import trackTask from '../../../memlog/tasks/trackTask';
import knowledgeStore from '../../knowledge/uks';
import ruleEngine from '../../knowledge/ruleEngine';
import contextModule from './contextModule';

/**
 * Reasoning task types
 */
type ReasoningTask =
    | { type: 'deduction', premises: string[], conclusion: string }
    | { type: 'induction', observations: string[], hypothesis: string }
    | { type: 'abduction', observation: string, explanations: string[] }
    | { type: 'analogy', source: string, target: string, mapping: Record<string, string> }
    | { type: 'counterfactual', premise: string, alternative: string, consequence: string };

/**
 * Reasoning result with uncertainty quantification
 */
interface ReasoningResult {
    id: string;
    taskType: string;
    result: boolean | string | string[];
    confidence: number;
    uncertainty: {
        epistemic: number;  // Due to missing knowledge
        aleatory: number;   // Due to inherent randomness
        total: number;
    };
    explanation: string[];
    timestamp: string;
}

/**
 * Reasoning Module for BrainSimIII
 */
const reasoningModule = {
    /**
     * Perform reasoning with uncertainty quantification
     */
    reason: function (task: ReasoningTask): ReasoningResult {
        const taskId = `reasoning-${Date.now()}`;
        trackTask({
            id: taskId,
            status: 'in-progress',
            startTime: new Date().toISOString(),
            taskType: task.type
        });

        try {
            let result: ReasoningResult;

            switch (task.type) {
                case 'deduction':
                    result = this.performDeduction(task, taskId);
                    break;
                case 'induction':
                    result = this.performInduction(task, taskId);
                    break;
                case 'abduction':
                    result = this.performAbduction(task, taskId);
                    break;
                case 'analogy':
                    result = this.performAnalogy(task, taskId);
                    break;
                case 'counterfactual':
                    result = this.performCounterfactual(task, taskId);
                    break;
                default:
                    throw new Error(`Unsupported reasoning task type: ${(task as any).type}`);
            }

            // Log state
            logState({
                type: 'reasoning-completed',
                taskId,
                taskType: task.type,
                confidence: result.confidence,
                uncertainty: result.uncertainty,
                timestamp: new Date().toISOString()
            });

            // Track task completion
            trackTask({
                id: taskId,
                status: 'completed',
                result: result.result,
                confidence: result.confidence,
                endTime: new Date().toISOString()
            });

            // Update context if available
            if (contextModule.activeContext) {
                contextModule.updateContext('reasoning', {
                    taskType: task.type,
                    result: result.result,
                    confidence: result.confidence
                });
            }

            return result;
        } catch (error: any) {
            // Log error
            logState({
                type: 'reasoning-error',
                taskId,
                error: error.message,
                timestamp: new Date().toISOString()
            });

            // Track task failure
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
     * Perform deductive reasoning (from premises to conclusion)
     */
    performDeduction: function (task: { type: 'deduction', premises: string[], conclusion: string }, taskId: string): ReasoningResult {
        // Simple implementation - check if conclusion follows from premises
        // In a real system, this would use formal logic or theorem proving

        // Apply rules to knowledge store first
        ruleEngine.applyRules();

        // Check if premises exist in knowledge store
        const premisesFound = task.premises.filter(premise => {
            // Search for nodes containing the premise text
            const nodes = knowledgeStore.queryNodes({
                attributes: { text: premise }
            });

            return nodes.length > 0;
        });

        // Calculate confidence based on premises found
        const premisesConfidence = premisesFound.length / task.premises.length;

        // Look for conclusion in knowledge store
        const conclusionNodes = knowledgeStore.queryNodes({
            attributes: { text: task.conclusion }
        });

        // Calculate confidence for conclusion existence
        const conclusionConfidence = conclusionNodes.length > 0 ? 0.8 : 0.2;

        // Combined confidence
        const confidence = premisesConfidence * 0.7 + conclusionConfidence * 0.3;

        // Calculate uncertainty
        const epistemic = premisesFound.length < task.premises.length ? 0.5 : 0.1; // Higher if premises are missing
        const aleatory = 0.1; // Base randomness
        const totalUncertainty = Math.min(1.0, epistemic + aleatory);

        // Generate explanation
        const explanation = [
            `Found ${premisesFound.length} of ${task.premises.length} premises in knowledge store`,
            conclusionNodes.length > 0
                ? `Conclusion "${task.conclusion}" is supported by existing knowledge`
                : `Conclusion "${task.conclusion}" is not directly supported by existing knowledge`
        ];

        return {
            id: taskId,
            taskType: 'deduction',
            result: confidence > 0.6,
            confidence,
            uncertainty: {
                epistemic,
                aleatory,
                total: totalUncertainty
            },
            explanation,
            timestamp: new Date().toISOString()
        };
    },

    /**
     * Perform inductive reasoning (from observations to hypothesis)
     */
    performInduction: function (task: { type: 'induction', observations: string[], hypothesis: string }, taskId: string): ReasoningResult {
        // Apply rules to knowledge store first
        ruleEngine.applyRules();

        // Check observations against knowledge store
        const observationsFound = task.observations.filter(observation => {
            // Search for nodes containing the observation text
            const nodes = knowledgeStore.queryNodes({
                attributes: { text: observation }
            });

            return nodes.length > 0;
        });

        // Calculate observation coverage
        const observationConfidence = observationsFound.length / task.observations.length;

        // Check hypothesis against knowledge store
        const hypothesisNodes = knowledgeStore.queryNodes({
            attributes: { text: task.hypothesis }
        });

        // Look for similar hypotheses
        const similarNodes = knowledgeStore.queryNodes({
            nodeType: 'hypothesis'
        });

        // Calculate hypothesis plausibility
        const hypothesisPlausibility = hypothesisNodes.length > 0 ? 0.8 : 0.4;

        // Combined confidence (induction is generally less certain than deduction)
        const confidence = observationConfidence * 0.6 + hypothesisPlausibility * 0.2;

        // Calculate uncertainty (induction has higher uncertainty)
        const epistemic = 0.3; // Base epistemic uncertainty for induction
        const aleatory = 0.2;  // Base aleatory uncertainty for induction
        const totalUncertainty = Math.min(1.0, epistemic + aleatory);

        // Generate explanation
        const explanation = [
            `${observationsFound.length} of ${task.observations.length} observations matched existing knowledge`,
            `Hypothesis "${task.hypothesis}" ${hypothesisNodes.length > 0 ? 'has' : 'has no'} direct support in knowledge store`,
            `Found ${similarNodes.length} similar hypotheses in knowledge store`
        ];

        return {
            id: taskId,
            taskType: 'induction',
            result: confidence > 0.5,
            confidence,
            uncertainty: {
                epistemic,
                aleatory,
                total: totalUncertainty
            },
            explanation,
            timestamp: new Date().toISOString()
        };
    },

    /**
     * Perform abductive reasoning (from observation to best explanation)
     */
    performAbduction: function (task: { type: 'abduction', observation: string, explanations: string[] }, taskId: string): ReasoningResult {
        // Apply rules to knowledge store
        ruleEngine.applyRules();

        // Check if observation exists in knowledge store
        const observationNodes = knowledgeStore.queryNodes({
            attributes: { text: task.observation }
        });

        const observationConfidence = observationNodes.length > 0 ? 0.8 : 0.3;

        // Rank explanations
        const explanationsWithRanking = task.explanations.map(explanation => {
            // Look for nodes supporting this explanation
            const supportingNodes = knowledgeStore.queryNodes({
                attributes: { text: explanation }
            });

            const support = supportingNodes.length;
            // Calculate simplicity (fewer nodes is simpler)
            const simplicity = 1 / (1 + support);
            // Calculate coverage
            const coverage = support > 0 ? 0.8 : 0.2;

            // Combined score (higher is better)
            const score = coverage * 0.5 + simplicity * 0.3 + observationConfidence * 0.2;

            return { explanation, score, support };
        });

        // Sort by score (descending)
        explanationsWithRanking.sort((a, b) => b.score - a.score);

        // Best explanation is the first one
        const bestExplanation = explanationsWithRanking[0].explanation;

        // Calculate confidence based on score difference between top explanations
        let confidence = explanationsWithRanking[0].score;
        if (explanationsWithRanking.length > 1) {
            const scoreDifference = explanationsWithRanking[0].score - explanationsWithRanking[1].score;
            // Higher difference means more confidence
            confidence = Math.min(0.9, confidence + scoreDifference * 0.5);
        }

        // Calculate uncertainty
        const epistemic = 0.3; // Base epistemic uncertainty for abduction
        const aleatory = 0.3;  // Base aleatory uncertainty for abduction
        const totalUncertainty = Math.min(1.0, epistemic + aleatory);

        // Generate explanation
        const explanation = [
            `Evaluated ${task.explanations.length} possible explanations for "${task.observation}"`,
            `Best explanation: "${bestExplanation}" with score ${explanationsWithRanking[0].score.toFixed(2)}`,
            `Support from knowledge store: ${explanationsWithRanking[0].support} nodes`
        ];

        return {
            id: taskId,
            taskType: 'abduction',
            result: bestExplanation,
            confidence,
            uncertainty: {
                epistemic,
                aleatory,
                total: totalUncertainty
            },
            explanation,
            timestamp: new Date().toISOString()
        };
    },

    /**
     * Perform analogical reasoning (mapping source to target)
     */
    performAnalogy: function (task: { type: 'analogy', source: string, target: string, mapping: Record<string, string> }, taskId: string): ReasoningResult {
        // Apply rules to knowledge store
        ruleEngine.applyRules();

        // Find source and target in knowledge store
        const sourceNodes = knowledgeStore.queryNodes({
            attributes: { text: task.source }
        });

        const targetNodes = knowledgeStore.queryNodes({
            attributes: { text: task.target }
        });

        // Calculate confidence based on existence of source and target
        let confidence = 0;
        if (sourceNodes.length > 0 && targetNodes.length > 0) {
            confidence = 0.7;
        } else if (sourceNodes.length > 0 || targetNodes.length > 0) {
            confidence = 0.4;
        } else {
            confidence = 0.2;
        }

        // Verify mapping
        const validMappings = Object.entries(task.mapping).filter(([sourceAttr, targetAttr]) => {
            // Check if source attributes exist in knowledge
            if (sourceNodes.length > 0) {
                const hasSourceAttr = sourceNodes.some(node =>
                    node.attributes[sourceAttr] !== undefined
                );

                // Check if target attributes exist in knowledge
                if (targetNodes.length > 0) {
                    const hasTargetAttr = targetNodes.some(node =>
                        node.attributes[targetAttr] !== undefined
                    );

                    return hasSourceAttr && hasTargetAttr;
                }

                return hasSourceAttr;
            }

            return false;
        });

        // Adjust confidence based on valid mappings
        const mappingConfidence = validMappings.length / Object.keys(task.mapping).length;
        confidence = confidence * 0.5 + mappingConfidence * 0.5;

        // Calculate uncertainty
        const epistemic = 1 - (sourceNodes.length > 0 && targetNodes.length > 0 ? 0.6 : 0.2