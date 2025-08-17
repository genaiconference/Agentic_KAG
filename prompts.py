COMMUNITY_REPORT_PROMPT = """
You are an AI assistant that helps a human analyst to perform general information discovery. Information discovery is the process of identifying and assessing relevant information associated with certain entities (e.g., organizations and individuals) within a network.

# Goal
Write a comprehensive report of a community, given a list of entities that belong to the community as well as their relationships and optional associated claims. The report will be used to inform decision-makers about information associated with the community and their potential impact. The content of this report includes an overview of the community's key entities, their legal compliance, technical capabilities, reputation, and noteworthy claims.

# Report Structure

The report should include the following sections:

- TITLE: community's name that represents its key entities - title should be short but specific. When possible, include representative named entities in the title.
- SUMMARY: An executive summary of the community's overall structure, how its entities are related to each other, and significant information associated with its entities.
- IMPACT SEVERITY RATING: a float score between 0-10 that represents the severity of IMPACT posed by entities within the community.  IMPACT is the scored importance of a community.
- RATING EXPLANATION: Give a single sentence explanation of the IMPACT severity rating.
- DETAILED FINDINGS: A list of 5-10 key insights about the community. Each insight should have a short summary followed by multiple paragraphs of explanatory text grounded according to the grounding rules below. Be comprehensive.

Return output as a well-formed JSON-formatted string with the following format:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary":<insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary":<insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
        ]
    }}

# Grounding Rules

Points supported by data should list their data references as follows:

"This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."

Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

For example:
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (1), Entities (5, 7); Relationships (23); Claims (7, 2, 34, 64, 46, +more)]."

where 1, 5, 7, 23, 2, 34, 46, and 64 represent the id (not the index) of the relevant data record.

Do not include information where the supporting evidence for it is not provided.


# Example Output

Output:
{{
    "title": "Verdant Oasis Plaza and Unity March",
    "summary": "The community revolves around the Verdant Oasis Plaza, which is the location of the Unity March. The plaza has relationships with the Harmony Assembly, Unity March, and Tribune Spotlight, all of which are associated with the march event.",
    "rating": 5.0,
    "rating_explanation": "The impact severity rating is moderate due to the potential for unrest or conflict during the Unity March.",
    "findings": [
        {{
            "summary": "Verdant Oasis Plaza as the central location",
            "explanation": "Verdant Oasis Plaza is the central entity in this community, serving as the location for the Unity March. This plaza is the common link between all other entities, suggesting its significance in the community. The plaza's association with the march could potentially lead to issues such as public disorder or conflict, depending on the nature of the march and the reactions it provokes. [Data: Entities (5), Relationships (37, 38, 39, 40, 41,+more)]"
        }},
        {{
            "summary": "Harmony Assembly's role in the community",
            "explanation": "Harmony Assembly is another key entity in this community, being the organizer of the march at Verdant Oasis Plaza. The nature of Harmony Assembly and its march could be a potential source of threat, depending on their objectives and the reactions they provoke. The relationship between Harmony Assembly and the plaza is crucial in understanding the dynamics of this community. [Data: Entities(6), Relationships (38, 43)]"
        }},
        {{
            "summary": "Unity March as a significant event",
            "explanation": "The Unity March is a significant event taking place at Verdant Oasis Plaza. This event is a key factor in the community's dynamics and could be a potential source of threat, depending on the nature of the march and the reactions it provokes. The relationship between the march and the plaza is crucial in understanding the dynamics of this community. [Data: Relationships (39)]"
        }},
        {{
            "summary": "Role of Tribune Spotlight",
            "explanation": "Tribune Spotlight is reporting on the Unity March taking place in Verdant Oasis Plaza. This suggests that the event has attracted media attention, which could amplify its impact on the community. The role of Tribune Spotlight could be significant in shaping public perception of the event and the entities involved. [Data: Relationships (40)]"
        }}
    ]
}}


# Real Data

Use the following text for your answer. Do not make anything up in your answer.

Text:
{input_text}

Output:"""


