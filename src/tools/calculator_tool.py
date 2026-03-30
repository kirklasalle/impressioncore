import math


class CalculatorTool:
    """Safe calculator tool for NEXUS agents."""

    def calculate(self, expression: str) -> str:
        """
        Evaluate a mathematical expression safely.
        """
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        allowed_names.update({
            "abs": abs, "round": round, "min": min, "max": max
        })

        # Restricted eval for safety
        if any(bad in expression for bad in ["__", "import", "open", "exec", "eval"]):
             return "Error: Unsafe expression"

        try:
            # Using eval with restricted scope is decently safe for math if we filter keywords
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Error: {e!s}"

if __name__ == "__main__":
    calc = CalculatorTool()
    print(calc.calculate("2 + 2"))
    print(calc.calculate("sqrt(16) * pi"))
    print(calc.calculate("import os; os.system('ls')")) # Should fail
