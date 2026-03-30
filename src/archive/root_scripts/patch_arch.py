import sys

path = r'd:\Projects\impressioncore\src\core\models\impressioncore_b3_architecture.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = """        self.router = nn.Sequential(
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, num_experts)
        )"""

replacement = """        self.router = nn.Sequential(
            nn.LayerNorm(embed_dim),
            nn.Linear(embed_dim, embed_dim),
            nn.GELU(),
            nn.Linear(embed_dim, num_experts)
        )"""

if target in content:
    new_content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully updated architecture.py")
else:
    # Try with \r\n
    target_rn = target.replace('\n', '\r\n')
    if target_rn in content:
        new_content = content.replace(target_rn, replacement.replace('\n', '\r\n'))
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Successfully updated architecture.py (with \r\n)")
    else:
        print("Target not found in architecture.py")
        sys.exit(1)
