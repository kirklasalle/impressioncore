# Implementation Plan: Sparsity Integration

## Overview
Sparsity Integration combines LoRA with weight pruning to further enhance memory efficiency and adaptation performance. By focusing adaptation on the most important weight subspaces, this approach delivers maximum impact with minimal parameter overhead.

## Implementation Roadmap

### Phase 1: Pruning Framework (Estimated completion: May 22, 2025)

1. **Weight Importance Analysis**
   - Implement magnitude-based pruning
   - Create gradient-based importance metrics
   - Add activation-based pruning
   - Implement second-order pruning methods

2. **Pruning Strategies**
   - Develop unstructured pruning for maximum sparsity
   - Implement N:M structured sparsity for hardware acceleration
   - Add block sparsity patterns
   - Create pruning schedules (gradual, one-shot)

### Phase 2: Sparse LoRA Components (Estimated completion: May 30, 2025)

1. **Create SparseLoRALayer Class**
   ```python
   class SparseLoRALayer(nn.Module):
       def __init__(
           self,
           base_layer: nn.Linear,
           rank: int = 8,
           alpha: float = 16.0,
           dropout_p: float = 0.0,
           use_bias: bool = False,
           sparsity: float = 0.5,
           pruning_method: str = "magnitude",
           structured_pattern: Optional[str] = None
       ):
           """
           Initialize Sparse LoRA adapter for a linear layer.
           
           Args:
               base_layer: Original linear layer to be adapted
               rank: Rank of low-rank decomposition
               alpha: Scaling factor for adaptation
               dropout_p: Dropout probability for regularization
               use_bias: Whether to include bias terms
               sparsity: Target sparsity ratio (0.0-1.0)
               pruning_method: Method to determine weight importance
               structured_pattern: Pattern for structured sparsity (None=unstructured)
           """
           super().__init__()
           
           # Save original layer
           self.base_layer = base_layer
           
           # LoRA hyperparameters
           self.rank = rank
           self.alpha = alpha
           self.scaling = alpha / rank
           
           # Sparsity parameters
           self.sparsity = sparsity
           self.pruning_method = pruning_method
           self.structured_pattern = structured_pattern
           
           # Extract base layer dimensions
           in_features, out_features = base_layer.in_features, base_layer.out_features
           
           # Create low-rank decomposition matrices
           self.lora_A = nn.Linear(in_features, rank, bias=False)
           self.lora_B = nn.Linear(rank, out_features, bias=use_bias)
           
           # Initialize with small non-zero weights
           nn.init.normal_(self.lora_A.weight, mean=0.0, std=0.02)
           nn.init.zeros_(self.lora_B.weight)
           if use_bias and self.lora_B.bias is not None:
               nn.init.zeros_(self.lora_B.bias)
           
           # Dropout for regularization
           self.dropout = nn.Dropout(dropout_p)
           
           # Create masks for sparse weights
           self.mask_A = torch.ones_like(self.lora_A.weight)
           self.mask_B = torch.ones_like(self.lora_B.weight)
           
           # Ensure base layer weights are frozen
           for param in base_layer.parameters():
               param.requires_grad = False
           
           # Pruning has not been applied yet
           self.is_pruned = False
       
       def forward(self, x: torch.Tensor) -> torch.Tensor:
           """Forward pass combining base layer with sparse LoRA adaptation."""
           # Base layer forward
           base_output = self.base_layer(x)
           
           # Apply masks during forward pass to maintain sparsity
           if self.is_pruned:
               # Sparse matrix operations
               A_weight = self.lora_A.weight * self.mask_A
               x_A = F.linear(x, A_weight)
               x_A = self.dropout(x_A)
               
               B_weight = self.lora_B.weight * self.mask_B
               lora_output = F.linear(x_A, B_weight, self.lora_B.bias)
           else:
               # Standard LoRA forward path
               lora_output = self.lora_B(self.dropout(self.lora_A(x)))
           
           # Combine with scaling factor
           return base_output + (lora_output * self.scaling)
       
       def _compute_weight_importance(self, weight, method="magnitude"):
           """Compute importance scores for weights."""
           if method == "magnitude":
               # Simple magnitude-based importance
               return torch.abs(weight)
           elif method == "movement":
               # Importance based on movement from initialization
               # Requires storing initial weights (not implemented here)
               return torch.abs(weight)
           elif method == "random":
               # Random importance (for baseline)
               return torch.rand_like(weight)
           else:
               raise ValueError(f"Unknown pruning method: {method}")
       
       def prune(self, sparsity=None, method=None):
           """
           Prune the LoRA matrices to the target sparsity.
           
           Args:
               sparsity: Target sparsity (0.0-1.0), uses self.sparsity if None
               method: Pruning method, uses self.pruning_method if None
           """
           sparsity = sparsity or self.sparsity
           method = method or self.pruning_method
           
           with torch.no_grad():
               # Compute importance scores
               importance_A = self._compute_weight_importance(self.lora_A.weight, method)
               importance_B = self._compute_weight_importance(self.lora_B.weight, method)
               
               if self.structured_pattern is None:
                   # Unstructured pruning
                   
                   # For A matrix
                   threshold_A = torch.quantile(importance_A.flatten(), sparsity)
                   self.mask_A = (importance_A > threshold_A).float()
                   
                   # For B matrix
                   threshold_B = torch.quantile(importance_B.flatten(), sparsity)
                   self.mask_B = (importance_B > threshold_B).float()
               
               elif self.structured_pattern == "2:4":
                   # 2:4 structured sparsity (keep 2 out of every 4 weights)
                   # Reshape to implement 2:4 pattern
                   
                   # For A matrix (example implementation - would need refinement)
                   original_shape_A = importance_A.shape
                   importance_A_reshaped = importance_A.reshape(-1, 4)
                   _, indices_A = torch.topk(importance_A_reshaped, 2, dim=1)
                   mask_A_reshaped = torch.zeros_like(importance_A_reshaped)
                   mask_A_reshaped.scatter_(1, indices_A, 1.0)
                   self.mask_A = mask_A_reshaped.reshape(original_shape_A)
                   
                   # For B matrix
                   original_shape_B = importance_B.shape
                   importance_B_reshaped = importance_B.reshape(-1, 4)
                   _, indices_B = torch.topk(importance_B_reshaped, 2, dim=1)
                   mask_B_reshaped = torch.zeros_like(importance_B_reshaped)
                   mask_B_reshaped.scatter_(1, indices_B, 1.0)
                   self.mask_B = mask_B_reshaped.reshape(original_shape_B)
               
               elif self.structured_pattern == "block":
                   # Block sparsity
                   # Implement block pruning logic
                   # ...
                   pass
               
               # Apply masks to zero out pruned weights
               self.lora_A.weight.data *= self.mask_A
               self.lora_B.weight.data *= self.mask_B
           
           self.is_pruned = True
           
           # Calculate and return achieved sparsity
           sparsity_A = 1.0 - (self.mask_A.sum() / self.mask_A.numel())
           sparsity_B = 1.0 - (self.mask_B.sum() / self.mask_B.numel())
           avg_sparsity = (sparsity_A + sparsity_B) / 2
           
           return {
               "sparsity_A": sparsity_A.item(),
               "sparsity_B": sparsity_B.item(),
               "avg_sparsity": avg_sparsity.item()
           }
       
       def get_sparse_delta_weights(self) -> torch.Tensor:
           """Get the sparse weight delta introduced by LoRA adaptation."""
           with torch.no_grad():
               # Apply masks to get sparse matrices
               A_sparse = self.lora_A.weight * self.mask_A
               B_sparse = self.lora_B.weight * self.mask_B
               
               # Calculate adaptation delta: (BA) * scaling
               delta = B_sparse @ A_sparse
               delta = delta * self.scaling
               
               return delta
       
       def merge_weights(self) -> nn.Linear:
           """Merge sparse LoRA weights with the base layer weights."""
           # Create a new linear layer to hold merged weights
           merged_layer = nn.Linear(
               self.base_layer.in_features, 
               self.base_layer.out_features,
               bias=True if self.base_layer.bias is not None else False,
               device=self.base_layer.weight.device,
               dtype=self.base_layer.weight.dtype
           )
           
           # Calculate merged weights: W + (BA) * scaling
           with torch.no_grad():
               # Get sparse delta weights
               delta = self.get_sparse_delta_weights()
               
               # Merge weights
               merged_weights = self.base_layer.weight + delta
               merged_layer.weight.copy_(merged_weights)
               
               # Copy bias if present
               if self.base_layer.bias is not None:
                   if hasattr(self.lora_B, 'bias') and self.lora_B.bias is not None:
                       merged_bias = self.base_layer.bias + self.lora_B.bias
                   else:
                       merged_bias = self.base_layer.bias
                   
                   merged_layer.bias.copy_(merged_bias)
           
           return merged_layer
   ```