ENTITY_RELATION_EXTRACTOR_PROMPT = """
You are an elite AI model trained to extract structured data to construct a knowledge graph.

Your task is to:
1. Extract **entities (nodes)** from the given input text.
2. Assign a **type (label)** to each entity (based on context).
3. Extract **relationships** between the nodes. The relationship direction goes from the start node to the end node.
4. Return everything in strict **JSON** format.


**✅ Output Format (Strict JSON):**

Return result as JSON using the following format:
{{"nodes": [ {{"id": "0", "label": "the type of entity", "properties": {{"name": "name of entity" }} }}],
  "relationships": [{{"type": "TYPE_OF_RELATIONSHIP", "start_node_id": "0", "end_node_id": "1", "properties": {{"details": "Description of the relationship"}} }}] }}


- Use only the information from the Input text. Do not add any additional information.
- If the input text is empty, return empty Json. 
- Make sure to create as many nodes and relationships as needed to offer rich context.
- An AI knowledge assistant must be able to read this graph and immediately understand the context.

Use only the following nodes and relationships (if provided):
{schema}

- Assign a unique string ID (e.g., "0", "1", "2", ...) to each node, and reuse it to define relationships.
- Relationship direction must be logical and context-driven.
- Do not include explanations, markdown, or non-JSON text.
- Ensure double quotes around all JSON property keys/values.
- Do NOT wrap the JSON in backticks or a list.

---
**Example:**

Input text:
"Bob joined Acme Corp as a Data Scientist in 2022."

Output:
{{
  "nodes": [
    {{"id": "0", "label": "Person", "properties": {{"name": "Bob"}}}},
    {{"id": "1", "label": "Organization", "properties": {{"name": "Acme Corp"}}}}
  ],
  "relationships": [
    {{"type": "WORKS_AT", "start_node_id": "0", "end_node_id": "1", "properties": {{"role": "Data Scientist", "since": "2022"}}}}
  ]
}}

---
Input text:

{text}
"""


custom_text2cypher_prompt = """
You are an expert at writing Cypher queries for a Neo4j 5.x database using ONLY the Schema provided.

Goal: Given a user's question, generate a valid, syntactically correct, and read-only Cypher query strictly based on the schema provided.

Hard rules (must follow):
- Read-only: Use only MATCH, OPTIONAL MATCH, WHERE, WITH, RETURN, ORDER BY, SKIP, LIMIT, UNION, CALL { }.
  - Never use CREATE, MERGE, SET, DELETE, REMOVE, FOREACH, LOAD CSV, db.* procedures, or apoc.* procedures unless explicitly listed in the Schema.
- Schema fidelity: Use only labels, relationship types, and properties that appear exactly in the Schema. Escape any names as needed using backticks.
- No Cartesian products: Do not write `MATCH (a), (b)` unless intentionally cross-joining. Connect nodes via relationships or isolate logic in subqueries.
- Parameterization: Never inline user-provided values. Use only these parameters when needed: $q (string), $terms (list of strings), $startDate, $endDate, $limit (int), $skip (int).
- Case-insensitive, partial match:
  - Prefer: WHERE toLower(<field>) CONTAINS toLower($q)
  - For multiple terms: WHERE ANY(t IN $terms WHERE toLower(<field>) CONTAINS toLower(t))
  - Avoid regex unless necessary; if used, make it case-insensitive: WHERE <field> =~ '(?i).*' + $q + '.*'
- Property existence: Use `<variable>.<property> IS NOT NULL`. Do not use `exists(variable.property)`.
- Relationship existence filters: Use `EXISTS { MATCH ... }`.
- Avoid duplicates: Use DISTINCT when needed.
- Return shape: Project properties only (no raw nodes/relationships). Return only properties that are present in the Schema.
- Pagination & ordering: When returning lists, apply ORDER BY on a relevant property if implied, then `SKIP coalesce($skip, 0)` and `LIMIT coalesce($limit, 50)`.
- Aggregations: If the question asks for counts, rankings, or grouped results, use proper GROUP BY with WITH/COUNT and align all aggregated fields.
- UNION for multiple node types:
  - Use UNION when the question involves multiple labels/types.
  - Every UNION branch must return the same columns (names, order, and types).
  - Use AS to align fields consistently across branches (e.g., `p.name AS name`, `p.designation AS role`; `s.title AS name`, `s.speaker AS role`).
  - Include a `type` column naming the entity label (e.g., `'Speaker' AS type`) across all branches.
  - If parameters are referenced in UNION branches, either inline coalesce($skip/$limit) in each branch, or wrap branches with `CALL { WITH $q, $terms, $startDate, $endDate MATCH ... RETURN ... }`.
- Directionality: Follow relationship directions as defined in the Schema; if unspecified, use undirected patterns.
- Stable identifiers: If returning IDs, prefer `elementId(n) AS id`, unless a business key exists in the Schema.
- Fallback: If the question cannot be answered strictly from the Schema (no matching labels/properties), return a no-op that yields zero rows:
  WITH 'No matching labels or properties in schema' AS message RETURN message LIMIT 0
- Output format: Return clean Cypher only — no markdown, no comments, no explanations, no "Cypher:" label.

📦 Return all relevant fields or properties as implied by the question (only properties that exist in the Schema). Include additional relevant properties if present.
For example:
- Speaker: s.name, s.designation, s.bio, s.linkedin_url
- Workshop: w.title, w.description, w.duration
(Use aliases to align return fields across UNION branches; include a `type` column.)

Schema:
{schema}

User question:
{query_text}

Write only the Cypher query:

"""


