from sqlalchemy import ARRAY, String, func, select, text
from sqlalchemy.types import UserDefinedType

from db.tables.operations.select import reflect_table_from_oid
from db.types import base
from db.types.base import get_qualifier_prefix
from db.types.operations.cast import MONEY_ARR_FUNC_NAME

MATHESAR_MONEY = base.MathesarCustomType.MATHESAR_MONEY.value
DB_TYPE = base.get_qualified_name(MATHESAR_MONEY)


class MathesarMoney(UserDefinedType):

    def get_col_spec(self, **_):
        return DB_TYPE.upper()


def install(engine):
    drop_domain_query = f"""
    DROP DOMAIN IF EXISTS {DB_TYPE};
    """
    create_domain_query = f"""
    CREATE DOMAIN {DB_TYPE} AS NUMERIC;
    """

    with engine.begin() as conn:
        conn.execute(text(drop_domain_query))
        conn.execute(text(create_domain_query))
        conn.commit()


def get_money_array(table_oid, engine, column_attnum):
    table = reflect_table_from_oid(table_oid, engine)
    column_name = column_attnum
    with engine.begin() as conn:
        package_func = getattr(func, get_qualifier_prefix())
        money_func = getattr(package_func, MONEY_ARR_FUNC_NAME)
        money_select = money_func((table.c[column_name]), type_=ARRAY(String)).label('x')
        sel = select(money_select).where(money_select[4] is not None)
        data = conn.execute(sel).fetchone()
        if data is None:
            return None
        else:
            return data[0]