2. **Design SparseLoRAConfig**
   ```python
   class SparseLoRAConfig:
       def __init__(
           self,
           rank: int = 8,
           alpha: float = 16.0,
           dropout_p: float = 0.0,
           target_modules: Optional[List[str]] = None,
           use_bias: bool = False,
           module_filter: Optional[str] = None,
           # Sparsity parameters
           sparsity: float = 0.5,
           pruning_method: str = "magnitude",
           structured_pattern: Optional[str] = None,
           pruning_schedule: Optional[str] = "one-shot",
           prune_initially: bool = True
       ):
           """
           Initialize sparse LoRA configuration.
           
           Args:
               rank: Rank of low-rank decomposition (smaller = fewer parameters)
               alpha: Scaling factor for adaptation
               dropout_p: Dropout probability for regularization
               target_modules: List of module types to apply LoRA to
               use_bias: Whether to include bias terms in LoRA
               module_filter: Regex pattern to filter module names
               sparsity: Target sparsity ratio (0.0-1.0)
               pruning_method: Method to determine weight importance
               structured_pattern: Pattern for structured sparsity
               pruning_schedule: Schedule for gradual pruning
               prune_initially: Whether to prune immediately on initialization
           """
           self.rank = rank
           self.alpha = alpha
           self.dropout_p = dropout_p
           self.target_modules = target_modules
           self.use_bias = use_bias
           self.module_filter = module_filter
           
           # Sparsity parameters
           self.sparsity = sparsity
           self.pruning_method = pruning_method
           self.structured_pattern = structured_pattern
           self.pruning_schedule = pruning_schedule
           self.prune_initially = prune_initially
           
           # Default target modules for attention layers if not provided
           if self.target_modules is None:
               self.target_modules = ["q_proj", "k_proj", "v_proj", "out_proj"]
   ```

