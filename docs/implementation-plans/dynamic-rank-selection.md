# Implementation Plan: Dynamic Rank Selection

## Overview
Dynamic Rank Selection automatically determines the optimal rank values for LoRA adaptation based on layer importance, model architecture, and available hardware resources. This eliminates manual trial-and-error while ensuring optimal memory-performance trade-offs.

## Implementation Roadmap

### Phase 1: Layer Analysis Framework (Estimated completion: May 20, 2025)

1. **Layer Sensitivity Measurement**
   - Implement gradient-based sensitivity analysis
   - Create eigenvalue analysis for weight matrices
   - Develop activation-based importance metrics
   - Add Fisher Information Matrix analysis

2. **Profiling Tools**
   - Implement layer-wise memory profiling
   - Create computation cost estimator
   - Add parameter influence analysis

### Phase 2: Rank Selection Algorithms (Estimated completion: May 28, 2025)

1. **Design Adaptive Rank Selector**
   ```python
   class RankSelector:
       def __init__(
           self,
           model: nn.Module,
           target_modules: Optional[List[str]] = None,
           memory_constraint: float = 4.0,  # GB
           min_rank: int = 2,
           max_rank: int = 64,
           importance_metric: str = "gradient",
           rank_allocation_strategy: str = "proportional"
       ):
           self.model = model
           self.target_modules = target_modules
           self.memory_constraint = memory_constraint
           self.min_rank = min_rank
           self.max_rank = max_rank
           self.importance_metric = importance_metric
           self.rank_allocation_strategy = rank_allocation_strategy
           
           # Find target layers
           self.target_layers = _find_layers(
               model, 
               target_modules=target_modules, 
               layer_type=nn.Linear
           )
           
       def compute_layer_importance(self, dataloader: Optional[torch.utils.data.DataLoader] = None):
           """Compute importance score for each layer based on the selected metric."""
           importance_scores = {}
           
           if self.importance_metric == "gradient":
               importance_scores = self._compute_gradient_importance(dataloader)
           elif self.importance_metric == "eigenvalue":
               importance_scores = self._compute_eigenvalue_importance()
           elif self.importance_metric == "activation":
               importance_scores = self._compute_activation_importance(dataloader)
           elif self.importance_metric == "fisher":
               importance_scores = self._compute_fisher_importance(dataloader)
           else:
               raise ValueError(f"Unknown importance metric: {self.importance_metric}")
               
           return importance_scores
           
       def _compute_gradient_importance(self, dataloader):
           """Compute importance based on gradient magnitude."""
           # ... gradient calculation implementation ...
           
       def _compute_eigenvalue_importance(self):
           """Compute importance based on eigenvalue distribution of weight matrices."""
           # ... eigenvalue analysis implementation ...
           
       def _compute_activation_importance(self, dataloader):
           """Compute importance based on activation patterns."""
           # ... activation analysis implementation ...
           
       def _compute_fisher_importance(self, dataloader):
           """Compute importance based on Fisher Information Matrix."""
           # ... FIM analysis implementation ...
           
       def allocate_ranks(self, importance_scores: Dict[str, float]):
           """Allocate ranks to layers based on their importance scores and memory constraints."""
           if self.rank_allocation_strategy == "proportional":
               return self._proportional_allocation(importance_scores)
           elif self.rank_allocation_strategy == "threshold":
               return self._threshold_allocation(importance_scores)
           elif self.rank_allocation_strategy == "binary":
               return self._binary_allocation(importance_scores)
           else:
               raise ValueError(f"Unknown allocation strategy: {self.rank_allocation_strategy}")
               
       def _proportional_allocation(self, importance_scores):
           """Allocate ranks proportionally to importance scores while respecting memory constraints."""
           # Normalize importance scores
           total_importance = sum(importance_scores.values())
           normalized_scores = {name: score/total_importance for name, score in importance_scores.items()}
           
           # Initial rank allocation proportional to importance
           initial_allocation = {
               name: max(self.min_rank, min(self.max_rank, int(score * self.max_rank * 2)))
               for name, score in normalized_scores.items()
           }
           
           # Estimate memory usage
           memory_usage = self._estimate_memory_usage(initial_allocation)
           
           # Adjust if over/under memory constraint
           scaling_factor = self.memory_constraint / memory_usage
           
           # Rescale ranks to fit memory constraint
           final_allocation = {
               name: max(self.min_rank, min(self.max_rank, int(rank * scaling_factor)))
               for name, rank in initial_allocation.items()
           }
           
           return final_allocation
           
       def _threshold_allocation(self, importance_scores):
           """Allocate ranks based on importance thresholds."""
           # ... threshold-based allocation implementation ...
           
       def _binary_allocation(self, importance_scores):
           """Allocate either min_rank or max_rank based on importance threshold."""
           # ... binary allocation implementation ...
           
       def _estimate_memory_usage(self, rank_allocation):
           """Estimate memory usage based on rank allocation."""
           total_memory = 0
           
           for name, layer in self.target_layers.items():
               rank = rank_allocation.get(name, self.min_rank)
               
               # Memory for LoRA weights: A matrix (in_features * rank) + B matrix (rank * out_features)
               in_features = layer.in_features
               out_features = layer.out_features
               
               # Memory in bytes (assuming float32)
               param_memory = (in_features * rank + rank * out_features) * 4
               
               # Gradient memory (only for training)
               gradient_memory = param_memory
               
               # Optimizer state memory (assuming Adam with 2 states per parameter)
               optimizer_memory = param_memory * 2
               
               layer_memory = param_memory + gradient_memory + optimizer_memory
               total_memory += layer_memory
               
           # Convert to GB
           total_memory_gb = total_memory / (1024 ** 3)
           return total_memory_gb
           
       def get_optimal_ranks(self, dataloader: Optional[torch.utils.data.DataLoader] = None):
           """Get optimal rank allocation based on importance and memory constraints."""
           # Compute layer importance
           importance_scores = self.compute_layer_importance(dataloader)
           
           # Allocate ranks based on importance
           rank_allocation = self.allocate_ranks(importance_scores)
           
           return rank_allocation
   ```

