import sys

path = r'd:\Projects\impressioncore\src\core\models\impressioncore_b3_architecture.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add norms to __init__
init_target = """        # Expert specialization tracking
        self.expert_usage = nn.Parameter(torch.zeros(num_experts), requires_grad=False)"""

init_replacement = """        # Expert specialization tracking
        self.expert_usage = nn.Parameter(torch.zeros(num_experts), requires_grad=False)

        # Stability Norms
        self.expert_input_norm = nn.LayerNorm(embed_dim)
        self.output_norm = nn.LayerNorm(embed_dim)"""

# Update forward pass - Expert input
forward_input_target = "expert_inputs = x_flat[expert_mask]"
forward_input_replacement = "expert_inputs = self.expert_input_norm(x_flat[expert_mask])"

# Update forward pass - Return
forward_return_target = "return final_output, specialization_loss"
forward_return_replacement = "return self.output_norm(final_output), specialization_loss"

# Handle potential \r\n
if init_target not in content:
    init_target = init_target.replace('\n', '\r\n')
    init_replacement = init_replacement.replace('\n', '\r\n')

if forward_return_target not in content:
    forward_return_target = forward_return_target.replace('\n', '\r\n')
    forward_return_replacement = forward_return_replacement.replace('\n', '\r\n')

# Apply replacements
if init_target in content and forward_input_target in content and forward_return_target in content:
    content = content.replace(init_target, init_replacement)
    content = content.replace(forward_input_target, forward_input_replacement)
    content = content.replace(forward_return_target, forward_return_replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully applied deep stabilization patches to architecture.py")
else:
    print("One or more targets not found in architecture.py")
    if init_target not in content: print("- init_target missing")
    if forward_input_target not in content: print("- forward_input_target missing")
    if forward_return_target not in content: print("- forward_return_target missing")
    sys.exit(1)
