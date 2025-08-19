examples = [

    # 1) BASIC RETRIEVAL (simple)
    "USER INPUT: 'List all speakers at the conference.'\nQUERY: MATCH (sp:Speaker) RETURN sp.name, sp.designation, sp.organization ORDER BY sp.name",
    "USER INPUT: 'Display all sessions.'\nQUERY: MATCH (s:Session) RETURN s.title, s.session_type AS type, s.theme, s.day, s.start_time, s.end_time ORDER BY s.day, s.start_time",
    "USER INPUT: 'Show all workshops.'\nQUERY: MATCH (w:Workshop) RETURN w.title, w.level, w.start_time ORDER BY time(w.start_time)",
    "USER INPUT: 'List all tools.'\nQUERY: MATCH (t:Tool) RETURN t.name, t.type ORDER BY t.name",
    "USER INPUT: 'List all topics.'\nQUERY: MATCH (t:Topic) RETURN t.name ORDER BY t.name",
    "USER INPUT: 'List all venues.'\nQUERY: MATCH (v:Venue) RETURN v.name ORDER BY v.name",
    "USER INPUT: 'Show all sponsors.'\nQUERY: MATCH (s:Sponsor) RETURN s.name, s.description",
    "USER INPUT: 'List all companies represented.'\nQUERY: MATCH (c:Company) RETURN c.name, c.industry, c.website ORDER BY c.name",
    "USER INPUT: 'List conferences by year.'\nQUERY: MATCH (c:Conference) RETURN c.name, c.year, c.location, c.theme ORDER BY c.year DESC",
    "USER INPUT: 'List all educational institutions speakers studied at.'\nQUERY: MATCH (ei:`Educational Institution`) RETURN ei.name ORDER BY ei.name",

    # 2) DIRECT RELATIONSHIPS (simple → medium)
    "USER INPUT: 'Who presents each session?'\nQUERY: MATCH (sp:Speaker)-[:PRESENTS]->(s:Session) RETURN s.title, sp.name ORDER BY s.title",
    "USER INPUT: 'Who conducted each workshop?'\nQUERY: MATCH (sp:Speaker)-[:CONDUCTS]->(w:Workshop) RETURN w.title, sp.name ORDER BY w.title",
    "USER INPUT: 'Which sessions cover the topic LLMs?'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic {name: 'LLMs'}) RETURN s.title ORDER BY s.title",
    "USER INPUT: 'Which workshops cover Agentic RAG?'\nQUERY: MATCH (w:Workshop)-[:COVERS]->(t:Topic {name: 'Agentic RAG'}) RETURN w.title ORDER BY w.title",
    "USER INPUT: 'What tools are used in the session titled \"LLM Scalability Challenges\"?'\nQUERY: MATCH (:Session {title: 'LLM Scalability Challenges'})-[:USES]->(tool:Tool) RETURN tool.name, tool.type",
    "USER INPUT: 'What sessions use LangChain?'\nQUERY: MATCH (s:Session)-[:USES]->(t:Tool {name: 'LangChain'}) RETURN s.title ORDER BY s.title",
    "USER INPUT: 'Which workshops use PyTorch?'\nQUERY: MATCH (w:Workshop)-[:USES]->(t:Tool {name: 'PyTorch'}) RETURN w.title ORDER BY w.title",
    "USER INPUT: 'Which companies employ speakers attending the conference?'\nQUERY: MATCH (:Speaker)-[:WORKS_FOR]->(c:Company) RETURN DISTINCT c.name ORDER BY c.name",
    "USER INPUT: 'Show sponsors of DataHack Summit 2025.'\nQUERY: MATCH (s:Sponsor)-[:SPONSORS]->(c:Conference {name: 'DataHack Summit', year: 2025}) RETURN s.name ORDER BY s.name",
    "USER INPUT: 'What content is hosted by the conference (sessions & workshops)?'\nQUERY: MATCH (c:Conference)-[:HOSTS]->(x) WHERE x:Session OR x:Workshop RETURN CASE WHEN x:Session THEN 'Session' ELSE 'Workshop' END AS type, x.title ORDER BY type, x.title",
    "USER INPUT: 'What is the venue for each session?'\nQUERY: MATCH (s:Session)-[:HOSTED_AT]->(v:Venue) RETURN s.title, v.name ORDER BY s.title",
    "USER INPUT: 'What is the venue for each workshop?'\nQUERY: MATCH (w:Workshop)-[:HOSTED_AT]->(v:Venue) RETURN w.title, v.name ORDER BY w.title",
    "USER INPUT: 'List hack panel speakers.'\nQUERY: MATCH (sp:Speaker) WHERE sp.is_hackpanel = true RETURN sp.name, sp.designation, sp.organization ORDER BY sp.name",
    "USER INPUT: 'Which speakers present Hack Panel sessions?'\nQUERY: MATCH (sp:Speaker)-[:PRESENTS]->(s:Session {session_type: 'Hack Panel'}) RETURN DISTINCT sp.name ORDER BY sp.name",
    "USER INPUT: 'List speakers and their alma maters.'\nQUERY: MATCH (sp:Speaker)-[r:STUDIED_AT]->(ei:`Educational Institution`) RETURN sp.name, ei.name, r.description ORDER BY sp.name",
    "USER INPUT: 'Which venue hosts the conference?'\nQUERY: MATCH (c:Conference)-[:HOSTED_AT]->(v:Venue) RETURN c.name, c.year, v.name",

    # 3) FILTERING & CONDITIONS (medium)
    "USER INPUT: 'List all intermediate-level workshops.'\nQUERY: MATCH (w:Workshop) WHERE toLower(w.level) = 'intermediate' RETURN w.title, w.description ORDER BY w.title",
    "USER INPUT: 'Find sessions on Day 2.'\nQUERY: MATCH (s:Session {day: 'Day 2'}) RETURN s.title, s.start_time, s.end_time ORDER BY s.start_time",
    "USER INPUT: 'Show sessions starting after 10:00 AM on Day 1.'\nQUERY: MATCH (s:Session {day: 'Day 1'}) WHERE s.start_time > time('10:00') RETURN s.title, s.start_time ORDER BY s.start_time",
    "USER INPUT: 'Show workshops starting after 10:00.'\nQUERY: MATCH (w:Workshop) WHERE time(w.start_time) > time('10:00') RETURN w.title, w.start_time ORDER BY time(w.start_time)",
    "USER INPUT: 'Sessions between 14:00 and 15:30.'\nQUERY: MATCH (s:Session) WHERE s.start_time >= time('14:00') AND s.end_time <= time('15:30') RETURN s.title, s.start_time, s.end_time ORDER BY s.start_time",
    "USER INPUT: 'Sessions that use both LangChain and Neo4j.'\nQUERY: MATCH (s:Session)-[:USES]->(:Tool {name: 'LangChain'}), (s)-[:USES]->(:Tool {name: 'Neo4j'}) RETURN DISTINCT s.title ORDER BY s.title",
    "USER INPUT: 'Sessions covering RAG or Agentic RAG.'\nQUERY: MATCH (s:Session)-[:COVERS]->(t:Topic) WHERE t.name IN ['RAG','Agentic RAG'] RETURN DISTINCT s.title ORDER BY s.title",
    "USER INPUT: 'Speakers with RAG-related skills.'\nQUERY: MATCH (sp:Speaker) WHERE ANY(skill IN sp.skills WHERE toLower(skill) CONTAINS 'rag') RETURN sp.name, sp.skills ORDER BY sp.name",
    "USER INPUT: 'Speakers who have awards listed.'\nQUERY: MATCH (sp:Speaker) WHERE sp.awards IS NOT NULL AND size(sp.awards) > 0 RETURN sp.name, sp.awards ORDER BY sp.name",
    "USER INPUT: 'Speakers certified in AWS or Azure.'\nQUERY: MATCH (sp:Speaker) WHERE ANY(c IN sp.certifications WHERE c CONTAINS 'AWS' OR c CONTAINS 'Azure') RETURN sp.name, sp.certifications ORDER BY sp.name",
    "USER INPUT: 'Venues hosting more than 3 sessions.'\nQUERY: MATCH (v:Venue)<-[:HOSTED_AT]-(s:Session) WITH v, COUNT(s) AS cnt WHERE cnt > 3 RETURN v.name, cnt ORDER BY cnt DESC",
    "USER INPUT: 'Topics with at least 5 total sessions/workshops.'\nQUERY: MATCH (x)-[:COVERS]->(t:Topic) WHERE x:Session OR x:Workshop WITH t, COUNT(x) AS total WHERE total >= 5 RETURN t.name, total ORDER BY total DESC",
    "USER INPUT: 'Most used tools across the program.'\nQUERY: MATCH (x)-[:USES]->(tool:Tool) WHERE x:Session OR x:Workshop RETURN tool.name, COUNT(DISTINCT x) AS uses ORDER BY uses DESC",
    "USER INPUT: 'Companies with at least two speakers.'\nQUERY: MATCH (sp:Speaker)-[:WORKS_FOR]->(c:Company) WITH c, COUNT(DISTINCT sp) AS speakers WHERE speakers >= 2 RETURN c.name, speakers ORDER BY speakers DESC",
    "USER INPUT: 'Sponsor counts per conference.'\nQUERY: MATCH (s:Sponsor)-[:SPONSORS]->(c:Conference) RETURN c.name, c.year, COUNT(s) AS sponsors ORDER BY sponsors DESC",

    # 4) AGGREGATIONS & STATS (medium)
    "USER INPUT: 'Count the number of sessions by theme.'\nQUERY: MATCH (s:Session) RETURN s.theme AS theme, COUNT(*) AS session_count ORDER BY session_count DESC",
    "USER INPUT: 'How many workshops did each speaker conduct?'\nQUERY: MATCH (sp:Speaker)-[:CONDUCTS]->(w:Workshop) RETURN sp.name, COUNT(w) AS num_workshops ORDER BY num_workshops DESC",
    "USER INPUT: 'How many sessions did each speaker present?'\nQUERY: MATCH (sp:Speaker)-[:PRESENTS]->(s:Session) RETURN sp.name, COUNT(s) AS num_sessions ORDER BY num_sessions DESC",
    "USER INPUT: 'How many hack panel speakers are there?'\nQUERY: MATCH (sp:Speaker) WHERE sp.is_hackpanel = true RETURN COUNT(sp) AS hackpanel_speakers",
    "USER INPUT: 'Number of sessions per day per venue.'\nQUERY: MATCH (s:Session)-[:HOSTED_AT]->(v:Venue) RETURN s.day AS day, v.name AS venue, COUNT(*) AS sessions ORDER BY day, venue",
    "USER INPUT: 'Top 5 topics by coverage across sessions and workshops.'\nQUERY: MATCH (x)-[:COVERS]->(t:Topic) WHERE x:Session OR x:Workshop RETURN t.name, COUNT(DISTINCT x) AS cnt ORDER BY cnt DESC LIMIT 5",
    "USER INPUT: 'For each speaker, how many distinct tools are used in their sessions?'\nQUERY: MATCH (sp:Speaker)-[:PRESENTS]->(s:Session)-[:USES]->(tool:Tool) RETURN sp.name, COUNT(DISTINCT tool) AS tools_count ORDER BY tools_count DESC",
    "USER INPUT: 'For each company, how many presenting speakers?'\nQUERY: MATCH (sp:Speaker)-[:WORKS_FOR]->(c:Company) MATCH (sp)-[:PRESENTS]->(:Session) RETURN c.name, COUNT(DISTINCT sp) AS presenters ORDER BY presenters DESC",
    "USER INPUT: 'Average number of sessions per venue.'\nQUERY: MATCH (s:Session)-[:HOSTED_AT]->(v:Venue) WITH v, COUNT(s) AS cnt RETURN avg(cnt) AS avg_sessions_per_venue",
    "USER INPUT: 'Session count by session type.'\nQUERY: MATCH (s:Session) RETURN s.session_type AS type, COUNT(*) AS count ORDER BY count DESC",

    # 5) PATTERN-BASED & RECOMMENDATIONS (complex)
    "USER INPUT: 'Recommend workshops for someone interested in LLMs and LangChain.'\nQUERY: MATCH (w:Workshop)-[:COVERS]->(:Topic {name: 'LLMs'}) MATCH (w)-[:USES]->(:Tool {name: 'LangChain'}) RETURN DISTINCT w.title, w.level, w.instructor ORDER BY w.title",
    "USER INPUT: 'Workshops using the same tools as the session \"Graph at Scale\".'\nQUERY: MATCH (s:Session {title: 'Graph at Scale'})-[:USES]->(tool:Tool)<-[:USES]-(w:Workshop) RETURN DISTINCT w.title ORDER BY w.title",
    "USER INPUT: 'Sessions similar to \"Graph at Scale\" by overlapping topics and tools.'\nQUERY: MATCH (seed:Session {title: 'Graph at Scale'}) OPTIONAL MATCH (seed)-[:COVERS]->(t1:Topic) WITH seed, collect(DISTINCT t1.name) AS seedTopics OPTIONAL MATCH (seed)-[:USES]->(u1:Tool) WITH seed, seedTopics, collect(DISTINCT u1.name) AS seedTools MATCH (other:Session) OPTIONAL MATCH (other)-[:COVERS]->(t2:Topic) WITH seed, seedTopics, seedTools, other, collect(DISTINCT t2.name) AS otherTopics OPTIONAL MATCH (other)-[:USES]->(u2:Tool) WITH seed, seedTopics, seedTools, other, otherTopics, collect(DISTINCT u2.name) AS otherTools WITH other, size([x IN otherTopics WHERE x IN seedTopics]) + size([y IN otherTools WHERE y IN seedTools]) AS overlap WHERE other <> seed AND overlap > 0 RETURN other.title ORDER BY overlap DESC LIMIT 10",
    "USER INPUT: 'Recommend sessions based on a list of interests (topics).' \nQUERY: WITH [x IN $interests | toLower(x)] AS wanted MATCH (s:Session)-[:COVERS]->(t:Topic) WITH s, collect(DISTINCT toLower(t.name)) AS covered WITH s, size([x IN covered WHERE x IN wanted]) AS score WHERE score > 0 RETURN s.title, score ORDER BY score DESC, s.start_time",
    "USER INPUT: 'Find sessions that do not use any tools.'\nQUERY: MATCH (s:Session) WHERE NOT (s)-[:USES]->(:Tool) RETURN s.title ORDER BY s.title",
    "USER INPUT: 'Find sessions that cover both RAG and Vector Databases.'\nQUERY: MATCH (s:Session)-[:COVERS]->(:Topic {name: 'RAG'}), (s)-[:COVERS]->(:Topic {name: 'Vector Databases'}) RETURN DISTINCT s.title ORDER BY s.title",
    "USER INPUT: 'Find sessions covering any of the given topics.'\nQUERY: WITH [x IN $topics | toLower(x)] AS topics MATCH (s:Session)-[:COVERS]->(t:Topic) WHERE toLower(t.name) IN topics RETURN DISTINCT s.title ORDER BY s.title",
    "USER INPUT: 'Who co-presented with a given speaker?'\nQUERY: MATCH (me:Speaker {name: $speaker})-[:PRESENTS]->(s:Session)<-[:PRESENTS]-(co:Speaker) WHERE co <> me RETURN DISTINCT co.name, s.title ORDER BY co.name",
    "USER INPUT: 'Sessions presented by speakers from a specific company.'\nQUERY: MATCH (sp:Speaker)-[:WORKS_FOR]->(c:Company {name: $company}) MATCH (sp)-[:PRESENTS]->(s:Session) RETURN DISTINCT s.title ORDER BY s.title",
    "USER INPUT: 'Beginner workshops covering a given topic.'\nQUERY: MATCH (w:Workshop)-[:COVERS]->(t:Topic {name: $topic}) WHERE toLower(w.level) = 'beginner' RETURN w.title, w.instructor ORDER BY w.title",
    "USER INPUT: 'Sessions at the Claude venue on Day 1 sorted by time.'\nQUERY: MATCH (s:Session)-[:HOSTED_AT]->(v:Venue {name: 'Claude'}) WHERE s.day = 'Day 1' RETURN s.title, s.start_time, s.end_time ORDER BY s.start_time",
    "USER INPUT: 'Sessions that use tools used by workshops covering Agentic RAG.'\nQUERY: MATCH (w:Workshop)-[:COVERS]->(:Topic {name: 'Agentic RAG'})-<-[:COVERS]-(:Workshop) WITH DISTINCT w MATCH (w)-[:USES]->(t:Tool) MATCH (s:Session)-[:USES]->(t) RETURN DISTINCT s.title ORDER BY s.title",

    # 6) TIME SENSITIVE QUESTIONS
      "USER INPUT: 'Find sessions between 2:00 PM and 4:00 PM on Aug 20. '\nQUERY: MATCH (s:Session) WHERE s.date = '2025-08-20' AND s.start_time >= '14:00' AND s.start_time <= '16:00' RETURN s.title, s.start_time, s.end_time, s.instructor ORDER BY s.start_time",
      "USER INPUT: 'Which sessions are happening between 2:00 PM and 4:00 PM on Aug 20?'\nQUERY: MATCH (s:Session) WHERE s.date = '2025-08-20' AND s.start_time >= '14:00' AND s.start_time <= '16:00' RETURN s.title, s.start_time, s.end_time, s.instructor ORDER BY s.start_time",
      "USER INPUT: 'Find sessions that start before 11:00 AM.'\nQUERY: MATCH (s:Session) WHERE s.start_time < '11:00' RETURN s.title, s.start_time, s.end_time ORDER BY s.start_time",
      "USER INPUT: 'Which sessions overlap with 10:00 to 11:00 window?'\nQUERY: MATCH (s:Session) WHERE s.start_time < '11:00' AND s.end_time > '10:00' RETURN s.title, s.start_time, s.end_time ORDER BY s.start_time",
      "USER INPUT: 'List all sessions scheduled on 2025-08-20 in order of time.'\nQUERY: MATCH (s:Session) WHERE s.date = '2025-08-20' RETURN s.title, s.instructor, s.start_time, s.end_time ORDER BY s.start_time",
      "USER INPUT: 'Find sessions longer than 1 hour.'\nQUERY: MATCH (s:Session) WITH s, duration.between(time({hour: toInteger(split(s.start_time, ':')[0]), minute: toInteger(split(s.start_time, ':')[1])}), time({hour: toInteger(split(s.end_time, ':')[0]), minute: toInteger(split(s.end_time, ':')[1])})) AS dur WHERE dur.minutes + dur.hours * 60 > 60 RETURN s.title, s.start_time, s.end_time, dur ORDER BY dur.minutes DESC"

]

