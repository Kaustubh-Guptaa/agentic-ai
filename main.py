from langchain_core.messages import HumanMessage
from agents.data_agent import parent_agent

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