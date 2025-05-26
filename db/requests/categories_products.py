from sqlalchemy import select, func

from config_data.constants import PAGE_SIZE
from db.models import Catalog, Product
from db.connection import database


async def get_paginated_categories(page: int = 1, page_size: int = PAGE_SIZE):
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
    category_id: int, page: int = 1, page_size: int = PAGE_SIZE
):
    offset = (page - 1) * page_size

    async with database.session as session:
        result = await session.execute(
            select(Catalog)
            .where(Catalog.parent_id == category_id)
            .offset(offset)
            .limit(page_size)
            .order_by(Catalog.id)
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

async def get_products_by_catalog(
    catalog_id: int, page: int = 1
):
    offset = (page - 1)

    async with database.session as session:
        result = await session.execute(
            select(Product)
            .where(Product.catalog_id == catalog_id)
            .offset(offset)
            .limit(1)
            .order_by(Product.id)
        )
        product = result.scalar_one_or_none()

        total_result = await session.execute(
            select(func.count()).select_from(
                select(Product)
                .where(Product.catalog_id == catalog_id)
                .subquery()
            )
        )
        total_count = total_result.scalar_one()

        return product, total_count
