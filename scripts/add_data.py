import asyncio
import sys
from pathlib import Path

scripts_dir = Path(__file__).parent
# Поднимаемся на уровень выше (в корень проекта)
project_root = scripts_dir.parent
# Добавляем в sys.path
sys.path.append(str(project_root))

from app.database.db import async_session_maker
from app.schemas.buildings import BuildingCreate
from app.schemas.organizations import OrganizationCreate
from app.dao.buildings_dao import BuildingDAO
from app.dao.organizations_dao import OrganizationDAO
from app.dao.activities_dao import ActivityDAO


async def seed_data():
    async with async_session_maker() as session:
        buildings_dao = BuildingDAO(session)
        buildings_data = [
            BuildingCreate(
                address="г. Москва, ул. Ленина, д. 1",
                latitude=55.7558,
                longitude=37.6176,
                geometry=f'POINT(37.6176 55.7558)'
            ),
            BuildingCreate(
                address="г. Москва, ул. Тверская, д. 15",
                latitude=55.7658,
                longitude=37.6076,
                geometry=f'POINT(37.6076 55.7658)'
            ),
            BuildingCreate(
                address="г. Москва, пр. Мира, д. 10",
                latitude=55.7858,
                longitude=37.6376,
                geometry=f'POINT(37.6376 55.7858)'
            ),
            BuildingCreate(
                address="г. Москва, ул. Арбат, д. 30",
                latitude=55.7458,
                longitude=37.5976,
                geometry=f'POINT(37.5976 55.7458)'
            ),
        ]

        buildings = []
        for building_data in buildings_data:
            building = await buildings_dao.add(building_data)
            buildings.append(building)
            print(f"Created building: {building.address}")

        print("\nCreating activities...")
        activities_dao = ActivityDAO(session)
        # Создаем деятельности (дерево)
        # Уровень 1
        food = await activities_dao.create_activity_tree(
            name="Еда", parent_id=None
        )
        print(f"Created activity: {food.name} (level {food.level})")

        auto = await activities_dao.create_activity_tree(
            name="Автомобили", parent_id=None
        )
        print(f"Created activity: {auto.name} (level {auto.level})")

        # Уровень 2
        meat = await activities_dao.create_activity_tree(
            name="Мясная продукция", parent_id=food.id
        )
        print(f"Created activity: {meat.name} (level {meat.level})")

        dairy = await activities_dao.create_activity_tree(
            name="Молочная продукция", parent_id=food.id
        )
        print(f"Created activity: {dairy.name} (level {dairy.level})")

        trucks = await activities_dao.create_activity_tree(
            name="Грузовые", parent_id=auto.id
        )
        print(f"Created activity: {trucks.name} (level {trucks.level})")

        cars = await activities_dao.create_activity_tree(
            name="Легковые", parent_id=auto.id
        )
        print(f"Created activity: {cars.name} (level {cars.level})")

        # Уровень 3
        parts = await activities_dao.create_activity_tree(
            name="Запчасти", parent_id=cars.id
        )
        print(f"Created activity: {parts.name} (level {parts.level})")

        accessories = await activities_dao.create_activity_tree(
            name="Аксессуары", parent_id=cars.id
        )
        print(f"Created activity: {accessories.name} (level {accessories.level})")

        print("\nCreating organizations...")
        organizations_dao = OrganizationDAO(session)
        # Создаем организации
        organizations_data = [
            OrganizationCreate(
                name='ООО "Рога и Копыта"',
                building_id=buildings[0].id,
                phones=["2-222-222", "3-333-333"],
                activity_ids=[meat.id, dairy.id]
            ),
            OrganizationCreate(
                name='ИП "Молочный рай"',
                building_id=buildings[1].id,
                phones=["8-923-666-13-13"],
                activity_ids=[dairy.id]
            ),
            OrganizationCreate(
                name='ООО "АвтоМир"',
                building_id=buildings[2].id,
                phones=["8-800-555-35-35", "8-812-123-45-67"],
                activity_ids=[cars.id, parts.id, accessories.id]
            ),
            OrganizationCreate(
                name='ЗАО "ГрузовичкоФ"',
                building_id=buildings[3].id,
                phones=["8-383-222-33-44"],
                activity_ids=[trucks.id, parts.id]
            ),
            OrganizationCreate(
                name='ООО "Мясокомбинат №1"',
                building_id=buildings[0].id,
                phones=["8-495-111-22-33"],
                activity_ids=[meat.id]
            ),
            OrganizationCreate(
                name='ИП "Автозапчасти+"',
                building_id=buildings[1].id,
                phone_numbers=["8-495-777-88-99"],
                activity_ids=[parts.id]
            ),
        ]

        for org_data in organizations_data:
            org = await organizations_dao.create_organization(org_data=org_data)
            print(f"Created organization: {org.name}")
        await session.commit()
        print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_data())