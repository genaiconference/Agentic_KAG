from neo4j_graphrag.schema import get_schema
from neo4j_graphrag.retrievers import HybridCypherRetriever, Text2CypherRetriever
from neo4j_graphrag.retrievers import HybridRetriever
from neo4j_graphrag.types import LLMMessage
from neo4j_graphrag.types import RetrieverResultItem
from neo4j_graphrag.message_history import InMemoryMessageHistory
from neo4j_graphrag.generation import GraphRAG, RagTemplate
from langchain.tools import Tool
from prompts import rag_prompt, custom_text2cypher_prompt2, MAP_SYSTEM_PROMPT, REDUCE_SYSTEM_PROMPT, LOCAL_SEARCH_SYSTEM_PROMPT
from examples import examples
from langchain.prompts import PromptTemplate
from cypher import local_search_query
from langchain_core.runnables import RunnableLambda
from tqdm.auto import tqdm
from openai import OpenAI
from langchain_openai import ChatOpenAI
from neo4j_graphrag.llm import OpenAILLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from neo4j import GraphDatabase
import os

load_dotenv()  # This loads .env at project root

NEO4J_URI = os.getenv('AV_NEO4J_URL')
NEO4J_USERNAME = os.getenv('AV_NEO4J_USERNAME')
NEO4J_PASSWORD = os.getenv('AV_NEO4J_PASSWORD')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set OPENAI_API_KEY as env variable for openai/neo4j-graphrag compatibility
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
)

# open_ai_client
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

embedder = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

INDEX_NAME = "entity_vector_index"
FULLTEXT_INDEX_NAME = "entity_fulltext_index"

DIMENSION = 1536


# -------------------------------------------------------------------------------------------------- Define Hybrid Retrieval Tool -----------------------------------------------------------------------------------------------------------
def get_rag_for_query_hybrid(query: str):
    """
    Wrapper to generate a Rag object dynamically for each query
    """
    hybrid_retriever = HybridRetriever(
        driver=driver,
        vector_index_name="entity_vector_index",
        fulltext_index_name="entity_fulltext_index",
        embedder=embedder,
    )

    custom_template = RagTemplate(template=rag_prompt,
                                  expected_inputs=["context", "query_text"],
                                  )

    rag_obj = GraphRAG(retriever=hybrid_retriever, llm=llm, prompt_template=custom_template)

    response = rag_obj.search(
        query,
    )
    return response.answer


av_hybrid_tool = Tool(
    name="AVHybrid",
    func=get_rag_for_query_hybrid,
    description=(
        "Uses both semantic vector search and traditional keyword search over the graph’s data stored in Neo4j, but does not perform any graph traversal. Instead, it finds relevant nodes and content by combining these retrieval methods for more accurate and contextually relevant answers. Use this tool as the fallback option if none of the other tools can confidently answer the query."
    )
)


# -------------------------------------------------------------------------------------------------- Define Hybrid Cypher Retrieval Tool -----------------------------------------------------------------------------------------------------


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


def generate_cypher_query(query):
    """
    Generate Cypher using the Text2Cypher Retriever

    """
    t2c_retriever = Text2CypherRetriever(
        llm=llm,
        neo4j_schema=get_schema(driver),
        driver=driver,
        custom_prompt=custom_text2cypher_prompt2,
        examples=examples,
    )
    response = t2c_retriever.search(query_text=query)
    return response.metadata['cypher']


def generate_cypher_query_lcel(user_question: str) -> str:
    """
    Converts a natural language question into a read-only Cypher query.

    Args:
        user_question (str): The user's natural language query.

    Returns:
        str: A syntactically correct Cypher query as a string.
    """
    # Ensure cypher_gen_prompt is a PromptTemplate before chaining
    if isinstance(custom_text2cypher_prompt2, str):
        cypher_prompt_template = PromptTemplate.from_template(custom_text2cypher_prompt2)
    else:
        cypher_prompt_template = custom_text2cypher_prompt2

    cypher_chain = cypher_prompt_template | lang_llm

    result = cypher_chain.invoke({"query_text":user_question, "examples":examples})

    return result.content



