import_community_query_old = """
UNWIND $data AS row
MERGE (c:__Community__ {communityId: row.communityId})
SET c.title = row.community.title,
    c.summary = row.community.summary,
    c.rating = row.community.rating,
    c.rating_explanation = row.community.rating_explanation
WITH c, row
UNWIND row.nodes AS node
WITH c, node WHERE node IS NOT NULL AND node.entity_id IS NOT NULL
MERGE (n:__Entity__ {entity_id: node.entity_id})
MERGE (n)-[:IN_COMMUNITY]->(c)
"""

import_community_query = """
UNWIND $data AS row
MERGE (c:__Community__ {communityId: row.communityId})
SET c.title = row.community.title,
    c.summary = row.community.summary,
    c.rating = row.community.rating,
    c.rating_explanation = row.community.rating_explanation
WITH c
MATCH (n:__Entity__ {louvain: c.communityId})
MERGE (n)-[:IN_COMMUNITY]->(c)
"""

community_info_query = """MATCH (e:__Entity__)
        WHERE e.louvain IS NOT NULL
        WITH e.louvain AS louvain, collect(e) AS nodes
        WHERE size(nodes) > 1
        CALL apoc.path.subgraphAll(nodes[0], {
            whitelistNodes:nodes
        })
        YIELD relationships
        RETURN louvain AS communityId,
               [n in nodes | {id: n.name, description: n.summary, type: [el in labels(n) WHERE el <> '__Entity__'][0]}] AS nodes,
               [r in relationships | {start: startNode(r).name, type: type(r), end: endNode(r).name, description: r.description}] AS rels"""

louvain_query = '''
        CALL gds.louvain.write('communityGraph', {writeProperty: 'louvain'})
        YIELD communityCount, communityDistribution
        '''

projection_query = '''
        CALL gds.graph.project.cypher(
            'communityGraph',
            'MATCH (n:__Entity__) RETURN id(n) AS id',
            'MATCH (n:__Entity__)-[r]->(m:__Entity__) RETURN id(n) AS source, id(m) AS target
             UNION
             MATCH (n:__Entity__)<-[r]-(m:__Entity__) RETURN id(n) AS source, id(m) AS target'
        )
        YIELD graphName, nodeCount, relationshipCount
        '''
        
local_search_query = """
CALL db.index.vector.queryNodes('entities', $k, $embedding)
YIELD node, score
WITH collect(node) as nodes
WITH collect {
    UNWIND nodes as n
    MATCH (n)<-[:HAS_ENTITY]->(c:__Chunk__)
    WITH c, count(distinct n) as freq
    RETURN c.text AS chunkText
    ORDER BY freq DESC
    LIMIT $topChunks
} AS text_mapping,
collect {
    UNWIND nodes as n
    MATCH (n)-[:IN_COMMUNITY]->(c:__Community__)
    WITH c, c.rank as rank, c.weight AS weight
    RETURN c.summary 
    ORDER BY rank, weight DESC
    LIMIT $topCommunities
} AS report_mapping,
collect {
    UNWIND nodes as n
    MATCH (n)-[r:SUMMARIZED_RELATIONSHIP]-(m) 
    WHERE m IN nodes
    RETURN r.summary AS descriptionText
    ORDER BY r.rank, r.weight DESC 
    LIMIT $topInsideRels
} as insideRels,
collect {
    UNWIND nodes as n
    RETURN n.summary AS descriptionText
} as entities
RETURN {Chunks: text_mapping, Reports: report_mapping, 
       Relationships: insideRels, 
       Entities: entities} AS text
"""

# Cypher to add entity_id where missing
cypher_add_entity_id = """
MATCH (n:__Entity__)
WHERE n.entity_id IS NULL
SET n.entity_id = randomUUID()
RETURN count(n) AS updated_count
"""

constraint_query = """CREATE CONSTRAINT unique_entity_id IF NOT EXISTS
ON (n:__Entity__)
ASSERT n.entity_id IS UNIQUE"""


