import sys

path = r'd:\Projects\impressioncore\src\core\models\impressioncore_b3_architecture.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add LayerNorm to EACH expert sequential
target = """            nn.Sequential(
                nn.Linear(embed_dim, expert_dim),
                nn.GELU(),
                nn.Linear(expert_dim, embed_dim),
                nn.Dropout(dropout)
            ) for _ in range(num_experts)"""

replacement = """            nn.Sequential(
                nn.LayerNorm(embed_dim),
                nn.Linear(embed_dim, expert_dim),
                nn.GELU(),
                nn.Linear(expert_dim, embed_dim),
                nn.Dropout(dropout)
            ) for _ in range(num_experts)"""

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully added per-expert LayerNorm")
else:
    target_rn = target.replace('\n', '\r\n')
    if target_rn in content:
        new_content = content.replace(target_rn, replacement.replace('\n', '\r\n'))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully added per-expert LayerNorm (with \r\n)")
    else:
        print("Expert Sequential target not found")
        sys.exit(1)
