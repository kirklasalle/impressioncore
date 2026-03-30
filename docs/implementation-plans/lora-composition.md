# Implementation Plan: LoRA Composition

## Overview
LoRA Composition enables combining multiple LoRA adaptations for different tasks or domains within a single model. This allows for efficient multi-task learning and adaptation without training separate models for each task.

## Implementation Roadmap

### Phase 1: Composable LoRA Framework (Estimated completion: May 25, 2025)

1. **LoRA Adapter Storage**
   - Create persistent storage for LoRA adapters
   - Implement adapter versioning
   - Add metadata for task association
   - Create adapter import/export utilities

2. **Layer-wise Adapter Management**
   - Implement storage of multiple adaptation matrices per layer
   - Design activation mechanism for adapters
   - Create adapter switching utilities

### Phase 2: Core Components (Estimated completion: June 2, 2025)

1. **Design ComposableLoRALayer**
   ```python
   class ComposableLoRALayer(nn.Module):
       def __init__(
           self,
           base_layer: nn.Linear,
           adapter_configs: Dict[str, Dict] = None,
           default_adapter: Optional[str] = None
       ):
           """
           Initialize a composable LoRA layer that can switch between multiple adapters.
           
           Args:
               base_layer: Original linear layer to be adapted
               adapter_configs: Dictionary mapping adapter names to configurations
               default_adapter: Name of the default adapter to use
           """
           super().__init__()
           
           # Save original layer
           self.base_layer = base_layer
           
           # Extract base layer dimensions
           self.in_features = base_layer.in_features
           self.out_features = base_layer.out_features
           
           # Initialize adapter storage
           self.adapters = nn.ModuleDict()
           self.adapter_configs = {}
           
           # Add initial adapters if provided
           if adapter_configs:
               for name, config in adapter_configs.items():
                   self.add_adapter(name, **config)
           
           # Set default adapter
           self.default_adapter = default_adapter
           self.active_adapter = default_adapter
           
           # Ensure base layer weights are frozen
           for param in base_layer.parameters():
               param.requires_grad = False
       
       def add_adapter(
           self,
           name: str,
           rank: int = 8,
           alpha: float = 16.0,
           dropout_p: float = 0.0,
           use_bias: bool = False,
           init_scale: float = 0.01
       ):
           """Add a new LoRA adapter to this layer."""
           if name in self.adapters:
               logger.warning(f"Adapter {name} already exists. Overwriting.")
           
           # Store configuration
           self.adapter_configs[name] = {
               'rank': rank,
               'alpha': alpha,
               'dropout_p': dropout_p,
               'use_bias': use_bias,
               'scaling': alpha / rank
           }
           
           # Create adapter weights
           adapter = nn.Module()
           adapter.lora_A = nn.Linear(self.in_features, rank, bias=False)
           adapter.lora_B = nn.Linear(rank, self.out_features, bias=use_bias)
           
           # Initialize weights
           nn.init.normal_(adapter.lora_A.weight, mean=0.0, std=init_scale)
           nn.init.zeros_(adapter.lora_B.weight)
           if use_bias and adapter.lora_B.bias is not None:
               nn.init.zeros_(adapter.lora_B.bias)
           
           # Add dropout for regularization
           adapter.dropout = nn.Dropout(dropout_p)
           
           # Add to module dictionary
           self.adapters[name] = adapter
           
           # Set as default if first adapter
           if self.default_adapter is None:
               self.default_adapter = name
               self.active_adapter = name
       
       def set_adapter(self, adapter_name: Optional[str] = None):
           """Set the active adapter for this layer."""
           if adapter_name is None:
               adapter_name = self.default_adapter
               
           if adapter_name not in self.adapters and adapter_name is not None:
               raise ValueError(f"Adapter {adapter_name} not found")
               
           self.active_adapter = adapter_name
       
       def forward(self, x: torch.Tensor) -> torch.Tensor:
           """Forward pass using the selected adapter."""
           # Base layer forward
           base_output = self.base_layer(x)
           
           # If no adapter is active, return base output
           if self.active_adapter is None:
               return base_output
           
           # Get active adapter
           adapter = self.adapters[self.active_adapter]
           config = self.adapter_configs[self.active_adapter]
           
           # LoRA forward path with the selected adapter
           lora_output = adapter.lora_B(adapter.dropout(adapter.lora_A(x)))
           
           # Combine with adapter-specific scaling factor
           scaling = config['scaling']
           return base_output + (lora_output * scaling)
       
       def merge_adapter(self, adapter_name: Optional[str] = None) -> nn.Linear:
           """
           Merge a specific adapter with the base layer weights.
           
           Args:
               adapter_name: Name of the adapter to merge
               
           Returns:
               New Linear layer with merged weights
           """
           if adapter_name is None:
               adapter_name = self.active_adapter
               
           if adapter_name not in self.adapters:
               raise ValueError(f"Adapter {adapter_name} not found")
           
           # Get the adapter and config
           adapter = self.adapters[adapter_name]
           config = self.adapter_configs[adapter_name]
           
           # Create a new linear layer to hold merged weights
           merged_layer = nn.Linear(
               self.in_features, 
               self.out_features,
               bias=True if self.base_layer.bias is not None else False,
               device=self.base_layer.weight.device,
               dtype=self.base_layer.weight.dtype
           )
           
           # Calculate merged weights
           with torch.no_grad():
               # Compute adaptation matrix
               adaptation = adapter.lora_B.weight @ adapter.lora_A.weight
               
               # Apply scaling
               scaling = config['scaling']
               adaptation = adaptation * scaling
               
               # Merge weights
               merged_weights = self.base_layer.weight + adaptation
               merged_layer.weight.copy_(merged_weights)
               
               # Copy bias if present
               if self.base_layer.bias is not None:
                   # Include LoRA bias if used
                   if adapter.lora_B.bias is not None:
                       merged_bias = self.base_layer.bias + adapter.lora_B.bias
                   else:
                       merged_bias = self.base_layer.bias
                   
                   merged_layer.bias.copy_(merged_bias)
           
           return merged_layer
   ```

