from typing import List
from fastapi import APIRouter, HTTPException
from app.models import SocialMediaProfile, SocialMediaProfileCreate, SocialMediaProfileUpdate
from app.db import get_db, create_entity, get_entity, get_entities_by_label, update_entity, delete_entity

router = APIRouter()


@router.post("", response_model=SocialMediaProfile, status_code=201)
async def create_social_media_profile(profile: SocialMediaProfileCreate):
    db = get_db()
    profile_model = SocialMediaProfile(**profile.model_dump())
    entity_id = create_entity(db, "SocialMediaProfile", profile_model)
    created_entity = get_entity(db, "SocialMediaProfile", entity_id)
    return SocialMediaProfile(**created_entity)


@router.get("", response_model=List[SocialMediaProfile])
async def list_social_media_profiles():
    db = get_db()
    entities = get_entities_by_label(db, "SocialMediaProfile")
    return [SocialMediaProfile(**e) for e in entities]


@router.get("/{profile_id}", response_model=SocialMediaProfile)
async def get_social_media_profile(profile_id: str):
    db = get_db()
    entity = get_entity(db, "SocialMediaProfile", profile_id)
    if not entity:
        raise HTTPException(status_code=404, detail="SocialMediaProfile not found")
    return SocialMediaProfile(**entity)


@router.put("/{profile_id}", response_model=SocialMediaProfile)
async def update_social_media_profile(profile_id: str, profile_update: SocialMediaProfileUpdate):
    db = get_db()
    updates = profile_update.model_dump(exclude_none=True)
    entity = update_entity(db, "SocialMediaProfile", profile_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="SocialMediaProfile not found")
    return SocialMediaProfile(**entity)


@router.delete("/{profile_id}", status_code=204)
async def delete_social_media_profile(profile_id: str):
    db = get_db()
    deleted = delete_entity(db, "SocialMediaProfile", profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="SocialMediaProfile not found")

