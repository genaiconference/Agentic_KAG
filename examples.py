examples = [

    # 1. Retrieving Data
    "USER INPUT: 'List all speakers at the conference.'\nQUERY: MATCH (p:Person) WHERE p.is_speaker = true RETURN p.name, p.designation, p.organization",
    "USER INPUT: 'Show all workshops.'\nQUERY: MATCH (w:Workshop) RETURN w.title, w.description, w.level",
    "USER INPUT: 'Display all sessions.'\nQUERY: MATCH (s:Session) RETURN s.title, s.description, s.theme",

    # 2. Relationship Between Entities
    "USER INPUT: 'Who conducted each workshop?'\nQUERY: MATCH (p:Person)-[:CONDUCTS]->(w:Workshop) RETURN w.title, p.name",
    "USER INPUT: 'Which sessions are hosted by the conference?'\nQUERY: MATCH (:Conference)-[:HOSTS]->(s:Session) RETURN s.title",
    "USER INPUT: 'Which sessions cover the topic LLMs?'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic {name: 'LLMs'}) RETURN s.title",

    # 3. Filtering With Conditions
    "USER INPUT: 'List all intermediate-level workshops.'\nQUERY: MATCH (w:Workshop) WHERE w.level = 'Intermediate' RETURN w.title, w.description",
    "USER INPUT: 'Find RAG sessions using LangChain.'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic {name: 'RAG'}) MATCH (s)-[:USES]->(tool:Tool {name: 'LangChain'}) RETURN s.title",
    "USER INPUT: 'Show workshops starting after 10:00 AM.'\nQUERY: MATCH (w:Workshop) WHERE w.start_time > '10:00' RETURN w.title, w.start_time",

    # 4. Aggregations and Statistics
    "USER INPUT: 'Count the number of sessions by theme.'\nQUERY: MATCH (s:Session) RETURN s.theme, COUNT(s) AS session_count",
    "USER INPUT: 'How many workshops did each speaker conduct?'\nQUERY: MATCH (p:Person)-[:CONDUCTS]->(w:Workshop) RETURN p.name, COUNT(w) AS num_workshops",
    "USER INPUT: 'How many sponsors does the conference have?'\nQUERY: MATCH (s:Sponsor)-[:SPONSORS]->(:Conference) RETURN COUNT(s) AS sponsor_count",

    # 5. Pattern-Based Recommendations
    "USER INPUT: 'Recommend workshops covering Agent ops.'\nQUERY: MATCH (w:Workshop)-[:COVERS]->(t:Topic {name: 'Agent ops'}) RETURN w.title, w.description",
    "USER INPUT: 'Suggest sessions for someone interested in LLMs.'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic {name: 'LLMs'}) RETURN s.title",
    "USER INPUT: 'Workshops using the same tools as the session Graph at Scale.'\nQUERY: MATCH (s:Session {title: 'Graph at Scale'})-[:USES]->(tool:Tool)<-[:USES]-(w:Workshop) RETURN DISTINCT w.title",

    # Additional Person, Workshop, Session Queries
    "USER INPUT: 'Who conducted the workshop titled \"Building AgentOps Pipelines\"?'\nQUERY: MATCH (p:Person)-[:CONDUCTS]->(w:Workshop {title: 'Building AgentOps Pipelines'}) RETURN p.name, p.designation",
    "USER INPUT: 'Who presented a session on generative AI?'\nQUERY: MATCH (p:Person)-[:PRESENTS]->(s:Session)-[:COVERS]->(t:Topic {name: 'Generative AI'}) RETURN p.name, s.title",
    "USER INPUT: 'What tools are used in the session titled \"LLM Scalability Challenges\"?'\nQUERY: MATCH (:Session {title: 'LLM Scalability Challenges'})-[:USES]->(tool:Tool) RETURN tool.name",
    "USER INPUT: 'Find all sessions that cover the topic RAG.'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic {name: 'RAG'}) RETURN s.title, s.description",
    "USER INPUT: 'What topics does the workshop Responsible AI in Practice cover?'\nQUERY: MATCH (:Workshop {title: 'Responsible AI in Practice'})-[:COVERS]->(t:Topic) RETURN t.name",
    "USER INPUT: 'Which workshops use PyTorch?'\nQUERY: MATCH (w:Workshop)-[:USES]->(t:Tool {name: 'PyTorch'}) RETURN w.title",
    "USER INPUT: 'What sessions use LangChain?'\nQUERY: MATCH (s:Session)-[:USES]->(t:Tool {name: 'LangChain'}) RETURN s.title",

    # Awards
    "USER INPUT: 'Who won the Best Open Source Contribution award?'\nQUERY: MATCH (p:Person)-[:WINS]->(a:Award {title: 'Best Open Source Contribution'}) RETURN p.name",
    "USER INPUT: 'List all award categories featured in the conference.'\nQUERY: MATCH (:Conference)-[:FEATURES]->(a:Award) RETURN DISTINCT a.category",

    # Sponsors & Companies
    "USER INPUT: 'Show all sponsors of the conference.'\nQUERY: MATCH (s:Sponsor)-[:SPONSORS]->(:Conference) RETURN s.name, s.level",
    "USER INPUT: 'Which companies employ people attending the conference?'\nQUERY: MATCH (p:Person)-[:WORKS_FOR]->(c:Company) RETURN DISTINCT c.name",
    "USER INPUT: 'List sponsors of awards.'\nQUERY: MATCH (s:Sponsor)-[:SPONSORS]->(a:Award) RETURN DISTINCT s.name, a.title",

    # Conference Info
    "USER INPUT: 'What sessions does the conference host?'\nQUERY: MATCH (:Conference)-[:HOSTS]->(s:Session) RETURN s.title",
    "USER INPUT: 'What workshops are hosted by the DataHack Summit 2025?'\nQUERY: MATCH (c:Conference {name: 'DataHack Summit', year: 2025})-[:HOSTS]->(w:Workshop) RETURN w.title",
    "USER INPUT: 'What is the theme of the 2025 conference?'\nQUERY: MATCH (c:Conference {year: 2025}) RETURN c.theme",

    # Participation & Nomination
    "USER INPUT: 'Who participated in the conference?'\nQUERY: MATCH (p:Person)-[:PARTICIPATES_IN]->(:Conference) RETURN p.name",
    "USER INPUT: 'Who nominated people for the AI Innovator Award?'\nQUERY: MATCH (p:Person)-[:NOMINATES]->(a:Award {title: 'AI Innovator Award'}) RETURN p.name",
    "USER INPUT: 'List people and the sessions they attended.'\nQUERY: MATCH (p:Person)-[:ATTENDS]->(s:Session) RETURN p.name, s.title"
]
