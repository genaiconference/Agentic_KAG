from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    PromptTemplate,
)

def get_react_agent(llm, tools, system_prompt, verbose=False):
    """Helper function for creating agent executor"""
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="conversation_history", optional=True),
            HumanMessagePromptTemplate(
                prompt=PromptTemplate(input_variables=["input"], template="{input}")
            ),
            AIMessagePromptTemplate(
                prompt=PromptTemplate(
                    input_variables=["agent_scratchpad"], template="{agent_scratchpad}"
                )
            ),
        ]
    )
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        stream_runnable=True,
        handle_parsing_errors=True,
        max_iterations=5,
        return_intermediate_steps=True,
    )