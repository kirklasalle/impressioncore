
import re

FILE_PATH = r"d:\Projects\impressioncore\src\interfaces\web_client\src\App.jsx"

def auto_format():
    with open(FILE_PATH, encoding='utf-8') as f:
        lines = f.readlines()

    formatted_lines = []

    # Indentation settings
    INDENT_SIZE = 4
    current_indent = 0

    # Exceptions that shouldn't cause indent change or should be handled carefully
    # We will use a simplified stack approach for braces.

    for _i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            formatted_lines.append("\n")
            continue

        # Heuristic for decreasing indent BEFORE printing the line
        # If line starts with closing tokens
        if stripped.startswith("}") or stripped.startswith(")") or stripped.startswith("]") or stripped.startswith("</"):
            current_indent = max(0, current_indent - 1)
        # Special case for "};"
        if stripped.startswith("};"):
             # current_indent already decremented by "}" check
             pass

        # Apply indentation
        formatted_lines.append(" " * (current_indent * INDENT_SIZE) + stripped + "\n")

        # Heuristic for increasing indent AFTER printing the line
        # Count openers and closers in the line to adjust NEXT line's indent

        # We need to be careful about strings, but for now we ignore them for simplicity
        # (assuming well-formed code mostly)

        # Net change in braces/parens
        stripped.count("{")
        stripped.count("}")
        stripped.count("(")
        stripped.count(")")
        len(re.findall(r"<[a-zA-Z][^>]*>", stripped)) - len(re.findall(r"<[a-zA-Z][^>]*/>", stripped)) # Simple tag open check
        len(re.findall(r"</[a-zA-Z][^>]*>", stripped))

        # JSX is tricky with regex.
        # Better approach: Just follow the basic structural characters.

        # If line ends with opening char
        if stripped.endswith("{") or stripped.endswith("(") or stripped.endswith("[") or stripped.endswith("=>") or (stripped.endswith("?") and not stripped.startswith("?")):
             current_indent += 1
        elif stripped.endswith(":"): # Case or object key (sometimes)
             # Checking if case statement
             if stripped.startswith("case ") or stripped.startswith("default:"):
                 current_indent += 1

        # If line is self-closing tag starting with < and ending with />?
        # We handle tags loosely.

        # Adjust for next line based on specific tokens at START of line (which we already dedented for)
        # If we dedented for '}', we don't need to do anything else, the loop continues.

        # What if multiple closures on one line? e.g. "}});"
        # The logic above only dedents ONCE if it starts with }.
        # We should calculate net indentation change.


        # Refined logic: simple brace counting is dangerous in JS due to expressions.
        # But for resolving the "Unexpected token" error which is block-level, correct nesting is key.

        # Let's try the "last char" heuristic which is robust for C-style languages.
        # If line ends in {, (, [, then indent++.
        # If line starts with }, ), ], then we already dedented.

        # Additionally, if we have "div className=...", that's an open tag.
        # If we have "</div>", that's a close tag.

        # Re-evaluating indent for next line based on pure counts is safer?
        # No, mixed content like `const x = { a: 1 };` is structured.

        # Let's stick to the "Ends with Opener" vs "Starts with Closer" + HTML logic

        if stripped.endswith("(") or stripped.endswith("{") or stripped.endswith("["):
             # Already handled above? No, I resets current_indent logic below.
             pass
        else:
             # Check for HTML opening tags that aren't self-closing
             # Regex for <Tag ... > but NOT <Tag ... /> and NOT </Tag>
             # This is hard.
             pass

    # Actually, simpler plan:
    # Just read the file and replace the specific block indentation with fixed indentation.
    # The file is mostly fine except for that 2000-2192 block.
    # We will target lines 2000 to 2192 specifically and set them to logical indentation (e.g. 8 spaces / 2 levels).
    pass

def strict_block_fix():
    # Focused fix: We know the corrupted block is approx 2000-2192.
    # We will clamp their indentation to 12 spaces (3 levels deep, assuming inside nested divs).
    # Except the component definitions which should be 4 spaces.

    with open(FILE_PATH, encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    for i, line in enumerate(lines):
        if 2000 <= i <= 2600: # Target range extended
            stripped = line.strip()
            if not stripped:
                new_lines.append("\n")
                continue

            # If it's a component definition or root logic
            if stripped.startswith("const IntelligencePanel") or stripped.startswith("const SystemStatusOverlay"):
                new_lines.append("    " + stripped + "\n")
            elif stripped.startswith("return") or stripped == "};" or stripped == ");":
                # These are likely closing or return statements of the component
                new_lines.append("    " + stripped + "\n")
            elif stripped.startswith("if (!status)"):
                 new_lines.append("        " + stripped + "\n")
            else:
                # Default content indentation
                new_lines.append("        " + stripped + "\n")
        else:
            new_lines.append(line)

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("Strict block fix applied.")

if __name__ == "__main__":
    strict_block_fix()