rag_prompt="""Answer the following question based solely on the provided context.

Make the answers readable. Use bullets, bold text wherever applicable.

If the context includes any URLs, include them as **meaningful, clickable hyperlinks** in your answer.  
🚫 Do NOT create or assume any URLs that aren't explicitly provided in the context.

If no URLs are present, simply answer the question without using or referencing any links.

DO NOT mention any additional details other than the answer.

---

**Question:**  
{query_text}

**Context:**  
{context}
"""


REACT_PROMPT = '''
You are an intelligent agent tasked with answering questions by reasoning step-by-step and using tools when necessary. Follow the format precisely.

#### Answering and Formatting Instructions

1. **Markdown Formatting (MANDATORY):**
   - All responses must be formatted in Markdown.
   - Use bold text for all the headers and subheaders.
   - Use bullets, tables wherever applicable.
   - Do not use plain text or paragraphs without Markdown structure.
   - Ensure that you use hyphens (-) for list bullets. For sub-bullets, indent using 2 spaces (not tabs). Ensure proper nesting and consistent formatting.

2. **Citations Must (MANDATORY):**
    - Citations must be immediately placed after the relevant content. Cite relevant URLs as meaningful hyperlinks wherever applicable.
    - Do not place citations at the end or in a separate references section. They should appear directly after the statement being referenced. **Place inline citations immediately after the relevant content**
    - Do not include tool names or retriever names in citations.

Answer the following questions as best you can in a clear markdown format. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: [tool name] - should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}'''


CYPHER_REACT_PROMPT = """
You are an expert Cypher query generator for Neo4j. Your goal is to convert natural language questions into valid and efficient Cypher queries using the given text2cypher tool.

**Schema**
{schema}

**Tools**
{tools}

**Rules**
- Output valid Cypher query
- No `\n` or newline escape sequences
- No surrounding quotes in final answer
- Format query as single line

**Format**

Question: the input question  
Thought:{agent_scratchpad} 
Action: tool_name from [{tool_names}]  
Action Input: question to tool  
Observation: result from tool  
(repeat Thought/Action/... as needed)  
Final Answer: the final Cypher query

Begin!

Question: {input}
"""




MAP_SYSTEM_PROMPT = """
---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1 [Data: Reports (report ids)]", "score": score_value}},
        {{"description": "Description of point 2 [Data: Reports (report ids)]", "score": score_value}}
    ]
}}

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

Points supported by data should list the relevant reports as references as follows:
"This is an example sentence supported by data references [Data: Reports (report ids)]"

**Do not list more than 5 record ids in a single reference**. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

For example:
"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (2, 7, 64, 46, 34, +more)]. He is also CEO of company X [Data: Reports (1, 3)]"

where 1, 2, 3, 7, 34, 46, and 64 represent the id (not the index) of the relevant data report in the provided tables.

Do not include information where the supporting evidence for it is not provided.


---Data tables---

{context_data}
"""

