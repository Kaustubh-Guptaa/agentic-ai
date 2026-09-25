import os
import sys

# Add the parent directory to the Python path to import modules from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.llm_router import choose_llm
from utils.database import DatabaseUtil
from models.schema import AgentSchema, JudgeSchema, AgentSelectionSchema, ParentAgentSchema
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from agents.sql_analyst import sql_analyst
from agents.etl_analyst import etl_analyst

llm = choose_llm("low")  

analyst_router = llm.with_structured_output(AgentSelectionSchema)  # Answer based on the structured output described in ParentAgentSchema

## Test
# print(analyst_router.invoke("Should I use SQL Agent or ETL Agent to answer the following question: 'Get me the total sales for the last quarter?'"))


# ------------- Data Agent Nodes --------------

def agent_selection_node(state: ParentAgentSchema):

    message = state.messages[-1].content
    select_agent = analyst_router.invoke(message)

    # Return only the updated keys; returning the full state would re-add messages via the `add` reducer
    return {"answer": select_agent.answer, "comments": select_agent.comments} # dot notation -> Pydantic; with_structured_output()


def etl_node(state: ParentAgentSchema):

    message = state.messages[-1].content

    response = etl_analyst.invoke({"messages": [HumanMessage(content=message)]})

    return {"messages": [response["messages"][-1]]}

def sql_node(state: ParentAgentSchema):

    message = state.messages[-1].content

    input_schema = {
            "messages": [],
            "user_question": message,
            "curated_question": "",
            "prompt_query_context": "",
            "generated_sql_query": "",
            "is_safe": False,
            "comments": "",
            "sql_query_result": "",
            "final_response": ""
        }
    
    response = sql_analyst.invoke(input_schema)
    
    return {"messages": [AIMessage(content=response["final_response"])]}


# ------------- Data Agent Graph --------------

data_agent_graph = StateGraph(ParentAgentSchema)

# Nodes
data_agent_graph.add_node('agent_selection_node', agent_selection_node)
data_agent_graph.add_node('etl_node', etl_node)
data_agent_graph.add_node('sql_node', sql_node)

# Edges
data_agent_graph.add_edge(START, 'agent_selection_node')

def select_agent_node(state: AgentSelectionSchema):
    if state.answer == 'sql':
        return "sql_node"
    elif state.answer == 'etl':
        return "etl_node"
    else:
        raise "Error deciding agent"

data_agent_graph.add_conditional_edges(
    'agent_selection_node', select_agent_node,
    {
        'sql_node': 'sql_node',
        'etl_node': 'etl_node'
    }
)

data_agent_graph.add_edge('sql_node', END)
data_agent_graph.add_edge('etl_node', END)

parent_agent = data_agent_graph.compile()

# parent_agent.get_graph().print_ascii()


if __name__ == "__main__":
    
    response_extract_data = parent_agent.invoke({
        "messages": [HumanMessage(content='Extract data from https://pokeapi.co/api/v2/pokemon and save it C:\\Users\\kaust\\OneDrive\\Desktop\\Agentic AI\\data\\extract')],
        "comments": ""
    })
    
    print(response_extract_data)
    
    response_transform_data = parent_agent.invoke({
        "messages": [HumanMessage(content='Transform data from C:\\Users\\kaust\\OneDrive\\Desktop\\Agentic AI\\data\\extract\\extracted_data.json, and save it to C:\\Users\\kaust\\OneDrive\\Desktop\\Agentic AI\\data\\transform and keep only bulbasaur in csv.')],
        "comments": ""
    })
    
    print(response_transform_data)


    
    
