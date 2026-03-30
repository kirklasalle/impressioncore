import sys

path = r'd:\Projects\impressioncore\src\core\models\impressioncore_b3_architecture.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Target 1: Add LayerNorm to AssemblyOfExperts initialization for output normalization
target1 = """        # Expert specialization tracking
        self.expert_usage = nn.Parameter(torch.zeros(num_experts), requires_grad=False)"""

replacement1 = """        # Expert specialization tracking
        self.expert_usage = nn.Parameter(torch.zeros(num_experts), requires_grad=False)
        self.output_norm = nn.LayerNorm(embed_dim)"""

# Target 2: Apply LayerNorm to final_output in forward pass
target2 = """        # Average expert outputs
        final_output = final_output / self.experts_per_token

        return final_output"""

replacement2 = """        # Average expert outputs
        final_output = final_output / self.experts_per_token

        return self.output_norm(final_output)"""

if target1 in content and target2 in content:
    content = content.replace(target1, replacement1)
    content = content.replace(target2, replacement2)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully updated architecture.py with output normalization")
else:
    # Try with \r\n
    target1_rn = target1.replace('\n', '\r\n')
    target2_rn = target2.replace('\n', '\r\n')
    if target1_rn in content and target2_rn in content:
        content = content.replace(target1_rn, replacement1.replace('\n', '\r\n'))
        content = content.replace(target2_rn, replacement2.replace('\n', '\r\n'))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully updated architecture.py (with \r\n) with output normalization")
    else:
        print("Targets for output normalization not found")
        sys.exit(1)