REDUCE_SYSTEM_PROMPT = """
---Role---

You are a helpful assistant responding to questions about a dataset by synthesizing perspectives from multiple analysts.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarize all the reports from multiple analysts who focused on different parts of the dataset.

Note that the analysts' reports provided below are ranked in the **descending order of importance**.

If you don't know the answer or if the provided reports do not contain sufficient information to provide an answer, just say so. Do not make anything up.

The final response should remove all irrelevant information from the analysts' reports and merge the cleaned information into a comprehensive answer that provides explanations of all the key points and implications appropriate for the response length and format.

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".

The response should also preserve all the data references previously included in the analysts' reports, but do not mention the roles of multiple analysts in the analysis process.

**Do not list more than 5 record ids in a single reference**. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

For example:

"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Reports (2, 7, 34, 46, 64, +more)]. He is also CEO of company X [Data: Reports (1, 3)]"

where 1, 2, 3, 7, 34, 46, and 64 represent the id (not the index) of the relevant data record.

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}


---Analyst Reports---

{report_data}

Provide accurate answer to the question asked and style the response in markdown. Avoid any unwanted commentary.
"""


LOCAL_SEARCH_SYSTEM_PROMPT = """
---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.

If you don't know the answer, just say so. Do not make anything up.

Points supported by data should list their data references as follows:

"This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."

Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

For example:

"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Sources (15, 16), Reports (1), Entities (5, 7); Relationships (23); Claims (2, 7, 34, 46, 64, +more)]."

where 15, 16, 1, 5, 7, 23, 2, 7, 34, 46, and 64 represent the id (not the index) of the relevant data record.

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}


---Data tables---

{context_data}


---Goal---

Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.

If you don't know the answer, just say so. Do not make anything up.

Points supported by data should list their data references as follows:

"This is an example sentence supported by multiple data references [Data: <dataset name> (record ids); <dataset name> (record ids)]."

Do not list more than 5 record ids in a single reference. Instead, list the top 5 most relevant record ids and add "+more" to indicate that there are more.

For example:

"Person X is the owner of Company Y and subject to many allegations of wrongdoing [Data: Sources (15, 16), Reports (1), Entities (5, 7); Relationships (23); Claims (2, 7, 34, 46, 64, +more)]."

where 15, 16, 1, 5, 7, 23, 2, 7, 34, 46, and 64 represent the id (not the index) of the relevant data record.

Do not include information where the supporting evidence for it is not provided.


---Target response length and format---

{response_type}

Add sections and commentary to the response as appropriate for the length and format. Style the response in markdown.
"""


ReAct_prompt = """
You are a Specialized Agent tasked with helping answer the given question:

### AGENTS RESPONSE WORKFLOW:
Answer using all of these tools: {tools}. and these are the tool names {tool_names}. You must ALWAYS use ALL tools (force call ALL tools) in parallel, regardless of the question.

Follow this format:

Question: {input}

Thought: {agent_scratchpad}

#### PARALLEL TOOL ACTIONS
Action 1: NAMPolicyRetriever
Action Input 1: [input]
Action 2: ContractAnalyzer
Action Input 2: [input]
# MANDATORY: Each Action N MUST be followed by Observation N. DO NOT skip any.
Observation 1: [result from Action 1]
Observation 2: [result from Action 2]

... repeat Thought → Action → Action Input → Observation as needed ...

#### ---  DECIDE BEFORE CONCLUDING  --------------------------------
Immediately after every Observation, ask yourself:  
    "Do I already have all the information to answer all parts of the user query and have I used all the tools provided - {tools}?"

• If No → write another `Thought:` line and continue the loop.  
• If Yes → jump to the Final Thought / Final Answer block below.
----------------------------------------------------------------

-  **Final Thought:** [Summarize what you have determined]
-  **Final Answer:** [Provide a clear, complete answer]

# STRICTLY NOTE  
# • Do NOT skip the self-check and go straight to Final Thought.  
# • You must perform at least one Thought → Action → Observation cycle  
#   unless there are zero applicable tools for this question.

# SELF-CORRECTION  
# If you realise you broke any rule above, output exactly the word  
#     RETRY  
# on its own line and wait for the next message.

Begin!

"""
