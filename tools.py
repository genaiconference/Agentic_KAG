from examples import examples
from neo4j_graphrag.schema import get_schema
from neo4j_graphrag.retrievers import HybridCypherRetriever, Text2CypherRetriever
from neo4j_graphrag.types import LLMMessage
from neo4j_graphrag.types import RetrieverResultItem
from neo4j_graphrag.message_history import InMemoryMessageHistory
from neo4j_graphrag.generation import GraphRAG, RagTemplate
from langchain.tools import Tool
import prompts
import cypher
import json
from langchain_core.tools import tool
from langchain_core.runnables import RunnableLambda
from tqdm.auto import tqdm
from IPython.display import Markdown
from openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # This loads .env at project root

NEO4J_URI = os.getenv('NEO4J_URI')
NEO4J_USERNAME = os.getenv('NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set OPENAI_API_KEY as env variable for openai/neo4j-graphrag compatibility
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

#open_ai_client
open_ai_client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Initialize OpenAI LLM using LangChain
lang_llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY, model_name="gpt-4.1", temperature=0)

# Neo4J LLM & embedder
llm = OpenAILLM(
    model_name="gpt-4.1",
    model_params={"temperature": 0}
)

json_llm = OpenAILLM(
    model_name="gpt-4.1",
    model_params={"temperature": 0,
                  "response_format": {"type": "json_object"}
                  }
)

embedder = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


INDEX_NAME = "entity_vector_index"
FULLTEXT_INDEX_NAME = "entity_fulltext_index"
DIMENSION = 1536


# --- Define Text2Cypher Tool ---
@tool("text2cypher_tool", description="Convert natural language query to Cypher.")
def text2cypher_tool(query: str) -> str:
    """Convert natural language query to Cypher."""
    text2cypher = Text2CypherRetriever(
        driver=driver,
        llm=json_llm,  # Use json_llm for structured output
        neo4j_schema=get_schema(driver),
        custom_prompt=prompts.custom_text2cypher_prompt,
        examples=examples
    )
    res = text2cypher.search(query)
    return res.metadata['cypher']


def result_formatter_dynamic(record):
    data = record.data()
    if len(data) == 1 and isinstance(list(data.values())[0], dict):
        node_props = dict(list(data.values())[0])
    else:
        node_props = dict(data)
    content = "\n".join(f"{k}: {v}" for k, v in node_props.items())

    return RetrieverResultItem(
        content=content.strip(),
        metadata={
            "raw_properties": node_props,
            "score": record.get("score"),
            "node_keys": list(node_props.keys())
        }
    )

# --- Define Hybrid Retrieval Tool ---
class AVHybridRetriever:
    """A class to handle hybrid retrieval for Analytics Vidhya data."""
    def __init__(self, driver, embedder, llm):
        self.driver = driver
        self.embedder = embedder
        self.llm = llm

    def retrieve(self, query: str, cypher_query: str):
        hyb_retriever = HybridCypherRetriever(
            driver=self.driver,
            vector_index_name=INDEX_NAME,
            fulltext_index_name=FULLTEXT_INDEX_NAME,
            retrieval_query=cypher_query,
            embedder=self.embedder,
            result_formatter=result_formatter_dynamic,
        )

        custom_template = RagTemplate(template=prompts.rag_prompt,
                                      expected_inputs=["context", "query_text"],
                                     )

        rag_obj = GraphRAG(retriever=hyb_retriever, llm=self.llm, prompt_template=custom_template)

        response = rag_obj.search(
            query,
            return_context=True,
            retriever_config={'top_k': 20},
            response_fallback="I can't answer this question without context"
        )
        return response.answer

class AVHybridTool(Tool):
    """LangChain Tool for the AVHybridRetriever."""
    def __init__(self, retriever):
        self.retriever = retriever
        super().__init__(
            name="AVVectorRetrieval",
            func=self._run,
            description=(
                "Use this tool to answer questions about the Analytics Vidhya DataHack Summit. "
                "Input should be a JSON object with 'query' and 'cypher_query' keys, e.g.: "
                '{"query": "List speakers", "cypher_query": "MATCH (s:Speaker)..."}'
            ),
        )

    def _run(self, input_str: str) -> str:
        try:
            parsed = json.loads(input_str)
            query = parsed["query"]
            cypher_query = parsed["cypher_query"]
            return self.retriever.retrieve(query, cypher_query)
        except Exception as e:
            return f"Failed to parse input: {e}"


