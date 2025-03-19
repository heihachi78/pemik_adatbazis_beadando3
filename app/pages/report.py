from math import e
from sqlalchemy import create_engine, text
from nicegui import ui
import pandas as pd
import theme
import config.database


def show_report():
    with theme.frame('Riport'):
        ui.page_title('Riport')

        sql = f'select * from partner_statistics_v'
        with ui.card():
            ui.label('Osszegzett adatok').style('color: #6E93D6; font-size: 300%; font-weight: 300')
            try:
                engine = create_engine(config.database.POOL_CONN_INFO)
                connection = engine.connect()
                data = pd.read_sql_query(text(sql), con=connection)
                data_table = ui.table.from_pandas(data).classes('w-full')
                connection.close()
            except:
                pass
