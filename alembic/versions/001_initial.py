"""Initial migration - create all tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('is_admin', sa.Boolean(), default=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('country', sa.String(100), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('support_email', sa.String(255), nullable=True),
        sa.Column('support_phone', sa.String(50), nullable=True),
        sa.Column('warranty_info', sa.Text(), nullable=True),
        sa.Column('avg_response_time_hours', sa.Float(), default=0.0),
        sa.Column('support_rating', sa.Float(), default=0.0),
        sa.Column('verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_companies_id', 'companies', ['id'])
    op.create_index('ix_companies_name', 'companies', ['name'], unique=True)

    # Create categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_categories_id', 'categories', ['id'])
    op.create_index('ix_categories_name', 'categories', ['name'], unique=True)

    # Create products table
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('datasheet_file_url', sa.String(500), nullable=False),
        sa.Column('manual_file_url', sa.String(500), nullable=True),
        sa.Column('validation_status', sa.Enum('pending', 'approved', 'rejected', name='validationstatus'), default='pending'),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_products_id', 'products', ['id'])
    op.create_index('ix_products_company_id', 'products', ['company_id'])
    op.create_index('ix_products_category_id', 'products', ['category_id'])
    op.create_index('ix_products_model_name', 'products', ['model_name'])

    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('datasheet', 'manual', name='documenttype'), nullable=False),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('extracted_text', sa.Text(), nullable=True),
        sa.Column('extraction_status', sa.Enum('pending', 'success', 'failed', name='extractionstatus'), default='pending'),
        sa.Column('extraction_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_documents_id', 'documents', ['id'])
    op.create_index('ix_documents_product_id', 'documents', ['product_id'])

    # Create product_specifications table
    op.create_table(
        'product_specifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('spec_key', sa.String(100), nullable=False),
        sa.Column('spec_value', sa.String(255), nullable=False),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('confidence_score', sa.Float(), default=1.0),
        sa.Column('source_location', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_product_specifications_id', 'product_specifications', ['id'])
    op.create_index('ix_product_specifications_product_id', 'product_specifications', ['product_id'])
    op.create_index('ix_product_specifications_spec_key', 'product_specifications', ['spec_key'])

    # Create company_metrics table
    op.create_table(
        'company_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('response_time_hours', sa.Float(), default=0.0),
        sa.Column('issue_resolution_rate', sa.Float(), default=0.0),
        sa.Column('failure_rate', sa.Float(), default=0.0),
        sa.Column('user_rating', sa.Float(), default=0.0),
        sa.Column('total_reviews', sa.Integer(), default=0),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_company_metrics_id', 'company_metrics', ['id'])
    op.create_index('ix_company_metrics_company_id', 'company_metrics', ['company_id'])

    # Create reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('issue_type', sa.String(100), nullable=True),
        sa.Column('reviewer_name', sa.String(100), nullable=True),
        sa.Column('reviewer_email', sa.String(255), nullable=True),
        sa.Column('is_verified_purchase', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id']),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reviews_id', 'reviews', ['id'])
    op.create_index('ix_reviews_product_id', 'reviews', ['product_id'])
    op.create_index('ix_reviews_company_id', 'reviews', ['company_id'])


def downgrade() -> None:
    op.drop_table('reviews')
    op.drop_table('company_metrics')
    op.drop_table('product_specifications')
    op.drop_table('documents')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('companies')
    op.drop_table('users')
