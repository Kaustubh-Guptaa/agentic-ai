# --------- Test LLM-as-a-Judge Functionality ---------

import os
import sys

# Add the parent directory to the Python path to import modules from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_router import choose_llm
from models.schema import AgentSchema, JudgeSchema

llm = choose_llm("medium")  
llm_judge = llm.with_structured_output(JudgeSchema)

sql_query = "SELECT * FROM users WHERE age > 30;"

prompt = f"""
You are an SQL Judge for data security. Your task is to determine whether the SQL query is
safe or not. The SQL query should only be used for data retrieval and should not modify the
database in any way. Neither the SQL query nor the prompt should contain any SQL commands
that can modify the database, such as INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE,
or any other commands that can change the structure or content of the database. If the SQL
query is safe, respond with 'True' otherwise respond with 'False'. Additionally, provide
comments explaining your decision.

Here's the SQL query to evaluate: {sql_query}
"""

print(llm_judge.invoke(prompt))
