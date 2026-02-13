from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from loguru import logger
from app.dependencies.dao_dep import get_session_without_commit
from app.dependencies.auth_dep import verify_api_key
from app.dao.organizations_dao import OrganizationDAO
from app.dao.activities_dao import ActivityDAO
from app.dao.buildings_dao import BuildingDAO
from app.schemas.organizations import OrganizationDetail, OrganizationList
from app.schemas.activities import ActivitySearchName

router = APIRouter(prefix="/organizations", tags=["Organizations"])


@router.get(
    "/{organization_id}",
    response_model=OrganizationDetail,
    summary="Детальная информация об организации",
    dependencies=[Depends(verify_api_key)]
)
async def get_organization(
        organization_id: int,
        session: AsyncSession = Depends(get_session_without_commit)
):
    org_dao = OrganizationDAO(session)
    organization = await org_dao.get_by_id_with_relations(organization_id)

    if not organization:
        logger.warning(f"Организация с ID {organization_id} не найдена")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )

    return OrganizationDetail.model_validate(organization)


@router.get(
    "/search/by-name",
    response_model=List[OrganizationList],
    summary="Поиск организаций по названию",
    dependencies=[Depends(verify_api_key)]
)
async def search_organizations_by_name(
        query: str = Query(..., min_length=2, max_length=100, description="Название для поиска"),
        session: AsyncSession = Depends(get_session_without_commit)
):
    org_dao = OrganizationDAO(session)
    organizations = await org_dao.search_by_name(query)
    return TypeAdapter(list[OrganizationList]).validate_python(organizations)


@router.get(
    "/by-building/{building_id}",
    response_model=List[OrganizationList],
    summary="Организации в здании",
    dependencies=[Depends(verify_api_key)]
)
async def get_organizations_by_building(
        building_id: int,
        session: AsyncSession = Depends(get_session_without_commit)
):
    building_dao = BuildingDAO(session)
    building = await building_dao.find_one_or_none_by_id(building_id)

    if not building:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Building not found"
        )

    org_dao = OrganizationDAO(session)
    organizations = await org_dao.get_by_building(building_id)

    return TypeAdapter(list[OrganizationList]).validate_python(organizations)


@router.get(
    "/by-activity",
    response_model=List[OrganizationList],
    summary="Организации по виду деятельности (прямой поиск)",
    dependencies=[Depends(verify_api_key)]
)
async def get_organizations_by_activity(
        query: str = Query(..., min_length=2, max_length=50, description="Название вида деятельности"),
        session: AsyncSession = Depends(get_session_without_commit)
):
    activity_dao = ActivityDAO(session)
    activity = await activity_dao.find_one_or_none(filters=ActivitySearchName(name=query))

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    org_dao = OrganizationDAO(session)
    organizations = await org_dao.get_by_activity_direct(activity.id)

    return TypeAdapter(list[OrganizationList]).validate_python(organizations)


@router.get(
    "/by-activity-tree",
    response_model=List[OrganizationList],
    summary="Организации по виду деятельности и всем подкатегориям",
    dependencies=[Depends(verify_api_key)]
)
async def get_organizations_by_activity_with_children(
        query: str = Query(..., min_length=2, max_length=50, description="Название вида деятельности"),
        session: AsyncSession = Depends(get_session_without_commit)
):
    activity_dao = ActivityDAO(session)
    activity = await activity_dao.find_one_or_none(filters=ActivitySearchName(name=query))

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    org_dao = OrganizationDAO(session)
    organizations = await org_dao.get_by_activity_with_children(
        activity.id
    )

    return TypeAdapter(list[OrganizationList]).validate_python(organizations)


@router.get(
    "/nearby/radius",
    response_model=List[OrganizationList],
    summary="Поиск организаций в радиусе",
    dependencies=[Depends(verify_api_key)]
)
async def find_organizations_in_radius(
        latitude: float = Query(..., ge=-90, le=90, description="Широта центра"),
        longitude: float = Query(..., ge=-180, le=180, description="Долгота центра"),
        radius: float = Query(..., gt=0, le=50000, description="Радиус в метрах (макс 50км)"),
        session: AsyncSession = Depends(get_session_without_commit)
):
    org_dao = OrganizationDAO(session)
    organizations = await org_dao.get_nearby_radius(
        latitude=latitude,
        longitude=longitude,
        radius=radius
    )

    return TypeAdapter(list[OrganizationList]).validate_python(organizations)
