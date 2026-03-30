
file_path = r"d:\Projects\impressioncore\src\interfaces\web_client\src\App.jsx"

with open(file_path, encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
removed = False
for i, line in enumerate(lines):
    # Check for the specific problematic line at 2491 (0-indexed 2490)
    if (2480 <= i <= 2500) and "const [telemetry, setTelemetry] = useState(null);" in line:
        print(f"Removing line {i+1}: {line.strip()}")
        removed = True
        continue
    new_lines.append(line)

if removed:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Successfully removed duplicate telemetry declaration.")
else:
    print("Could not find the duplicate telemetry declaration in the specified range.")
