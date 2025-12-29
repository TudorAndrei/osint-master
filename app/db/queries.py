from datetime import datetime
from typing import Any, Dict, List, Optional
from falkordb import Graph
from app.models.base import BaseEntity


def create_entity(graph: Graph, label: str, entity: BaseEntity) -> str:
    properties = entity.model_dump(exclude_none=True)
    entity_id = properties.get("id")
    if not entity_id:
        from uuid import uuid4
        entity_id = str(uuid4())
        properties["id"] = entity_id
    
    properties_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
    params = {k: _serialize_value(v) for k, v in properties.items()}
    
    query = f"CREATE (n:{label} {{{properties_str}}}) RETURN n.id as id"
    result = graph.query(query, params)
    
    if result.result_set:
        return entity_id
    raise Exception("Failed to create entity")


def get_entity(graph: Graph, label: str, entity_id: str) -> Optional[Dict[str, Any]]:
    query = f"MATCH (n:{label}) WHERE n.id = $id RETURN n"
    result = graph.query(query, {"id": entity_id})
    
    if result.result_set:
        node = result.result_set[0][0]
        return _node_to_dict(node)
    return None


def get_entities_by_label(graph: Graph, label: str) -> List[Dict[str, Any]]:
    query = f"MATCH (n:{label}) RETURN n"
    result = graph.query(query)
    
    entities = []
    for row in result.result_set:
        node = row[0]
        entities.append(_node_to_dict(node))
    return entities


def update_entity(graph: Graph, label: str, entity_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    updates["updated_at"] = datetime.utcnow().isoformat()
    set_clauses = [f"n.{k} = ${k}" for k in updates.keys()]
    params = {k: _serialize_value(v) for k, v in updates.items()}
    params["id"] = entity_id
    
    query = f"MATCH (n:{label}) WHERE n.id = $id SET {', '.join(set_clauses)} RETURN n"
    result = graph.query(query, params)
    
    if result.result_set:
        node = result.result_set[0][0]
        return _node_to_dict(node)
    return None


def delete_entity(graph: Graph, label: str, entity_id: str) -> bool:
    query = """
    MATCH (n)
    WHERE n.id = $id
    OPTIONAL MATCH (n)-[r]-()
    DELETE n, r
    RETURN COUNT(n) as deleted
    """
    result = graph.query(query, {"id": entity_id})
    
    if result.result_set:
        deleted = result.result_set[0][0]
        return deleted > 0
    return False


def create_relationship(
    graph: Graph,
    source_id: str,
    target_id: str,
    relationship_type: str,
    properties: Optional[Dict[str, Any]] = None
) -> str:
    props = properties or {}
    props["created_at"] = datetime.utcnow().isoformat()
    props["updated_at"] = datetime.utcnow().isoformat()
    
    properties_str = ", ".join([f"{k}: ${k}" for k in props.keys()])
    params = {k: _serialize_value(v) for k, v in props.items()}
    params["source_id"] = source_id
    params["target_id"] = target_id
    
    if properties_str:
        query = f"""
        MATCH (a), (b)
        WHERE a.id = $source_id AND b.id = $target_id
        CREATE (a)-[r:{relationship_type} {{{properties_str}}}]->(b)
        RETURN ID(r) as id
        """
    else:
        query = f"""
        MATCH (a), (b)
        WHERE a.id = $source_id AND b.id = $target_id
        CREATE (a)-[r:{relationship_type}]->(b)
        RETURN ID(r) as id
        """
    
    result = graph.query(query, params)
    
    if result.result_set:
        rel_id = result.result_set[0][0]
        return str(rel_id)
    raise Exception("Failed to create relationship")


def get_relationships(graph: Graph, entity_id: str) -> List[Dict[str, Any]]:
    query = """
    MATCH (a)-[r]->(b)
    WHERE a.id = $id OR b.id = $id
    RETURN type(r) as type, a.id as source_id, b.id as target_id, properties(r) as props
    """
    result = graph.query(query, {"id": entity_id})
    
    relationships = []
    for row in result.result_set:
        rel_type, source_id, target_id, props = row
        parsed_props = _node_to_dict_from_props(props)
        relationships.append({
            "relationship_type": rel_type,
            "source_entity_id": source_id,
            "target_entity_id": target_id,
            **parsed_props
        })
    return relationships


def _serialize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, dict)):
        import json
        return json.dumps(value)
    return value


def _node_to_dict(node) -> Dict[str, Any]:
    props = node.properties
    return _node_to_dict_from_props(props)


def _node_to_dict_from_props(props: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    for key, value in props.items():
        if isinstance(value, str):
            try:
                import json
                result[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                result[key] = value
        else:
            result[key] = value
    return result