### Phase 3: Implementation (Estimated completion: June 8, 2025)

1. **Create SparseLoRAModel Class**
   ```python
   class SparseLoRAModel(nn.Module):
       def __init__(
           self,
           base_model: nn.Module,
           config: SparseLoRAConfig
       ):
           """Initialize sparse LoRA model wrapper."""
           super().__init__()
           self.base_model = base_model
           self.config = config
           self.lora_layers = nn.ModuleDict()
           
           # Find and replace linear layers with sparse LoRA layers
           self._apply_sparse_lora_layers()
           
           # Freeze all parameters except LoRA parameters
           self._freeze_non_lora_params()
           
           # Prune initially if configured
           if self.config.prune_initially:
               self.prune_all_layers()
       
       def _apply_sparse_lora_layers(self):
           """Find and replace target layers with sparse LoRA layers."""
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
           
           # Log info
           logger.info(f"Applying sparse LoRA to {len(target_layers)} layers")
           
           # Replace each target layer with a sparse LoRA layer
           for name, layer in target_layers.items():
               # Create sparse LoRA wrapper
               sparse_lora_layer = SparseLoRALayer(
                   base_layer=layer,
                   rank=self.config.rank,
                   alpha=self.config.alpha,
                   dropout_p=self.config.dropout_p,
                   use_bias=self.config.use_bias,
                   sparsity=self.config.sparsity,
                   pruning_method=self.config.pruning_method,
                   structured_pattern=self.config.structured_pattern
               )
               
               # Replace original layer
               path_parts = name.split('.')
               parent_name = '.'.join(path_parts[:-1])
               child_name = path_parts[-1]
               
               if parent_name:
                   # Get parent module
                   parent = self.base_model
                   for part in parent_name.split('.'):
                       parent = getattr(parent, part)
                   
                   # Replace the original layer
                   setattr(parent, child_name, sparse_lora_layer)
               else:
                   # Layer is at top level
                   setattr(self.base_model, child_name, sparse_lora_layer)
               
               # Store reference
               self.lora_layers[name] = sparse_lora_layer
       
       def _freeze_non_lora_params(self):
           """Freeze all parameters except LoRA parameters."""
           # Get all LoRA parameter IDs
           lora_param_ids = set()
           for layer in self.lora_layers.values():
               for param in [layer.lora_A.weight, layer.lora_B.weight]:
                   lora_param_ids.add(id(param))
               if layer.lora_B.bias is not None:
                   lora_param_ids.add(id(layer.lora_B.bias))
           
           # Freeze all non-LoRA parameters
           for param in self.parameters():
               if id(param) not in lora_param_ids:
                   param.requires_grad = False
       
       def forward(self, *args, **kwargs):
           """Forward pass using the base model with sparse LoRA adaptations."""
           return self.base_model(*args, **kwargs)
       
       def prune_all_layers(self, sparsity=None, method=None):
           """Prune all LoRA layers to the target sparsity."""
           sparsity = sparsity or self.config.sparsity
           method = method or self.config.pruning_method
           
           sparsity_results = {}
           
           for name, layer in self.lora_layers.items():
               if isinstance(layer, SparseLoRALayer):
                   sparsity_results[name] = layer.prune(sparsity, method)
           
           return sparsity_results
       
       def get_sparsity_stats(self):
           """Get sparsity statistics for all layers."""
           stats = {
               "overall": {
                   "total_params": 0,
                   "pruned_params": 0,
                   "sparsity": 0.0
               },
               "layers": {}
           }
           
           for name, layer in self.lora_layers.items():
               if isinstance(layer, SparseLoRALayer):
                   # Count parameters in A
                   a_total = layer.mask_A.numel()
                   a_pruned = a_total - layer.mask_A.sum().item()
                   
                   # Count parameters in B
                   b_total = layer.mask_B.numel()
                   b_pruned = b_total - layer.mask_B.sum().item()
                   
                   total = a_total + b_total
                   pruned = a_pruned + b_pruned
                   
                   layer_stats = {
                       "total_params": total,
                       "pruned_params": pruned,
                       "sparsity": pruned / total if total > 0 else 0.0
                   }
                   
                   stats["layers"][name] = layer_stats
                   
                   # Add to overall stats
                   stats["overall"]["total_params"] += total
                   stats["overall"]["pruned_params"] += pruned
           
           # Calculate overall sparsity
           if stats["overall"]["total_params"] > 0:
               stats["overall"]["sparsity"] = (
                   stats["overall"]["pruned_params"] / 
                   stats["overall"]["total_params"]
               )
           
           return stats
       
       def merge_and_unload(self) -> nn.Module:
           """Merge sparse LoRA weights with base weights and return the base model."""
           logger.info(f"Merging {len(self.lora_layers)} sparse LoRA layers")
           
           # Create a new copy of the base model
           merged_model = copy.deepcopy(self.base_model)
           
           # For each sparse LoRA layer
           for name, lora_layer in self.lora_layers.items():
               # Merge the weights
               merged_layer = lora_layer.merge_weights()
               
               # Find the parent module and replace the layer
               path_parts = name.split('.')
               parent_name = '.'.join(path_parts[:-1])
               child_name = path_parts[-1]
               
               if parent_name:
                   # Get parent module
                   parent = merged_model
                   for part in parent_name.split('.'):
                       parent = getattr(parent, part)
                   
                   # Replace the LoRA layer with merged layer
                   setattr(parent, child_name, merged_layer)
               else:
                   # Layer is at top level
                   setattr(merged_model, child_name, merged_layer)
           
           return merged_model
   ```

