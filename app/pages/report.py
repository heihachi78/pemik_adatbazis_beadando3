from math import e
from sqlalchemy import create_engine, text
from nicegui import ui
import pandas as pd
import theme
import config.database


def show_report():
    with theme.frame('Riport'):
        ui.page_title('Riport')

        sql = f'select partner_neve, vasarlasi_ertek, vasarolt_ugyek_osszerteke, vasarlasok_szama, vasarolt_ugyek_szama, nyitott_ugyek_szama, ugyfelek_szama, elso_vasarlas, utolso_vasarlas, leosztas_osszesen from partner_statistics_v'
        ui.label('Osszegzett adatok 1').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            engine = create_engine(config.database.POOL_CONN_INFO)
            connection = engine.connect()
            data = pd.read_sql_query(text(sql), con=connection)
            data_table = ui.table.from_pandas(data).classes('w-full')
            connection.close()
        except:
            pass

        sql = f'select partner_neve, vasarlasi_ertek, teljes_toke_tartozas, leosztott_toke_tartozas, befizetetlen_toke_tartozas, nyilvantartott_befizetetlen_toke_tartozas, nyilvantartott_kamat, leosztott_kamat, befizetetlen_kamat, nyilvantartott_befizetetlen_kamat_tartozas, osszes_befizetes, tulfizetes, leosztas_osszesen from partner_statistics_v'
        ui.label('Osszegzett adatok 2').style('color: #6E93D6; font-size: 300%; font-weight: 300')
        try:
            engine = create_engine(config.database.POOL_CONN_INFO)
            connection = engine.connect()
            data = pd.read_sql_query(text(sql), con=connection)
            data_table = ui.table.from_pandas(data).classes('w-full')
            connection.close()
        except:
            pass
