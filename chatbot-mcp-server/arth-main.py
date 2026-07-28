## this is local mcp server for doing arthimatic operation 
from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server with the name "arith"
mcp = FastMCP("arith")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract the second number (b) from the first (a)."""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float | str:
    """Divide the first number (a) by the second (b)."""
    if b == 0:
        return "Error: Cannot divide by zero."
    return a / b

if __name__ == "__main__":
    # FastMCP uses stdio transport by default when run this way
    mcp.run()