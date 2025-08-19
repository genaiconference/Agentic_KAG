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
        nodes AS nodes,
        [r in relationships | r] AS rels"""

louvain_query = '''
        CALL gds.louvain.write('communityGraph', {writeProperty: 'louvain'})
        YIELD communityCount, communityDistribution
        '''

projection_query_all_nodes = '''
        CALL gds.graph.project.cypher(
            'communityGraph',
            'MATCH (n:__Entity__) RETURN id(n) AS id',
            'MATCH (n:__Entity__)-[r]->(m:__Entity__) RETURN id(n) AS source, id(m) AS target
             UNION
             MATCH (n:__Entity__)<-[r]-(m:__Entity__) RETURN id(n) AS source, id(m) AS target'
        )
        YIELD graphName, nodeCount, relationshipCount
        '''
projection_query = """
    'communityGraph',
    // Project Topic nodes + all their neighbors
    '
    MATCH (t:Topic) RETURN id(t) AS id
    UNION
    MATCH (t:Topic)--(n) RETURN id(n) AS id
    ',
    // Project all relationships involving Topics
    '
    MATCH (t:Topic)-[r]-(n) 
    RETURN id(t) AS source, id(n) AS target
    '
)
YIELD graphName, nodeCount, relationshipCount;
 
"""


local_search_query = """
CALL db.index.vector.queryNodes('entity_vector_index', $k, $embedding)
YIELD node, score
WITH collect(node)[0..20] as nodes   // only keep top 20 matched nodes
RETURN {
   Entities: [n IN nodes | {label: labels(n)[0], id: n.entity_id, name: n.name, title: n.title, bio: c.bio, description: c.description,}],
   Communities: [ (n)-[:IN_COMMUNITY]->(c:__Community__) | 
                  {entity: n.name, community: c.summary, title: c.title, rating: c.rating}][0..10],   // max 10 communities
   Connections: [ (n)-[r]->(m) WHERE m IN nodes | 
                  {from: n.name, rel: type(r), to: m.name}][0..20]   // max 20 connections
} AS text
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


