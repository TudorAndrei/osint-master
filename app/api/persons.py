from typing import Annotated

from falkordb import Graph
from fastapi import APIRouter, Depends, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import Person

router = APIRouter()


@router.post("", status_code=201)
async def create_person(
    person: Person,
    db: Annotated[Graph, Depends(get_db)],
) -> Person:
    person_model = Person(**person.model_dump())
    entity_id = create_entity(db, "Person", person_model)
    created_entity = get_entity(db, "Person", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return Person(**created_entity)


@router.get("")
async def list_persons(
    db: Annotated[Graph, Depends(get_db)],
) -> list[Person]:
    entities = get_entities_by_label(db, "Person")
    return [Person(**e) for e in entities]


@router.get("/{person_id}")
async def get_person(
    person_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> Person:
    entity = get_entity(db, "Person", person_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Person not found")
    return Person(**entity)


@router.put("/{person_id}")
async def update_person(
    person_id: str,
    person_update: Person,
    db: Annotated[Graph, Depends(get_db)],
) -> Person:
    updates = person_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Person", person_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Person not found")
    return Person(**entity)


@router.delete("/{person_id}", status_code=204)
async def delete_person(
    person_id: str,
    db: Annotated[Graph, Depends(get_db)],
) -> None:
    deleted = delete_entity(db, "Person", person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")
