"""Add Chemical, Tag, and full nutrients

Revision ID: 7f5ca7b1c6f4
Revises: 65b0a483ed78
Create Date: 2025-07-20 22:46:29.976135
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7f5ca7b1c6f4'
down_revision: Union[str, Sequence[str], None] = '65b0a483ed78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('chemicals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('ai_percentage', sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column('cost_per_unit', sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_chemicals_id'), 'chemicals', ['id'], unique=False)
    op.create_table('activity_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_logs_id'), 'activity_logs', ['id'], unique=False)
    op.create_table('farms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('location', sa.Text(), nullable=True),
        sa.Column('total_acres', sa.Float(), nullable=True),
        sa.Column('soil_type', sa.String(length=100), nullable=True),
        sa.Column('irrigation_type', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_farms_id'), 'farms', ['id'], unique=False)
    op.create_table('price_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.Column('old_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('new_price', sa.DECIMAL(precision=10, scale=2), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_price_history_id'), 'price_history', ['id'], unique=False)
    op.create_table('blend_chemicals',
        sa.Column('blend_id', sa.Integer(), nullable=True),
        sa.Column('chemical_id', sa.Integer(), nullable=True),
        sa.Column('ai_percentage', sa.Float(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['blend_id'], ['blends.id'], ),
        sa.ForeignKeyConstraint(['chemical_id'], ['chemicals.id'], )
    )
    op.create_table('blend_ingredients',
        sa.Column('blend_id', sa.Integer(), nullable=True),
        sa.Column('ingredient_id', sa.Integer(), nullable=True),
        sa.Column('percentage', sa.Float(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['blend_id'], ['blends.id'], ),
        sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], )
    )
    op.create_table('fields',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('farm_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('acres', sa.Float(), nullable=True),
        sa.Column('crop_type', sa.String(length=100), nullable=True),
        sa.Column('planting_date', sa.DateTime(), nullable=True),
        sa.Column('harvest_date', sa.DateTime(), nullable=True),
        sa.Column('soil_test_date', sa.DateTime(), nullable=True),
        sa.Column('soil_ph', sa.Float(), nullable=True),
        sa.Column('soil_om', sa.Float(), nullable=True),
        sa.Column('soil_cec', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fields_id'), 'fields', ['id'], unique=False)
    op.create_table('tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tag_number', sa.String(length=50), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=True),
        sa.Column('blend_id', sa.Integer(), nullable=True),
        sa.Column('ingredients', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['blend_id'], ['blends.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tag_number')
    )
    op.create_index(op.f('ix_tags_id'), 'tags', ['id'], unique=False)
    op.add_column('blends', sa.Column('code', sa.String(length=50), nullable=True))
    op.add_column('blends', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('blends', sa.Column('is_template', sa.Boolean(), nullable=True))
    op.add_column('blends', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('blends', sa.Column('target_n', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_p', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_k', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_s', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_ca', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_mg', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_fe', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_zn', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_mn', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_b', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('target_cl', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('blends', sa.Column('application_rate', sa.Float(), nullable=True))
    op.add_column('blends', sa.Column('application_unit', sa.String(length=20), nullable=True))
    op.add_column('blends', sa.Column('created_by', sa.Integer(), nullable=True))
    op.add_column('blends', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('blends', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('blends', 'name',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
    op.drop_index('ix_blends_name', table_name='blends')
    op.create_unique_constraint(None, 'blends', ['code'])
    op.create_foreign_key(None, 'blends', 'users', ['created_by'], ['id'])
    op.add_column('customers', sa.Column('code', sa.String(length=20), nullable=True))
    op.add_column('customers', sa.Column('email', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('customers', sa.Column('address', sa.Text(), nullable=True))
    op.add_column('customers', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('state', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('zip_code', sa.String(length=20), nullable=True))
    op.add_column('customers', sa.Column('contact_person', sa.String(length=100), nullable=True))
    op.add_column('customers', sa.Column('tax_id', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('credit_limit', sa.DECIMAL(precision=10, scale=2), nullable=True))
    op.add_column('customers', sa.Column('payment_terms', sa.String(length=50), nullable=True))
    op.add_column('customers', sa.Column('default_margin_type', sa.String(length=20), nullable=True))
    op.add_column('customers', sa.Column('default_margin_value', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('customers', sa.Column('is_active', sa.Boolean(), nullable=True))
    op.add_column('customers', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('customers', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('customers', 'name',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
    op.drop_index('ix_customers_name', table_name='customers')
    op.create_unique_constraint(None, 'customers', ['code'])
    op.add_column('ingredients', sa.Column('calcium', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('magnesium', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('iron', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('manganese', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('chlorine', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('copper', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('molybdenum', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('moisture_content', sa.Float(), nullable=True))
    op.add_column('ingredients', sa.Column('margin_percent', sa.DECIMAL(precision=5, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('fixed_margin', sa.DECIMAL(precision=10, scale=2), nullable=True))
    op.add_column('ingredients', sa.Column('is_available', sa.Boolean(), nullable=True))
    op.add_column('ingredients', sa.Column('min_order_qty', sa.Float(), nullable=True))
    op.add_column('ingredients', sa.Column('max_order_qty', sa.Float(), nullable=True))
    op.add_column('ingredients', sa.Column('display_order', sa.Integer(), nullable=True))
    op.add_column('ingredients', sa.Column('notes', sa.Text(), nullable=True))
    op.add_column('ingredients', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    op.add_column('ingredients', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('ingredients', 'name',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
    op.drop_index('ix_ingredients_name', table_name='ingredients')
    op.create_unique_constraint(None, 'ingredients', ['name'])
    op.create_unique_constraint(None, 'ingredients', ['code'])
    op.add_column('quotes', sa.Column('services', sa.JSON(), nullable=True))
    op.add_column('quotes', sa.Column('application_acres', sa.Float(), nullable=True))
    op.add_column('quotes', sa.Column('cost_per_acre', sa.DECIMAL(precision=10, scale=2), nullable=True))
    op.add_column('quotes', sa.Column('valid_until', sa.DateTime(), nullable=True))
    op.add_column('quotes', sa.Column('internal_notes', sa.Text(), nullable=True))
    op.add_column('quotes', sa.Column('customer_notes', sa.Text(), nullable=True))
    op.alter_column('quotes', 'quote_number',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
    op.alter_column('quotes', 'customer_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)
    op.alter_column('quotes', 'blend_id',
                   existing_type=sa.INTEGER(),
                   nullable=True)
    op.alter_column('quotes', 'unit_price',
                   existing_type=sa.NUMERIC(),
                   nullable=True)
    op.alter_column('quotes', 'total_price',
                   existing_type=sa.NUMERIC(),
                   nullable=True)
    op.alter_column('quotes', 'margin_value',
                   existing_type=sa.NUMERIC(),
                   nullable=True)
    op.alter_column('quotes', 'services_total',
                   existing_type=sa.NUMERIC(),
                   nullable=True)
    op.alter_column('quotes', 'status',
                   existing_type=postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', name='quotestatus'),
                   nullable=True)
    op.alter_column('quotes', 'created_by',
                   existing_type=sa.INTEGER(),
                   nullable=True)
    op.alter_column('quotes', 'created_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   nullable=True)
    op.alter_column('quotes', 'updated_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=True)
    op.drop_index('ix_quotes_quote_number', table_name='quotes')
    op.create_unique_constraint(None, 'quotes', ['quote_number'])
    op.add_column('system_settings', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.alter_column('system_settings', 'value',
                   existing_type=sa.TEXT(),
                   type_=sa.JSON(),
                   nullable=True,
                   postgresql_using='value::json')
    op.alter_column('system_settings', 'description',
                   existing_type=sa.VARCHAR(),
                   type_=sa.Text(),
                   existing_nullable=True)
    op.drop_index('ix_system_settings_key', table_name='system_settings')
    op.create_unique_constraint(None, 'system_settings', ['key'])
    op.alter_column('users', 'created_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   nullable=True,
                   existing_server_default=sa.text('now()'))
    op.alter_column('users', 'updated_at',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=True)
    op.alter_column('users', 'last_login',
                   existing_type=postgresql.TIMESTAMP(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.alter_column('users', 'last_login',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=True)
    op.alter_column('users', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=True)
    op.alter_column('users', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   nullable=False,
                   existing_server_default=sa.text('now()'))
    op.drop_constraint(None, 'system_settings', type_='unique')
    op.create_index('ix_system_settings_key', 'system_settings', ['key'], unique=True)
    op.alter_column('system_settings', 'description',
                   existing_type=sa.Text(),
                   type_=sa.VARCHAR(),
                   existing_nullable=True)
    op.alter_column('system_settings', 'value',
                   existing_type=sa.JSON(),
                   type_=sa.TEXT(),
                   nullable=False)
    op.drop_column('system_settings', 'updated_at')
    op.drop_constraint(None, 'quotes', type_='unique')
    op.create_index('ix_quotes_quote_number', 'quotes', ['quote_number'], unique=True)
    op.alter_column('quotes', 'updated_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   existing_nullable=True)
    op.alter_column('quotes', 'created_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=postgresql.TIMESTAMP(),
                   nullable=False)
    op.alter_column('quotes', 'created_by',
                   existing_type=sa.INTEGER(),
                   nullable=False)
    op.alter_column('quotes', 'status',
                   existing_type=postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', name='quotestatus'),
                   nullable=False)
    op.alter_column('quotes', 'services_total',
                   existing_type=sa.NUMERIC(),
                   nullable=False)
    op.alter_column('quotes', 'margin_value',
                   existing_type=sa.NUMERIC(),
                   nullable=False)
    op.alter_column('quotes', 'total_price',
                   existing_type=sa.NUMERIC(),
                   nullable=False)
    op.alter_column('quotes', 'unit_price',
                   existing_type=sa.NUMERIC(),
                   nullable=False)
    op.alter_column('quotes', 'blend_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)
    op.alter_column('quotes', 'customer_id',
                   existing_type=sa.INTEGER(),
                   nullable=False)
    op.alter_column('quotes', 'quote_number',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
    op.drop_column('quotes', 'customer_notes')
    op.drop_column('quotes', 'internal_notes')
    op.drop_column('quotes', 'valid_until')
    op.drop_column('quotes', 'cost_per_acre')
    op.drop_column('quotes', 'application_acres')
    op.drop_column('quotes', 'services')
    op.drop_constraint(None, 'ingredients', type_='unique')
    op.drop_constraint(None, 'ingredients', type_='unique')
    op.create_index('ix_ingredients_name', 'ingredients', ['name'], unique=False)
    op.alter_column('ingredients', 'name',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
    op.drop_column('ingredients', 'updated_at')
    op.drop_column('ingredients', 'created_at')
    op.drop_column('ingredients', 'notes')
    op.drop_column('ingredients', 'display_order')
    op.drop_column('ingredients', 'max_order_qty')
    op.drop_column('ingredients', 'min_order_qty')
    op.drop_column('ingredients', 'is_available')
    op.drop_column('ingredients', 'fixed_margin')
    op.drop_column('ingredients', 'margin_percent')
    op.drop_column('ingredients', 'moisture_content')
    op.drop_column('ingredients', 'molybdenum')
    op.drop_column('ingredients', 'copper')
    op.drop_column('ingredients', 'chlorine')
    op.drop_column('ingredients', 'manganese')
    op.drop_column('ingredients', 'iron')
    op.drop_column('ingredients', 'magnesium')
    op.drop_column('ingredients', 'calcium')
    op.drop_constraint(None, 'customers', type_='unique')
    op.create_index('ix_customers_name', 'customers', ['name'], unique=False)
    op.alter_column('customers', 'name',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
    op.drop_column('customers', 'updated_at')
    op.drop_column('customers', 'created_at')
    op.drop_column('customers', 'is_active')
    op.drop_column('customers', 'default_margin_value')
    op.drop_column('customers', 'default_margin_type')
    op.drop_column('customers', 'payment_terms')
    op.drop_column('customers', 'credit_limit')
    op.drop_column('customers', 'tax_id')
    op.drop_column('customers', 'contact_person')
    op.drop_column('customers', 'zip_code')
    op.drop_column('customers', 'state')
    op.drop_column('customers', 'city')
    op.drop_column('customers', 'address')
    op.drop_column('customers', 'phone')
    op.drop_column('customers', 'email')
    op.drop_column('customers', 'code')
    op.drop_constraint(None, 'blends', type_='foreignkey')
    op.drop_constraint(None, 'blends', type_='unique')
    op.create_index('ix_blends_name', 'blends', ['name'], unique=False)
    op.alter_column('blends', 'name',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
    op.drop_column('blends', 'updated_at')
    op.drop_column('blends', 'created_at')
    op.drop_column('blends', 'created_by')
    op.drop_column('blends', 'application_unit')
    op.drop_column('blends', 'application_rate')
    op.drop_column('blends', 'target_cl')
    op.drop_column('blends', 'target_b')
    op.drop_column('blends', 'target_mn')
    op.drop_column('blends', 'target_zn')
    op.drop_column('blends', 'target_fe')
    op.drop_column('blends', 'target_mg')
    op.drop_column('blends', 'target_ca')
    op.drop_column('blends', 'target_s')
    op.drop_column('blends', 'target_k')
    op.drop_column('blends', 'target_p')
    op.drop_column('blends', 'target_n')
    op.drop_column('blends', 'is_active')
    op.drop_column('blends', 'is_template')
    op.drop_column('blends', 'description')
    op.drop_column('blends', 'code')
    op.drop_index(op.f('ix_tags_id'), table_name='tags')
    op.drop_table('tags')
    op.drop_index(op.f('ix_fields_id'), table_name='fields')
    op.drop_table('fields')
    op.drop_table('blend_ingredients')
    op.drop_table('blend_chemicals')
    op.drop_index(op.f('ix_price_history_id'), table_name='price_history')
    op.drop_table('price_history')
    op.drop_index(op.f('ix_farms_id'), table_name='farms')
    op.drop_table('farms')
    op.drop_index(op.f('ix_activity_logs_id'), table_name='activity_logs')
    op.drop_table('activity_logs')
    op.drop_index(op.f('ix_chemicals_id'), table_name='chemicals')
    op.drop_table('chemicals')
