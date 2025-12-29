from typing import List
from fastapi import APIRouter, HTTPException
from app.models import Person, PersonCreate, PersonUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=Person, status_code=201)
async def create_person(person: PersonCreate):
    db = get_db()
    person_model = Person(**person.model_dump())
    entity_id = create_entity(db, "Person", person_model)
    created_entity = get_entity(db, "Person", entity_id)
    return Person(**created_entity)


@router.get("", response_model=List[Person])
async def list_persons():
    db = get_db()
    entities = get_entities_by_label(db, "Person")
    return [Person(**e) for e in entities]


@router.get("/{person_id}", response_model=Person)
async def get_person(person_id: str):
    db = get_db()
    entity = get_entity(db, "Person", person_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Person not found")
    return Person(**entity)


@router.put("/{person_id}", response_model=Person)
async def update_person(person_id: str, person_update: PersonUpdate):
    db = get_db()
    updates = person_update.model_dump(exclude_none=True)
    entity = update_entity(db, "Person", person_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="Person not found")
    return Person(**entity)


@router.delete("/{person_id}", status_code=204)
async def delete_person(person_id: str):
    db = get_db()
    deleted = delete_entity(db, "Person", person_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Person not found")