2. **Design ComposableLoRAModel**
   ```python
   class ComposableLoRAModel(nn.Module):
       def __init__(
           self,
           base_model: nn.Module,
           target_modules: Optional[List[str]] = None,
           module_filter: Optional[str] = None
       ):
           """
           Initialize a model with composable LoRA adaptation capability.
           
           Args:
               base_model: Base model to adapt
               target_modules: List of module types to apply LoRA to
               module_filter: Regex pattern to filter module names
           """
           super().__init__()
           
           self.base_model = base_model
           self.target_modules = target_modules or ["q_proj", "k_proj", "v_proj", "out_proj"]
           self.module_filter = module_filter
           
           # Store adapter names
           self.available_adapters = set()
           self.active_adapter = None
           self.lora_layers = {}
           
           # Convert regular layers to composable LoRA layers
           self._convert_to_composable_layers()
           
           # Freeze all parameters in the base model
           self._freeze_base_params()
       
       def _convert_to_composable_layers(self):
           """Convert regular linear layers to composable LoRA layers."""
           # Find target layers
           target_layers = _find_layers(
               self.base_model,
               target_modules=self.target_modules,
               layer_type=nn.Linear
           )
           
           # Apply module filter if specified
           if self.module_filter is not None:
               module_filter_pattern = re.compile(self.module_filter)
               target_layers = {
                   name: module for name, module in target_layers.items()
                   if module_filter_pattern.search(name)
               }
           
           # Log info
           logger.info(f"Converting {len(target_layers)} layers to composable LoRA layers")
           
           # Replace each target layer with a composable LoRA layer
           for name, layer in target_layers.items():
               # Create composable LoRA layer
               composable_layer = ComposableLoRALayer(base_layer=layer)
               
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
                   setattr(parent, child_name, composable_layer)
               else:
                   # Layer is at top level
                   setattr(self.base_model, child_name, composable_layer)
               
               # Store reference
               self.lora_layers[name] = composable_layer
       
       def _freeze_base_params(self):
           """Freeze all parameters in the base model."""
           for param in self.base_model.parameters():
               if not isinstance(param, ComposableLoRALayer):
                   param.requires_grad = False
       
       def add_adapter(
           self,
           adapter_name: str,
           rank: int = 8,
           alpha: float = 16.0,
           dropout_p: float = 0.0,
           use_bias: bool = False,
           layers: Optional[List[str]] = None
       ):
           """
           Add a new adapter to the model.
           
           Args:
               adapter_name: Name of the adapter
               rank: Rank of low-rank decomposition
               alpha: Scaling factor
               dropout_p: Dropout probability
               use_bias: Whether to use bias in LoRA layers
               layers: Specific layers to add the adapter to (None = all)
           """
           config = {
               'rank': rank,
               'alpha': alpha,
               'dropout_p': dropout_p,
               'use_bias': use_bias
           }
           
           # Target layers
           target_layers = layers or list(self.lora_layers.keys())
           
           # Add adapter to each target layer
           for name in target_layers:
               if name in self.lora_layers:
                   self.lora_layers[name].add_adapter(adapter_name, **config)
           
           # Add to available adapters
           self.available_adapters.add(adapter_name)
           
           # Set as active adapter if first one
           if self.active_adapter is None:
               self.set_adapter(adapter_name)
       
       def set_adapter(self, adapter_name: Optional[str] = None):
           """
           Set the active adapter for all layers.
           
           Args:
               adapter_name: Name of the adapter to activate
           """
           if adapter_name is not None and adapter_name not in self.available_adapters:
               raise ValueError(f"Adapter {adapter_name} not found")
           
           # Set adapter in all LoRA layers
           for layer in self.lora_layers.values():
               layer.set_adapter(adapter_name)
           
           self.active_adapter = adapter_name
       
       def forward(self, *args, **kwargs):
           """Forward pass using the active adapter."""
           return self.base_model(*args, **kwargs)
       
       def save_adapter(self, adapter_name: str, save_path: str):
           """
           Save a specific adapter to disk.
           
           Args:
               adapter_name: Name of the adapter to save
               save_path: Path to save the adapter
           """
           if adapter_name not in self.available_adapters:
               raise ValueError(f"Adapter {adapter_name} not found")
           
           # Create state dict with only the specified adapter
           adapter_state = {}
           
           for layer_name, layer in self.lora_layers.items():
               if adapter_name in layer.adapters:
                   # Get adapter module
                   adapter = layer.adapters[adapter_name]
                   
                   # Store adapter weights
                   for param_name, param in adapter.named_parameters():
                       key = f"{layer_name}.{adapter_name}.{param_name}"
                       adapter_state[key] = param
                   
                   # Store adapter config
                   config_key = f"{layer_name}.{adapter_name}.config"
                   adapter_state[config_key] = layer.adapter_configs[adapter_name]
           
           # Add metadata
           adapter_state['_metadata'] = {
               'name': adapter_name,
               'timestamp': datetime.datetime.now().isoformat(),
               'target_modules': self.target_modules,
               'layer_names': list(self.lora_layers.keys())
           }
           
           # Save to disk
           torch.save(adapter_state, save_path)
           logger.info(f"Saved adapter {adapter_name} to {save_path}")
       
       def load_adapter(self, adapter_path: str, adapter_name: Optional[str] = None):
           """
           Load an adapter from disk.
           
           Args:
               adapter_path: Path to the saved adapter
               adapter_name: Optional name to use for the loaded adapter
           """
           # Load state dict
           adapter_state = torch.load(adapter_path, map_location='cpu')
           
           # Get metadata
           metadata = adapter_state.get('_metadata', {})
           original_name = metadata.get('name', 'unnamed_adapter')
           
           # Use provided name or original name
           adapter_name = adapter_name or original_name
           
           # Process each layer
           layer_configs = {}
           
           # Extract configs and organize by layer
           for key, value in adapter_state.items():
               if key == '_metadata':
                   continue
                   
               if '.config' in key:
                   # Extract layer name
                   layer_name = key.split('.')[0]
                   layer_configs[layer_name] = value
           
           # Create the adapter with extracted configs
           self.add_adapter(adapter_name)
           
           # Load weights for each layer
           for layer_name, layer in self.lora_layers.items():
               if layer_name in layer_configs:
                   adapter = layer.adapters[adapter_name]
                   
                   # Restore A matrix
                   a_key = f"{layer_name}.{original_name}.lora_A.weight"
                   if a_key in adapter_state:
                       adapter.lora_A.weight.data.copy_(adapter_state[a_key])
                   
                   # Restore B matrix
                   b_key = f"{layer_name}.{original_name}.lora_B.weight"
                   if b_key in adapter_state:
                       adapter.lora_B.weight.data.copy_(adapter_state[b_key])
                   
                   # Restore bias if present
                   bias_key = f"{layer_name}.{original_name}.lora_B.bias"
                   if bias_key in adapter_state and adapter.lora_B.bias is not None:
                       adapter.lora_B.bias.data.copy_(adapter_state[bias_key])
           
           # Add to available adapters
           self.available_adapters.add(adapter_name)
           logger.info(f"Loaded adapter {adapter_name} from {adapter_path}")
           
           return adapter_name
   ```

