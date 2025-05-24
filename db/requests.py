from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from db.models import Catalog
from db.connection import database


async def get_paginated_categories(page: int = 1, page_size: int = 4):
    offset = (page - 1) * page_size

    async with database.session as session:
        result = await session.execute(
            select(Catalog)
            .where(Catalog.parent_id.is_(None))
            .offset(offset)
            .limit(page_size)
            .order_by(Catalog.id)
        )
        categories = result.scalars().all()

        total_result = await session.execute(
            select(func.count()).select_from(
                select(Catalog)
                .where(Catalog.parent_id.is_(None))
                .subquery()
            )
        )
        total_count = total_result.scalar_one()

        return categories, total_count

async def get_subcategories_by_category(
    category_id: int, page: int = 1, page_size: int = 10
):
    offset = (page - 1) * page_size

    async with database.session as session:
        result = await session.execute(
            select(Catalog)
            .where(Catalog.parent_id == category_id)
            .offset(offset)
            .limit(page_size)
        )
        subcategories = result.scalars().all()

        total_result = await session.execute(
            select(func.count()).select_from(
                select(Catalog)
                .where(Catalog.parent_id == category_id)
                .subquery()
            )
        )
        total_count = total_result.scalar_one()

        return subcategories, total_count