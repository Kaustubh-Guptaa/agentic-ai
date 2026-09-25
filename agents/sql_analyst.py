import os
import sys

# Add the parent directory to the Python path to import modules from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_router import choose_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema, JudgeSchema
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

# ------------ AI Agent Code ------------

# Curate Question Node
def curate_question(state: AgentSchema) -> AgentSchema:
    
    user_question = state.user_question # Pydantic model objects are accessed using dot notation
    
    llm = choose_llm("low")  
    
    response = llm.invoke(f"Curate the following question for SQL query generation: {user_question}")
    
    state.curated_question = response.content  # Update the curated question in the state
    state.messages = state.messages + [HumanMessage(content=f"Curated Question: {state.curated_question}")]  # Append the curated question to the messages
    
    return state


# Prompt Engineering Node for the agent
def prompt_query_context(state: AgentSchema) -> AgentSchema:
    
    curated_question = state.curated_question
    
    connection_details = {
        "host": os.environ['host'],
        "port": int(os.environ['port']),
        "user": os.environ['user'],
        "password": os.environ['password'],
        "dbname": os.environ['database']
    }
    
    obj = DatabaseUtil(connection_details)
    schema_info = obj.schema_details('public')
    
    # Prompt engineering for the agent to generate SQL query
    prompt = f"""
    You are an SQL analyst agent. Your task is to convert the user's natural language 
    query into Postgres SQL query that can be executed on the database. You are provided 
    with the user's original query and the schema details of the database, including
    table names, column names, data types, and sample data for each table so that 
    you can understand the structure of the database and generate an accurate SQL query.
    Unless user explicitly asks for specific number of rows, always limit the output to 10 rows.
    Note - Just generate the SQL query without any explanation or additional text because
    this query will be executed directly on the database. So, the output should be SQL
    ready to be executed without any modifications.  
    
    User's Original Query: {curated_question}

    Database Schema Details: {schema_info}
    """
    
    state.prompt_query_context = prompt  # Update the prompt query context in the state
    
    return state

# Generate SQL Query Node
def generate_sql_query(state: AgentSchema) -> AgentSchema:
    
    prompt = state.prompt_query_context
    llm = choose_llm("medium")  
    generated_sql_query = llm.invoke(prompt).content
    
    state.generated_sql_query = generated_sql_query  # Update the generated SQL query in the state
    
    return state

# Is Safe Node
def is_safe_sql(state: AgentSchema) -> AgentSchema:
    
    sql_query = state.generated_sql_query
    
    llm = choose_llm("medium")
    llm_judge = llm.with_structured_output(JudgeSchema) # Enforce the output of the LLM to match the JudgeSchema structure
    
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
    
    judge_response = llm_judge.invoke(prompt)
    state.is_safe = judge_response.answer  # Update the is_safe field in the state; pydantic model objects are accessed using dot notation
    state.comments = judge_response.comments  # Update the comments field in the state
     
    return state

# Canceled SQL Query Node
def canceled_sql_query(state: AgentSchema) -> AgentSchema:
    
    comments = state.comments
    state.final_response = f"The generated SQL query was deemed unsafe by the judge. Comments: {comments}"
    state.messages = state.messages + [AIMessage(content=f"Final Response: {state.final_response}")]  # Append the final response to the messages
    
    return state


# Execute SQL Query Node
def execute_sql_query(state: AgentSchema) -> AgentSchema:
    
    sql_query = state.generated_sql_query
    
    connection_details = {
        "host": os.environ['host'],
        "port": int(os.environ['port']),
        "user": os.environ['user'],
        "password": os.environ['password'],
        "dbname": os.environ['database']
    }
    
    obj = DatabaseUtil(connection_details)
    sql_query_result = obj.execute_sql(sql_query)
    
    state.sql_query_result = sql_query_result  # Update the SQL query result in the state
    
    return state


# Representation Node for the final response
def final_response(state: AgentSchema) -> AgentSchema:
    
    sql_query_result = state.sql_query_result
    curated_question = state.curated_question
    
    llm = choose_llm("low")
    
    prompt = f"""
    You are a SQL analyst agent. Your task is to provide a final response to the user based on the curated 
    question and the results of the executed SQL query. Please provide a clear and concise answer to the 
    user's original question, using the results of the executed SQL query to support your response. If the 
    SQL query did not return any results, please inform the user accordingly. \n
    
    Here's the user's question: {curated_question} \n
    Here are the SQL Results: {sql_query_result}
    """
    
    llm_response = llm.invoke(prompt)
    state.final_response = llm_response.content  # Update the final response in the state
    state.messages = state.messages + [AIMessage(content=f"Final Response: {state.final_response}")]  # Append the final response to the messages
    
    return state


# ------------ Building the Graph ------------

sql_agent_graph = StateGraph(AgentSchema)

# Nodes
sql_agent_graph.add_node("Curate Question", curate_question)
sql_agent_graph.add_node("Prompt Query Context", prompt_query_context)
sql_agent_graph.add_node("Generate SQL Query", generate_sql_query)
sql_agent_graph.add_node("Is Safe SQL", is_safe_sql)
sql_agent_graph.add_node("Canceled SQL Query", canceled_sql_query)
sql_agent_graph.add_node("Execute SQL Query", execute_sql_query)
sql_agent_graph.add_node("Final Response", final_response) 
    
# Edges: Connect the nodes to form the flow of the agent
sql_agent_graph.add_edge(START, "Curate Question")
sql_agent_graph.add_edge("Curate Question", "Prompt Query Context")
sql_agent_graph.add_edge("Prompt Query Context", "Generate SQL Query")
sql_agent_graph.add_edge("Generate SQL Query", "Is Safe SQL")

# Conditional edge based on the safety of the SQL query
def is_safe_sql_condition(state: AgentSchema) -> str:
    if state.is_safe:
        return "Execute SQL Query"  # Proceed to execute the SQL query if it is safe
    else:
        return "Canceled SQL Query"  # Proceed to canceled SQL query if it is not safe

sql_agent_graph.add_conditional_edges("Is Safe SQL", is_safe_sql_condition,
                                      ["Execute SQL Query", "Canceled SQL Query"])

sql_agent_graph.add_edge("Canceled SQL Query", END)  # End the flow if the SQL query is deemed unsafe
sql_agent_graph.add_edge("Execute SQL Query", "Final Response") # Continue if the SQL query is safe 
sql_agent_graph.add_edge("Final Response", END)

# Compile the graph
sql_analyst = sql_agent_graph.compile()

if __name__ == "__main__":

    # # Visualize the graph on Terminal
    # sql_analyst.get_graph().print_ascii()

    input_schema = {
        "messages": [],
        "user_question": "What are the different types of Payment Methods we have in our database",
        "curated_question": "",
        "prompt_query_context": "",
        "generated_sql_query": "",
        "is_safe": False,
        "comments": "",
        "sql_query_result": "",
        "final_response": ""
    }

    # Execute the Graph
    sql_analyst_response = sql_analyst.invoke(input_schema)
    
    # Print the final output of the graph execution
    print(sql_analyst_response['messages'])  # Print the final output of the graph execution
    
    print("********************************")

    print(sql_analyst_response['generated_sql_query'])  # Print the generated SQL query

    print("********************************")

    print(sql_analyst_response['sql_query_result'])  # Print the result of executing the SQL query

    print("********************************")

    print(sql_analyst_response['prompt_query_context'])  # Print the prompt query context