2. **Create Utility Functions**
   ```python
   def apply_sparse_lora(
       model: nn.Module,
       rank: int = 8,
       alpha: int = 16,
       dropout_p: float = 0.0,
       target_modules: Optional[List[str]] = None,
       sparsity: float = 0.5,
       pruning_method: str = "magnitude",
       structured_pattern: Optional[str] = None
   ) -> SparseLoRAModel:
       """
       Apply Sparse LoRA to a model for efficient fine-tuning.
       
       Args:
           model: Model to apply LoRA to
           rank: Rank of low-rank decomposition
           alpha: Scaling factor for LoRA
           dropout_p: Dropout probability for LoRA
           target_modules: List of module types to apply LoRA to
           sparsity: Target sparsity ratio (0.0-1.0)
           pruning_method: Method to determine weight importance
           structured_pattern: Pattern for structured sparsity
           
       Returns:
           Model wrapped with Sparse LoRA
       """
       config = SparseLoRAConfig(
           rank=rank,
           alpha=alpha,
           dropout_p=dropout_p,
           target_modules=target_modules,
           sparsity=sparsity,
           pruning_method=pruning_method,
           structured_pattern=structured_pattern
       )
       
       return SparseLoRAModel(model, config)
   ```

### Phase 4: Gradual Pruning Implementation (Estimated completion: June 15, 2025)