3. **Implement Adapter Merging**
   ```python
   def merge_adapters(
       model: ComposableLoRAModel,
       adapter_names: List[str],
       weights: Optional[List[float]] = None,
       adapter_name: str = "merged"
   ) -> str:
       """
       Merge multiple adapters into a new adapter.
       
       Args:
           model: ComposableLoRAModel
           adapter_names: List of adapter names to merge
           weights: Optional list of weights for weighted merging
           adapter_name: Name for the merged adapter
           
       Returns:
           Name of the merged adapter
       """
       if not all(name in model.available_adapters for name in adapter_names):
           missing = [name for name in adapter_names if name not in model.available_adapters]
           raise ValueError(f"Adapters not found: {missing}")
       
       # Use equal weights if not specified
       if weights is None:
           weights = [1.0 / len(adapter_names)] * len(adapter_names)
       elif len(weights) != len(adapter_names):
           raise ValueError("Mismatch between number of adapters and weights")
       
       # Normalize weights to sum to 1
       weights = [w / sum(weights) for w in weights]
       
       # Create new adapter with a rank that accommodates the merged content
       # This is a heuristic - for true merging we'd need to analyze rank requirements
       max_rank = max(
           layer.adapter_configs[adapter_names[0]]['rank']
           for layer in model.lora_layers.values()
           if adapter_names[0] in layer.adapters
       )
       merged_rank = min(max_rank * 2, 64)  # Increase rank but cap it
       
       # Add new adapter
       model.add_adapter(
           adapter_name=adapter_name,
           rank=merged_rank,
           alpha=16.0  # Default alpha
       )
       
       # For each layer, merge the adapter weights
       for layer_name, layer in model.lora_layers.items():
           # Skip layers that don't have all adapters
           if not all(name in layer.adapters for name in adapter_names):
               continue
           
           # Get the new adapter
           merged_adapter = layer.adapters[adapter_name]
           
           # Get dimensions
           in_features = layer.in_features
           out_features = layer.out_features
           rank = merged_adapter.lora_A.weight.shape[0]
           
           # Initialize merged weights
           merged_A = torch.zeros_like(merged_adapter.lora_A.weight)
           merged_B = torch.zeros_like(merged_adapter.lora_B.weight)
           
           # For each source adapter
           for i, (name, weight) in enumerate(zip(adapter_names, weights)):
               # Get source adapter and its config
               src_adapter = layer.adapters[name]
               src_config = layer.adapter_configs[name]
               src_rank = src_adapter.lora_A.weight.shape[0]
               
               # Skip if incompatible
               if src_rank > rank:
                   logger.warning(f"Adapter {name} has higher rank than merged adapter, truncating")
               
               # Get effective rank for this adapter
               effective_rank = min(src_rank, rank)
               
               # Copy and weight the A matrix (truncate or pad as needed)
               merged_A[:effective_rank, :] += weight * src_adapter.lora_A.weight[:effective_rank, :]
               
               # Copy and weight the B matrix (truncate or pad as needed)
               merged_B[:, :effective_rank] += weight * src_adapter.lora_B.weight[:, :effective_rank]
               
               # Handle bias if present
               if merged_adapter.lora_B.bias is not None and src_adapter.lora_B.bias is not None:
                   merged_adapter.lora_B.bias.data += weight * src_adapter.lora_B.bias.data
           
           # Copy merged weights to the new adapter
           merged_adapter.lora_A.weight.data.copy_(merged_A)
           merged_adapter.lora_B.weight.data.copy_(merged_B)
       
       return adapter_name
   ```

