"""Database initialization and seed data script."""
import logging
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.core.security import get_password_hash
from app.models.category import Category, DEFAULT_CATEGORIES
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize the database by creating all tables."""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


def seed_categories(db: Session) -> None:
    """Seed default categories if they don't exist."""
    logger.info("Seeding categories...")
    
    for cat_data in DEFAULT_CATEGORIES:
        existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
            logger.info(f"Created category: {cat_data['name']}")
    
    db.commit()
    logger.info("Categories seeded successfully.")


def seed_admin_user(db: Session) -> None:
    """Seed the default admin user if it doesn't exist."""
    logger.info("Seeding admin user...")
    
    # Check if admin user exists
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin_user = User(
            username="admin",
            email="admin@solarproducts.local",
            full_name="System Administrator",
            hashed_password=get_password_hash("admin123"),  # Change in production!
            is_admin=True,
            is_active=True,
        )
        db.add(admin_user)
        db.commit()
        logger.info("Created default admin user: admin / admin123")
        logger.warning("IMPORTANT: Change the admin password in production!")
    else:
        logger.info("Admin user already exists.")


def seed_all() -> None:
    """Run all seed functions."""
    logger.info("Starting database seeding...")
    
    db = SessionLocal()
    try:
        init_db()
        seed_categories(db)
        seed_admin_user(db)
        logger.info("Database seeding completed successfully!")
    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()
