"""Initialise database

Revision ID: 5d83af1f4cb3
Revises: 
Create Date: 2022-01-27 09:33:34.317792

"""
import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5d83af1f4cb3"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "postcodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pcd", sa.String(length=7), nullable=True),
        sa.Column("pcd2", sa.String(length=7), nullable=True),
        sa.Column("pcds", sa.String(length=7), nullable=True),
        sa.Column("dointr", sa.Date(), nullable=True),
        sa.Column("doterm", sa.Date(), nullable=True),
        sa.Column("usertype", sa.Integer(), nullable=True),
        sa.Column("oseast1m", sa.Integer(), nullable=True),
        sa.Column("osnrth1m", sa.Integer(), nullable=True),
        sa.Column("osgrdind", sa.Integer(), nullable=True),
        sa.Column("oa11", sa.String(length=9), nullable=True),
        sa.Column("cty", sa.String(length=9), nullable=True),
        sa.Column("ced", sa.String(length=9), nullable=True),
        sa.Column("laua", sa.String(length=9), nullable=True),
        sa.Column("ward", sa.String(length=9), nullable=True),
        sa.Column("hlthau", sa.String(length=9), nullable=True),
        sa.Column("nhser", sa.String(length=9), nullable=True),
        sa.Column("ctry", sa.String(length=9), nullable=True),
        sa.Column("rgn", sa.String(length=9), nullable=True),
        sa.Column("pcon", sa.String(length=9), nullable=True),
        sa.Column("eer", sa.String(length=9), nullable=True),
        sa.Column("teclec", sa.String(length=9), nullable=True),
        sa.Column("ttwa", sa.String(length=9), nullable=True),
        sa.Column("pct", sa.String(length=9), nullable=True),
        sa.Column("nuts", sa.String(length=9), nullable=True),
        sa.Column("npark", sa.String(length=9), nullable=True),
        sa.Column("lsoa11", sa.String(length=9), nullable=True),
        sa.Column("msoa11", sa.String(length=9), nullable=True),
        sa.Column("wz11", sa.String(length=9), nullable=True),
        sa.Column("ccg", sa.String(length=9), nullable=True),
        sa.Column("bua11", sa.String(length=9), nullable=True),
        sa.Column("buasd11", sa.String(length=9), nullable=True),
        sa.Column("ru11ind", sa.String(length=2), nullable=True),
        sa.Column("oac11", sa.String(length=3), nullable=True),
        sa.Column("lat", sa.Float(), nullable=True),
        sa.Column("long", sa.Float(), nullable=True),
        sa.Column("lep1", sa.String(length=9), nullable=True),
        sa.Column("lep2", sa.String(length=9), nullable=True),
        sa.Column("pfa", sa.String(length=9), nullable=True),
        sa.Column("imd", sa.Integer(), nullable=True),
        sa.Column("calncv", sa.String(length=9), nullable=True),
        sa.Column("stp", sa.String(length=9), nullable=True),
        sa.Column(
            "geom",
            geoalchemy2.types.Geometry(
                geometry_type="POINT",
                srid=4326,
                from_text="ST_GeomFromEWKT",
                name="geometry",
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_postcodes_pcd"), "postcodes", ["pcd"], unique=True)
    op.create_index(op.f("ix_postcodes_pcd2"), "postcodes", ["pcd2"], unique=True)
    op.create_index(op.f("ix_postcodes_pcds"), "postcodes", ["pcds"], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_postcodes_pcds"), table_name="postcodes")
    op.drop_index(op.f("ix_postcodes_pcd2"), table_name="postcodes")
    op.drop_index(op.f("ix_postcodes_pcd"), table_name="postcodes")
    op.drop_table("postcodes")
    # ### end Alembic commands ###