2. **Create Dynamic LoRA Configuration**
   ```python
   class DynamicLoRAConfig(LoRAConfig):
       def __init__(
           self,
           # Base LoRA parameters
           alpha: float = 16.0,
           dropout_p: float = 0.0,
           target_modules: Optional[List[str]] = None,
           use_bias: bool = False,
           module_filter: Optional[str] = None,
           # Dynamic rank parameters
           memory_constraint: float = 4.0,  # GB
           min_rank: int = 2,
           max_rank: int = 64,
           importance_metric: str = "gradient",
           rank_allocation_strategy: str = "proportional",
           # Pre-computed ranks (if available)
           rank_allocation: Optional[Dict[str, int]] = None
       ):
           # Initialize with a placeholder rank (will be overridden per layer)
           super().__init__(
               rank=min_rank,  # This is just a placeholder
               alpha=alpha,
               dropout_p=dropout_p,
               target_modules=target_modules,
               use_bias=use_bias,
               module_filter=module_filter
           )
           
           # Dynamic rank parameters
           self.memory_constraint = memory_constraint
           self.min_rank = min_rank
           self.max_rank = max_rank
           self.importance_metric = importance_metric
           self.rank_allocation_strategy = rank_allocation_strategy
           self.rank_allocation = rank_allocation or {}
   ```

### Phase 3: Dynamic LoRA Model Implementation (Estimated completion: June 8, 2025)

