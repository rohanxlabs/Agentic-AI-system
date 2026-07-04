"""Safe calculator implementation using AST parsing."""
import ast


def calculate(expression: str) -> str:
    """Safely evaluate a basic arithmetic expression using AST parsing.
    
    Supports only numbers, +, -, *, /, **, parentheses, and unary minus.
    No access to builtins, attributes, or function calls.
    
    Args:
        expression: Arithmetic expression string to evaluate
        
    Returns:
        String representation of the result, or error message if invalid
    """
    if not expression.strip():
        return "Error: Empty expression provided"
    
    try:
        tree = ast.parse(expression.strip(), mode='eval')
    except SyntaxError as e:
        return f"Error: Invalid syntax in expression: {str(e)}"
    
    # Visitor to evaluate the AST safely
    class SafeEvaluator(ast.NodeVisitor):
        def visit_Constant(self, node: ast.Constant) -> float:
            if isinstance(node.value, (int, float)):
                return float(node.value)
            raise ValueError(f"Unsupported constant type: {type(node.value)}")
        
        def visit_UnaryOp(self, node: ast.UnaryOp) -> float:
            if isinstance(node.op, ast.USub):
                return -self.visit(node.operand)
            raise ValueError(f"Unsupported unary operator: {type(node.op)}")
        
        def visit_BinOp(self, node: ast.BinOp) -> float:
            left = self.visit(node.left)
            right = self.visit(node.right)
            
            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise ZeroDivisionError("Division by zero")
                return left / right
            elif isinstance(node.op, ast.Pow):
                return left ** right
            else:
                raise ValueError(f"Unsupported binary operator: {type(node.op)}")
        
        def generic_visit(self, node: ast.AST) -> None:
            raise ValueError(f"Unsupported syntax in expression: {type(node).__name__}")
    
    try:
        evaluator = SafeEvaluator()
        result = evaluator.visit(tree.body)
        # Return as integer if it's whole number, else float
        if result.is_integer():
            return str(int(result))
        return str(result)
    except ZeroDivisionError:
        return "Error: Division by zero"
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error evaluating expression: {str(e)}"