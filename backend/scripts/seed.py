## An idempotent seed script to populate the database with sample data for development and testing.
import asyncio
from sqlalchemy import select
from app.db.models import Base, Platform, Brand, OrderContext
from app.db.session import engine, SessionLocal


async def seed():
    async with SessionLocal() as db:
        # 1. Create platform if it doesn't exist
        result = await db.execute(
            select(Platform).where(Platform.name == "DemoStore")
        )
        platform = result.scalar_one_or_none()

        if platform is None:
            platform = Platform(
                name="DemoStore",
                website_url="https://demostore.com",
            )
            db.add(platform)
            await db.flush()

        # 2. Create brand if it doesn't exist
        result = await db.execute(
            select(Brand).where(Brand.slug == "acme-electronics")
        )
        brand = result.scalar_one_or_none()

        if brand is None:
            brand = Brand(
                name="Acme Electronics",
                slug="acme-electronics",
            )
            db.add(brand)
            await db.flush()

        # 3. Create demo order if it doesn't exist
        result = await db.execute(
            select(OrderContext).where(
                OrderContext.order_id == "ORDER-1001"
            )
        )
        order = result.scalar_one_or_none()

        if order is None:
            order = OrderContext(
                order_id="ORDER-1001",
                platform_id=platform.id,
                brand_id=brand.id,
                product_category="electronics",
            )
            db.add(order)

        await db.commit()

        print("Seed completed successfully!")
        print(f"Platform: {platform.name}")
        print(f"Brand: {brand.name}")
        print(f"Demo order: {order.order_id}")


if __name__ == "__main__":
    asyncio.run(seed())