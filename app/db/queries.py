import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from falkordb import Graph

from app.models.base import EntityMixin


class EntityCreationError(Exception):
    """Raised when entity creation fails."""


class RelationshipCreationError(Exception):
    """Raised when relationship creation fails."""


def create_entity(graph: Graph, label: str, entity: EntityMixin) -> str:
    """Create a new entity in the graph database."""
    properties = entity.model_dump(exclude_none=True)
    entity_id = properties.get("id")
    if not entity_id:
        entity_id = str(uuid4())
        properties["id"] = entity_id

    properties_str = ", ".join([f"{k}: ${k}" for k in properties])
    params = {k: _serialize_value(v) for k, v in properties.items()}

    query = f"CREATE (n:{label} {{{properties_str}}}) RETURN n.id as id"
    result = graph.query(query, params)

    if result.result_set:
        return entity_id
    msg = "Failed to create entity"
    raise EntityCreationError(msg)


def get_entity(graph: Graph, label: str, entity_id: str) -> dict[str, Any] | None:
    """Get an entity by ID from the graph database."""
    query = f"MATCH (n:{label}) WHERE n.id = $id RETURN n"
    result = graph.query(query, {"id": entity_id})

    if result.result_set:
        node = result.result_set[0][0]
        return _node_to_dict(node)
    return None


def get_entities_by_label(graph: Graph, label: str) -> list[dict[str, Any]]:
    """Get all entities with a given label from the graph database."""
    query = f"MATCH (n:{label}) RETURN n"
    result = graph.query(query)

    entities = []
    for row in result.result_set:
        node = row[0]
        entities.append(_node_to_dict(node))
    return entities


def update_entity(
    graph: Graph,
    label: str,
    entity_id: str,
    updates: dict[str, Any],
) -> dict[str, Any] | None:
    """Update an entity in the graph database."""
    updates["updated_at"] = datetime.now(UTC).isoformat()
    set_clauses = [f"n.{k} = ${k}" for k in updates]
    params = {k: _serialize_value(v) for k, v in updates.items()}
    params["id"] = entity_id

    query = f"MATCH (n:{label}) WHERE n.id = $id SET {', '.join(set_clauses)} RETURN n"
    result = graph.query(query, params)

    if result.result_set:
        node = result.result_set[0][0]
        return _node_to_dict(node)
    return None


def delete_entity(graph: Graph, _label: str, entity_id: str) -> bool:
    """Delete an entity from the graph database."""
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
    properties: dict[str, Any] | None = None,
) -> str:
    """Create a relationship between two entities in the graph database."""
    props = properties or {}
    props["created_at"] = datetime.now(UTC).isoformat()
    props["updated_at"] = datetime.now(UTC).isoformat()

    properties_str = ", ".join([f"{k}: ${k}" for k in props])
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
    msg = "Failed to create relationship"
    raise RelationshipCreationError(msg)


def get_relationships(graph: Graph, entity_id: str) -> list[dict[str, Any]]:
    """Get all relationships for an entity from the graph database."""
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
        relationships.append(
            {
                "relationship_type": rel_type,
                "source_entity_id": source_id,
                "target_entity_id": target_id,
                **parsed_props,
            },
        )
    return relationships


def _serialize_value(
    value: str | float | datetime | list[Any] | dict[str, Any] | None,
) -> str | float | None:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


def _node_to_dict(node: Any) -> dict[str, Any]:  # noqa: ANN401
    props = node.properties
    return _node_to_dict_from_props(props)


def _node_to_dict_from_props(props: dict[str, Any]) -> dict[str, Any]:
    result = {}
    for key, value in props.items():
        if isinstance(value, str):
            try:
                result[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                result[key] = value
        else:
            result[key] = value
    return result