def get_map_system_prompt(context):
    return prompts.MAP_SYSTEM_PROMPT.format(context_data=context)

def get_reduce_system_prompt(report_data, response_type: str = "multiple paragraphs"):
    return prompts.REDUCE_SYSTEM_PROMPT.format(report_data=report_data, response_type=response_type)


# --- Phase 1: Define the map chain ---
def format_map_prompt(summary):
    return {
        "role": "system",
        "content": get_map_system_prompt(summary)
    }

map_prompt_chain = (
    RunnableLambda(lambda inputs: [
        format_map_prompt(inputs["summary"]),
        {"role": "user", "content": inputs["query"]}
    ])
    | lang_llm
)

# --- Phase 2: Define the reduce chain ---
def format_reduce_prompt(intermediate_results):
    return [
        {
            "role": "system",
            "content": get_reduce_system_prompt(intermediate_results)
        },
        {"role": "user", "content": intermediate_results[0]["query"]}
    ]

reduce_prompt_chain = (
    RunnableLambda(format_reduce_prompt)
    | lang_llm
)

# --- Define Global Search Tool ---
def global_retriever(query: str, rating_threshold: float = 5) -> str:
    community_data, _, _ = driver.execute_query(
        """
        MATCH (c:__Community__)
        WHERE c.rating >= $rating
        RETURN c.summary AS summary
        """,
        rating=rating_threshold,
    )

    print(f"Got {len(community_data)} community summaries")

    # Run the map phase for each community
    intermediate_results = []
    for community in tqdm(community_data, desc="Processing communities"):
        result = map_prompt_chain.invoke({
            "summary": community["summary"],
            "query": query
        })
        intermediate_results.append(result)

    # Run the reduce phase
    reduce_input = [{"query": query, "response": r.content if hasattr(r, 'content') else r} for r in intermediate_results]
    final_result = reduce_prompt_chain.invoke(reduce_input)
    answer = final_result.content if hasattr(final_result, 'content') else final_result
    return answer

class GlobalRetrieverTool(Tool):
    """LangChain Tool for the global_retriever."""
    def __init__(self, retriever_func):
        self.retriever_func = retriever_func
        super().__init__(
            name="GlobalRetrieval",
            func=self._run,
            description=(
                "Use this tool to answer questions by performing a global search across communities. "
                "Input should be the query string."
            ),
        )

    def _run(self, query: str) -> str:
        try:
            return self.retriever_func(query)
        except Exception as e:
            return f"Failed to run global retrieval: {e}"


def get_local_system_prompt(report_data, response_type: str = "multiple paragraphs"):
    return prompts.LOCAL_SEARCH_SYSTEM_PROMPT.format(context_data=report_data, response_type=response_type)

def embed(texts, model="text-embedding-3-small"):
    response = open_ai_client.embeddings.create(
        input=texts,
        model=model,
    )
    return list(map(lambda n: n.embedding, response.data))


def chat(messages, model="gpt-4o", temperature=0, config={}):
    response = open_ai_client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=messages,
        **config,
    )
    return response.choices[0].message.content

k_entities = 5

topChunks = 3
topCommunities = 3
topInsideRels = 3

# --- Define Local Search Tool ---
def local_search(query: str) -> str:
    context, _, _ = driver.execute_query(
        cypher.local_search_query,
        embedding=embed(query)[0],
        topChunks=topChunks,
        topCommunities=topCommunities,
        topInsideRels=topInsideRels,
        k=k_entities,
    )
    context_str = str(context[0]["text"])
    local_messages = [
        {
            "role": "system",
            "content": get_local_system_prompt(context_str),
        },
        {
            "role": "user",
            "content": query,
        },
    ]
    final_answer = chat(local_messages, model="gpt-4o")
    return final_answer

class LocalSearchTool(Tool):
    """LangChain Tool for the local_search function."""
    def __init__(self, search_func):
        self.search_func = search_func
        super().__init__(
            name="LocalSearch",
            func=self._run,
            description=(
                "Use this tool to perform a local search within the knowledge graph "
                "to find specific information related to the query. "
                "Input should be the query string."
            ),
        )

    def _run(self, query: str) -> str:
        try:
            return self.search_func(query)
        except Exception as e:
            return f"Failed to run local search: {e}"