### Phase 3: Utility Functions (Estimated completion: June 10, 2025)

1. **Factory Function**
   ```python
   def create_composable_lora_model(
       model: nn.Module,
       target_modules: Optional[List[str]] = None,
       module_filter: Optional[str] = None
   ) -> ComposableLoRAModel:
       """
       Create a composable LoRA model from a base model.
       
       Args:
           model: Base model to adapt
           target_modules: List of module types to apply LoRA to
           module_filter: Regex pattern to filter module names
           
       Returns:
           ComposableLoRAModel ready for multiple adapters
       """
       return ComposableLoRAModel(
           base_model=model,
           target_modules=target_modules,
           module_filter=module_filter
       )
   ```

2. **Mixed Inference Function**
   ```python
   def run_with_mixed_adapters(
       model: ComposableLoRAModel,
       inputs: Dict[str, torch.Tensor],
       adapter_weights: Dict[str, float] = None,
       layer_adapter_map: Dict[str, str] = None
   ) -> torch.Tensor:
       """
       Run inference with different adapters for different parts of the model.
       
       Args:
           model: ComposableLoRAModel
           inputs: Model inputs
           adapter_weights: Mapping of adapter names to weights (for weighted mixing)
           layer_adapter_map: Mapping of layer names to adapter names
           
       Returns:
           Model output
       """
       # Store original adapter state
       original_adapter = model.active_adapter
       
       try:
           # If layer_adapter_map is provided, set adapters per layer
           if layer_adapter_map:
               for layer_name, adapter_name in layer_adapter_map.items():
                   if layer_name in model.lora_layers:
                       model.lora_layers[layer_name].set_adapter(adapter_name)
           
           # If adapter_weights is provided, create a temporary merged adapter
           elif adapter_weights:
               adapter_names = list(adapter_weights.keys())
               weights = [adapter_weights[name] for name in adapter_names]
               
               # Create temporary merged adapter
               temp_name = merge_adapters(model, adapter_names, weights, "temp_mixed")
               model.set_adapter(temp_name)
           
           # Run forward pass
           outputs = model(**inputs)
           
           return outputs
           
       finally:
           # Restore original adapter state
           model.set_adapter(original_adapter)
           
           # Clean up temporary adapter if created
           if adapter_weights and "temp_mixed" in model.available_adapters:
               # Remove temp adapter (implementation detail)
               pass
   ```

