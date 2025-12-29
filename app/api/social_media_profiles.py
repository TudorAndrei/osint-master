"""Social Media Profiles API endpoints."""

from fastapi import APIRouter, HTTPException

from app.db import (
    create_entity,
    delete_entity,
    get_db,
    get_entities_by_label,
    get_entity,
    update_entity,
)
from app.models import (
    SocialMediaProfile,
    SocialMediaProfileCreate,
    SocialMediaProfileUpdate,
)

router = APIRouter()


@router.post("", status_code=201)
async def create_social_media_profile(
    profile: SocialMediaProfileCreate,
) -> SocialMediaProfile:
    """Create a new social media profile."""
    db = get_db()
    profile_model = SocialMediaProfile(**profile.model_dump())
    entity_id = create_entity(db, "SocialMediaProfile", profile_model)
    created_entity = get_entity(db, "SocialMediaProfile", entity_id)
    if not created_entity:
        raise HTTPException(status_code=500, detail="Failed to retrieve created entity")
    return SocialMediaProfile(**created_entity)


@router.get("")
async def list_social_media_profiles() -> list[SocialMediaProfile]:
    """List all social media profiles."""
    db = get_db()
    entities = get_entities_by_label(db, "SocialMediaProfile")
    return [SocialMediaProfile(**e) for e in entities]


@router.get("/{profile_id}")
async def get_social_media_profile(profile_id: str) -> SocialMediaProfile:
    """Get a social media profile by ID."""
    db = get_db()
    entity = get_entity(db, "SocialMediaProfile", profile_id)
    if not entity:
        raise HTTPException(status_code=404, detail="SocialMediaProfile not found")
    return SocialMediaProfile(**entity)


@router.put("/{profile_id}")
async def update_social_media_profile(
    profile_id: str, profile_update: SocialMediaProfileUpdate,
) -> SocialMediaProfile:
    """Update a social media profile."""
    db = get_db()
    updates = profile_update.model_dump(exclude_none=True)
    entity = update_entity(db, "SocialMediaProfile", profile_id, updates)
    if not entity:
        raise HTTPException(status_code=404, detail="SocialMediaProfile not found")
    return SocialMediaProfile(**entity)


@router.delete("/{profile_id}", status_code=204)
async def delete_social_media_profile(profile_id: str) -> None:
    """Delete a social media profile."""
    db = get_db()
    deleted = delete_entity(db, "SocialMediaProfile", profile_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="SocialMediaProfile not found")