def get_rag_for_query_text2cypher(query: str):
    """
    Wrapper to generate a Rag object dynamically for each query
    """
    t2c_retriever = Text2CypherRetriever(
        llm=llm,
        neo4j_schema=get_schema(driver),
        driver=driver,
        custom_prompt=custom_text2cypher_prompt2,
        examples=examples,
    )

    custom_template = RagTemplate(template=rag_prompt,
                                  expected_inputs=["context", "query_text"],
                                  )

    rag_obj = GraphRAG(retriever=t2c_retriever, llm=llm, prompt_template=custom_template)

    response = rag_obj.search(
        query,
        return_context=True,
        retriever_config={'top_k': 20},
        response_fallback="I can't answer this question without context"
    )
    return response.answer


def get_rag_for_query_hybrid_cypher(query: str):
    """
    Wrapper to generate a Rag object dynamically for each query
    """
    INDEX_NAME = "entity_vector_index"
    FULLTEXT_INDEX_NAME = "entity_fulltext_index"

    cypher_query = generate_cypher_query_lcel(query)
    print(cypher_query)
    hybrid_cypher_retriever = HybridCypherRetriever(
        driver=driver,
        vector_index_name=INDEX_NAME,
        fulltext_index_name=FULLTEXT_INDEX_NAME,
        retrieval_query=cypher_query,
        embedder=embedder,
        result_formatter=result_formatter_dynamic,
    )

    custom_template = RagTemplate(template=rag_prompt,
                                  expected_inputs=["context", "query_text"],
                                  )

    rag_obj = GraphRAG(retriever=hybrid_cypher_retriever, llm=llm, prompt_template=custom_template)

    response = rag_obj.search(
        query,
        return_context=True,
        retriever_config={'top_k': 20},
        response_fallback="I can't answer this question without context"
    )
    return response.answer


av_hybrid_cypher_tool = Tool(
    name="AVHybridCypher",
    func=get_rag_for_query_hybrid_cypher,
    description=(
        "Performs a hybrid search combining vector similarity and Cypher-based graph traversal, leveraging both semantic embeddings and graph structure in Neo4j for nuanced, context-rich retrieval. Use this tool if the query involves relationships, graph patterns, or semantic context within a Neo4j graph. "
    )
)


# ------------------------------------------------------------------------------------------------- Define Global Search Tool ---------------------------------------------------------------------------------------------------------

def get_map_system_prompt(context):
    return MAP_SYSTEM_PROMPT.format(context_data=context)


def get_reduce_system_prompt(report_data, response_type: str = "multiple paragraphs"):
    return REDUCE_SYSTEM_PROMPT.format(report_data=report_data, response_type=response_type)


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


def get_community_data(rating_threshold: float = 5):
    community_data, _, _ = driver.execute_query(
        """
        MATCH (c:__Community__)
        WHERE c.rating >= $rating
        RETURN c.summary AS summary
        """,
        rating=rating_threshold,
    )
    print(f"Got {len(community_data)} community summaries")
    return community_data


community_data = get_community_data()

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm


def global_retriever(query: str, community_data: list) -> str:
    intermediate_results = []

    def process_community(community):
        result = map_prompt_chain.invoke({
            "summary": community["summary"],
            "query": query
        })
        return result

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_community, c) for c in community_data]
        for f in tqdm(as_completed(futures), total=len(futures), desc="Processing communities in parallel"):
            intermediate_results.append(f.result())

    reduce_input = [
        {"query": query, "response": r.content if hasattr(r, 'content') else r}
        for r in intermediate_results
    ]
    final_result = reduce_prompt_chain.invoke(reduce_input)
    answer = final_result.content if hasattr(final_result, 'content') else final_result
    return answer


global_retriever_tool = Tool(
    name="GlobalRetrieval",
    func=lambda query: global_retriever(query, community_data),
    description=(
        "Performs global semantic search over unstructured text (documents, paragraphs, etc). Choose this tool when a semantic search over all available documents is desired."
        )
)


# ------------------------------------------------------------------------------------------------- Define Local Search Tool ---------------------------------------------------------------------------------------------------------

def get_local_system_prompt(report_data, response_type: str = "multiple paragraphs"):
    return LOCAL_SEARCH_SYSTEM_PROMPT.format(context_data=report_data, response_type=response_type)


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


def local_search(query: str) -> str:
    context, _, _ = driver.execute_query(
        local_search_query,
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


local_retriever_tool = Tool(
    name="LocalRetrieval",
    func=local_search,
    description=(
        "Use this tool to perform a local search within the knowledge graph to find specific information related to the query. Performs semantic search over a subset of documents (i.e., a specific section or context). Use this tool when the query is limited to a smaller scope."
    ),
)