### Phase 4: Web Interface and Visualization (Estimated completion: June 20, 2025)

1. **Web Interface Enhancements**
   - Add adapter management UI
   - Implement adapter comparison visualization
   - Create adapter blending controls
   - Add import/export functionality

2. **Visualization Tools**
   - Create adapter similarity visualization
   - Implement weight distribution comparison
   - Add performance analysis by adapter

## Testing Strategy

1. **Unit Tests**
   - Test adapter addition/removal
   - Verify adapter switching
   - Test weight merging functionality
   - Verify import/export operations

2. **Integration Tests**
   - Test multi-adapter training
   - Verify adapter composition
   - Test adapter saving/loading
   - Verify memory management with multiple adapters

3. **Performance Benchmarks**
   - Compare individual vs. merged adapters
   - Measure overhead of adapter switching
   - Test quality of composed adapters

## Memory Impact

LoRA Composition optimizes memory usage by:
- Sharing base model parameters across tasks
- Allowing selective activation of adapters
- Enabling fine-grained control over adaptation

Expected memory benefits:
- Multiple specialized adaptations with only 2-5% additional parameters per task
- Efficient storage of multiple fine-tuned variants in a single model
- Load-on-demand capabilities for memory-constrained environments

## Documentation Updates

- Add LoRA Composition section to implementation guide
- Document adapter management procedures
- Provide examples of effective adapter combinations
- Create visualization guides for understanding adapter similarities
