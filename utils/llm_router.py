from langchain_openai import ChatOpenAI
from langchain_typesafe import Noul, TypeSafeClassifier
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def choose_llm(level: str):
    """
    Choose the appropriate LLM based on the specified level.

    Args:
        level (str): The level of the LLM to choose. Can be 'low', 'medium', or 'high'.

    Returns:
        str: The name of the chosen LLM.
    """
    if level.lower() == "low":
        llm = ChatOpenAI(model_name="gpt-5.6-luna", temperature=0)
    elif level.lower() == "medium":
        llm = ChatOpenAI(model_name="gpt-5.6-terra", temperature=0)
    elif level.lower() == "high":
        llm = ChatOpenAI(model_name="gpt-5.4-2026-03-05", temperature=0)
    elif level.lower() == "function_tool":
        llm = ChatOpenAI(model_name="gpt-5.6-terra", temperature=0, reasoning={"effort": "none"})
    else:
        raise ValueError("Invalid level specified. Choose from 'low', 'medium', or 'high'.")

    return llm

def parent_agent_decision():
    
    classifier  = TypeSafeClassifier()
    
    return classifier


if __name__ == "__main__":
    # Test the function
    llm_obj = choose_llm("low")
    print(llm_obj.invoke("What's the capital of India?").content)