1. **Create Pruning Scheduler**
   ```python
   class PruningScheduler:
       def __init__(
           self,
           model: SparseLoRAModel,
           initial_sparsity: float = 0.0,
           final_sparsity: float = 0.8,
           pruning_steps: int = 10,
           pruning_type: str = "linear",
           start_step: int = 0
       ):
           """
           Schedule gradual pruning for sparse LoRA.
           
           Args:
               model: SparseLoRAModel to prune
               initial_sparsity: Starting sparsity level
               final_sparsity: Target final sparsity level
               pruning_steps: Number of pruning steps
               pruning_type: Type of pruning schedule (linear, cubic, exponential)
               start_step: Step to start pruning
           """
           self.model = model
           self.initial_sparsity = initial_sparsity
           self.final_sparsity = final_sparsity
           self.pruning_steps = pruning_steps
           self.pruning_type = pruning_type
           self.start_step = start_step
           self.current_step = 0
           
           # Default pruning method from model config
           self.pruning_method = model.config.pruning_method
       
       def step(self):
           """Perform a pruning step according to the schedule."""
           self.current_step += 1
           
           # Skip if before start step
           if self.current_step < self.start_step:
               return None
           
           # Skip if past pruning steps
           if self.current_step > self.start_step + self.pruning_steps:
               return None
           
           # Calculate target sparsity for this step
           relative_step = self.current_step - self.start_step
           if self.pruning_type == "linear":
               # Linear schedule
               progress = relative_step / self.pruning_steps
               target_sparsity = (
                   self.initial_sparsity + 
                   (self.final_sparsity - self.initial_sparsity) * progress
               )
           elif self.pruning_type == "cubic":
               # Cubic schedule
               progress = (relative_step / self.pruning_steps) ** 3
               target_sparsity = (
                   self.initial_sparsity + 
                   (self.final_sparsity - self.initial_sparsity) * progress
               )
           elif self.pruning_type == "exponential":
               # Exponential schedule
               progress = 1 - 0.95 ** relative_step
               normalized_progress = progress / (1 - 0.95 ** self.pruning_steps)
               target_sparsity = (
                   self.initial_sparsity + 
                   (self.final_sparsity - self.initial_sparsity) * normalized_progress
               )
           else:
               raise ValueError(f"Unknown pruning type: {self.pruning_type}")
           
           # Apply pruning
           return self.model.prune_all_layers(
               sparsity=target_sparsity,
               method=self.pruning_method
           )
   ```

### Phase 5: Integration and Visualization (Estimated completion: June 25, 2025)

1. **Web Interface Enhancement**
   - Add sparsity configuration to the interactive UI
   - Implement pruning method selection
   - Create structured pattern visualization
   - Add sparsity visualization by layer

2. **Monitoring Tools**
   - Create sparsity tracking dashboard
   - Implement pruning schedule visualization
   - Add parameter efficiency metrics

## Testing Strategy

1. **Unit Tests**
   - Test pruning algorithms
   - Verify mask application
   - Test weight importance calculations
   - Verify structured sparsity patterns

2. **Integration Tests**
   - Test end-to-end sparse fine-tuning
   - Verify memory usage reduction
   - Test gradual pruning schedules
   - Verify sparse inference performance

3. **Performance Benchmarks**
   - Compare sparse vs. dense LoRA quality
   - Measure memory usage reductions
   - Test inference speed improvements
   - Benchmark structured vs. unstructured patterns

## Memory Impact

Sparse LoRA optimization provides:
- Additional 30-50% parameter reduction compared to standard LoRA
- Improved inference speed on supporting hardware
- Potential quality improvements through noise reduction

With 50% sparsity and rank=8, a typical adaptation may use only:
- ~0.35% of the parameters of full fine-tuning
- ~40% of the parameters of standard LoRA
- Negligible quality loss compared to dense LoRA

## Documentation Updates

- Add Sparse LoRA section to implementation guide
- Document pruning methods and their trade-offs
- Provide guidance on optimal sparsity levels
- Create tutorials for gradual pruning during training
