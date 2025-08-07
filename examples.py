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

    # 6. Time and Speaker-Specific Session Queries
"USER INPUT: 'When is Arun delivering a session?'\nQUERY: MATCH (p:Person {name: 'Arun'})-[:PRESENTS]->(s:Session) RETURN s.title, s.start_time, s.day, s.date",

"USER INPUT: 'Give me all the sessions that happen between 12:00 and 13:00 on Day 1.'\nQUERY: MATCH (s:Session) WHERE s.day = 'Day 1' AND s.start_time >= time('12:00') AND s.start_time < time('13:00') RETURN s.title, s.start_time, s.venue",

"USER INPUT: 'In which auditorium should I attend Arun\'s session?'\nQUERY: MATCH (p:Person {name: 'Arun'})-[:PRESENTS]->(s:Session)-[:HOSTED_AT]->(v:Venue) RETURN s.title, v.name",

"USER INPUT: 'I like only sessions related to knowledge graphs. Tell me when and where and who is delivering such sessions.'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic) WHERE toLower(t.name) CONTAINS 'knowledge graph' MATCH (s)<-[:PRESENTS]-(p:Person) OPTIONAL MATCH (s)-[:HOSTED_AT]->(v:Venue) RETURN s.title, s.start_time, s.day, v.name AS venue, p.name AS speaker",


    # 7. Speaker + Time Reasoning
"USER INPUT: 'When is Priya conducting her workshop?'\nQUERY: MATCH (p:Person {name: 'Priya'})-[:CONDUCTS]->(w:Workshop) RETURN w.title, w.start_time, w.duration",

# 8. Tool + Topic Filtering
"USER INPUT: 'List all sessions that cover LLMs and use LangChain.'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic {name: 'LLMs'}) MATCH (s)-[:USES]->(tool:Tool {name: 'LangChain'}) RETURN s.title, s.start_time",

# 9. Multi-hop Reasoning
"USER INPUT: 'Which companies are the speakers of Generative AI sessions affiliated with?'\nQUERY: MATCH (p:Person)-[:PRESENTS]->(s:Session)-[:COVERS]->(t:Topic {name: 'Generative AI'}) MATCH (p)-[:WORKS_FOR]->(c:Company) RETURN DISTINCT p.name, c.name",

# 10. Workshop vs Session Comparison
"USER INPUT: 'Which tools are used both in workshops and sessions?'\nQUERY: MATCH (w:Workshop)-[:USES]->(t:Tool)<-[:USES]-(s:Session) RETURN DISTINCT t.name",

# 11. Venue-Time Planning
"USER INPUT: 'What sessions are happening in ELON after 2 PM on Day 2?'\nQUERY: MATCH (s:Session)-[:HOSTED_AT]->(v:Venue {name: 'ELON'}) WHERE s.day = 'Day 2' AND s.start_time > time('14:00') RETURN s.title, s.start_time",

# 12. Topic Popularity
"USER INPUT: 'Which topics are most frequently covered in sessions?'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic) RETURN t.name, COUNT(s) AS session_count ORDER BY session_count DESC",

# 13. Speaker Session Count
"USER INPUT: 'Which speakers are giving more than one session?'\nQUERY: MATCH (p:Person)-[:PRESENTS]->(s:Session) WITH p, COUNT(s) AS num_sessions WHERE num_sessions > 1 RETURN p.name, num_sessions",

# 14. Venue Load
"USER INPUT: 'How many sessions are hosted in each venue?'\nQUERY: MATCH (s:Session)-[:HOSTED_AT]->(v:Venue) RETURN v.name, COUNT(s) AS session_count ORDER BY session_count DESC",

# 15. Company Presence
"USER INPUT: 'Which companies have more than 2 employees attending sessions?'\nQUERY: MATCH (p:Person)-[:WORKS_FOR]->(c:Company) MATCH (p)-[:ATTENDS]->(s:Session) WITH c, COUNT(DISTINCT p) AS attendees WHERE attendees > 2 RETURN c.name, attendees",

# 16. Cross-Affiliations
"USER INPUT: 'Which universities are represented by people attending the summit?'\nQUERY: MATCH (p:Person)-[:AFFILIATED_WITH]->(u:University) RETURN DISTINCT u.name",

# 17. Day-wise Session Breakdown
"USER INPUT: 'How many sessions happen each day?'\nQUERY: MATCH (s:Session) RETURN s.day, COUNT(s) AS session_count ORDER BY s.day",

# 18. Advanced Filtering
"USER INPUT: 'List advanced sessions on day 3 that use PyTorch.'\nQUERY: MATCH (s:Session) WHERE s.level = 'Advanced' AND s.day = 'Day 3' MATCH (s)-[:USES]->(t:Tool {name: 'PyTorch'}) RETURN s.title, s.start_time, s.venue",

# 19. Instructor Participation
"USER INPUT: 'Does every workshop instructor also present a session?'\nQUERY: MATCH (p:Person)-[:CONDUCTS]->(w:Workshop) OPTIONAL MATCH (p)-[:PRESENTS]->(s:Session) RETURN p.name, COUNT(w) AS num_workshops, COUNT(s) AS num_sessions",

# 20. Tool Usage Trends
"USER INPUT: 'Which tools are most used across all sessions and workshops?'\nQUERY: MATCH (n)-[:USES]->(t:Tool) RETURN t.name, COUNT(*) AS usage_count ORDER BY usage_count DESC",

]