1. **Create DynamicLoRAModel Class**
   ```python
   class DynamicLoRAModel(LoRAModel):
       def __init__(
           self,
           base_model: nn.Module,
           config: DynamicLoRAConfig,
           dataloader: Optional[torch.utils.data.DataLoader] = None
       ):
           self.config = config
           self.base_model = base_model
           
           # Compute optimal ranks if not provided
           if not self.config.rank_allocation:
               self._determine_optimal_ranks(dataloader)
               
           # Initialize with parent constructor (now that ranks are determined)
           super().__init__(base_model, config)
           
       def _determine_optimal_ranks(self, dataloader):
           """Determine optimal ranks for each layer."""
           rank_selector = RankSelector(
               model=self.base_model,
               target_modules=self.config.target_modules,
               memory_constraint=self.config.memory_constraint,
               min_rank=self.config.min_rank,
               max_rank=self.config.max_rank,
               importance_metric=self.config.importance_metric,
               rank_allocation_strategy=self.config.rank_allocation_strategy
           )
           
           self.config.rank_allocation = rank_selector.get_optimal_ranks(dataloader)
           
       def _apply_lora_layers(self):
           """Apply LoRA with dynamically determined ranks for each layer."""
           # Find target layers
           target_layers = _find_layers(
               self.base_model,
               target_modules=self.config.target_modules,
               layer_type=nn.Linear
           )
           
           # Apply module filter if specified
           if self.config.module_filter is not None:
               module_filter_pattern = re.compile(self.config.module_filter)
               target_layers = {
                   name: module for name, module in target_layers.items()
                   if module_filter_pattern.search(name)
               }
           
           # Log info on target layers
           logger.info(f"Applying Dynamic LoRA to {len(target_layers)} layers")
           
           # Replace each target layer with a LoRA layer using the allocated rank
           for name, layer in target_layers.items():
               # Get the dynamically determined rank for this layer
               rank = self.config.rank_allocation.get(name, self.config.min_rank)
               
               # Create LoRA wrapper for this layer with the specific rank
               lora_layer = LoRALayer(
                   base_layer=layer,
                   rank=rank,
                   alpha=self.config.alpha,
                   dropout_p=self.config.dropout_p,
                   use_bias=self.config.use_bias
               )
               
               # Find the parent module and name of this layer
               path_parts = name.split('.')
               parent_name = '.'.join(path_parts[:-1])
               child_name = path_parts[-1]
               
               # Replace the layer (same as in parent class)
               # ...existing layer replacement code...
               
               # Store reference to lora layer
               self.lora_layers[name] = lora_layer
   ```

2. **Utility Function**
   ```python
   def apply_dynamic_lora(
       model: nn.Module,
       alpha: int = 16,
       target_modules: Optional[List[str]] = None,
       memory_constraint: float = 4.0,  # GB
       min_rank: int = 2,
       max_rank: int = 64,
       importance_metric: str = "gradient",
       dataloader: Optional[torch.utils.data.DataLoader] = None
   ) -> DynamicLoRAModel:
       """
       Apply Dynamic LoRA with automatically determined ranks.
       
       Args:
           model: Model to apply LoRA to
           alpha: Scaling factor for LoRA
           target_modules: List of module types to apply LoRA to
           memory_constraint: Maximum memory in GB to use for LoRA parameters
           min_rank: Minimum allowed rank per layer
           max_rank: Maximum allowed rank per layer
           importance_metric: Method to determine layer importance
           dataloader: Optional dataloader for computing importance metrics
           
       Returns:
           Model wrapped with Dynamic LoRA
       """
       config = DynamicLoRAConfig(
           alpha=alpha,
           target_modules=target_modules,
           memory_constraint=memory_constraint,
           min_rank=min_rank,
           max_rank=max_rank,
           importance_metric=importance_metric
       )
       
       return DynamicLoRAModel(model, config, dataloader)
   ```

### Phase 4: Integration and Visualization (Estimated completion: June 15, 2025)

1. **Web Interface Integration**
   - Add dynamic rank configuration to interactive UI
   - Implement memory constraint slider
   - Create importance metric selection
   - Add visualization of rank allocation

2. **Visualization Tools**
   - Create rank distribution visualization
   - Implement importance score heatmap
   - Add memory usage breakdown by layer

## Testing Strategy

1. **Unit Tests**
   - Test importance calculation methods
   - Verify rank allocation algorithms
   - Test memory usage estimation

2. **Integration Tests**
   - Test end-to-end rank determination
   - Verify memory constraint compliance
   - Test with various model architectures

3. **Performance Benchmarks**
   - Compare dynamic vs. static rank allocation
   - Measure quality-vs-memory trade-offs
   - Test adaptation quality across tasks

## Memory Impact

Dynamic Rank Selection optimizes memory usage by:
- Allocating higher ranks to important layers
- Reducing ranks in less critical components
- Automatically adapting to memory constraints

Expected memory efficiency improvement of 15-30% compared to uniform rank allocation with equivalent quality.

## Documentation Updates

- Add Dynamic Rank Selection section to implementation guide
- Document importance metrics and their use cases
- Provide examples of rank allocation strategies
- Create visualization guides for understanding layer importance
