

FILE_PATH = r"d:\Projects\impressioncore\src\interfaces\web_client\src\App.jsx"

def clean_indentation():
    with open(FILE_PATH, encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []

    # We want to detect lines with massive indentation (e.g. > 100 spaces) and reduce them.
    # While preserving relative indentation if possible, but 100 spaces is clearly garbage.

    for line in lines:
        stripped = line.lstrip()
        if not stripped:
            new_lines.append(line) # Keep empty lines as is (or empty)
            continue

        leading_spaces = len(line) - len(stripped)

        if leading_spaces > 40:
            # Heuristic: If > 40 spaces, assume it's the messed up block.
            # Convert to a reasonable baseline.
            # Since we don't know the exact nesting depth efficiently without parsing,
            # we'll assume a standard 4-space indent for top-level or 8-12 for nested.
            # However, simpler is just removing the excessive chunk.

            # If it's > 100, reduce strictly.
            if leading_spaces > 100:
                # Keep 4 spaces? Or try to "guess"?
                # Most of these seem to be top level component definitions or inside one block.
                # Let's just set it to 4 spaces if it looks like a component def, or 8 otherwise.
                if stripped.startswith("const ") or stripped.startswith("return") or stripped == "};":
                     # Likely top level or near it
                     new_lines.append("    " + stripped)
                else:
                     new_lines.append("        " + stripped)
            else:
                # If 40-100, maybe just leave it or reduce it?
                # The user logs showed massive indents.
                new_lines.append("    " + stripped)
        else:
            new_lines.append(line)

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"Processed {len(lines)} lines.")

if __name__ == "__main__":
    clean_indentation()
