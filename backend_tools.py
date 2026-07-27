import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

load_dotenv()

## Search Tool 
_tavily_search = TavilySearch(
    max_results=5, # Fixed: changed max_result to max_results
    topic="general",
)

@tool
def search_tool(query: str) -> str:
    """Search the web for real-time information, news, weather, and current events."""
    # We manually invoke the complex tool, shielding Groq from the complex schema
    return _tavily_search.invoke({"query": query})

## Calculator Tool
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """
    Perform a basic arithmetic operation on two numbers.
    Supported operations for the 'operation' argument: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}
    
## Stock Price Tool
@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given ticker symbol (e.g., 'AAPL', 'TSLA') 
    using Alpha Vantage.
    """
    # Fixed: Changed double quotes to single quotes inside the f-string variable expression
    api_key = os.getenv('STOCK_API_KEY', '')
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}"
    r = requests.get(url)
    return r.json()