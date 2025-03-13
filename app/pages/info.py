from math import e
from sqlalchemy import create_engine, text
from nicegui import ui
import pandas as pd
import theme
import os
import config.database


def show_info():
    with theme.frame('Replikáció információk'):
        ui.page_title('Replikáció információk')

        try:
            engine_1 = create_engine(config.database.SRV1_DB_CONN_INFO)
            connection_1 = engine_1.connect()
        except:
            pass

        try:
            engine_2 = create_engine(config.database.SRV2_DB_CONN_INFO)
            connection_2 = engine_2.connect()
        except:
            pass

        try:
            engine_3 = create_engine(config.database.SRV1_DB_CONN_INFO)
            connection_3 = engine_3.connect()
        except:
            pass

        #sector data for dropdown
        def get_info_1():
            try:
                return pd.read_sql_query('select r.usename, r.application_name, r.sync_state from pg_stat_replication r', con=connection_1)
            except:
                return None

        def get_info_2():
            try:
                return pd.read_sql_query('select r.status, r.sender_host, r.sender_port from pg_stat_wal_receiver r', con=connection_1)
            except:
                return None

        def get_info_3():
            try:
                return pd.read_sql_query('select r.usename, r.application_name, r.sync_state from pg_stat_replication r', con=connection_2)
            except:
                return None
        
        def get_info_4():
            try:
                return pd.read_sql_query('select r.status, r.sender_host, r.sender_port from pg_stat_wal_receiver r', con=connection_2)
            except:
                return None

        def get_info_5():
            try:
                return pd.read_sql_query('show pool_nodes', con=connection_3)
            except:
                return None
            
        def get_n(connection):
            try:
                return pd.read_sql_query('select count(*) from test', con=connection)
            except:
                return None

        def shutdown_docker_host():
            os.system("docker stop postgres-1")

        def restart_docker_host():
            os.system("docker restart pgpool")

        with ui.card():
            ui.label('pgpool').style('color: #6E93D6; font-size: 300%; font-weight: 300')
            with ui.card():
                ui.label('pool_nodes')
                try:
                    data_table = ui.table.from_pandas(get_info_5()).classes('w-full')
                except:
                    pass
                ui.button('PGPOOL RESTART', on_click=restart_docker_host).props('color=red')

        with ui.row():
            with ui.card():
                ui.label('postgres-1').style('color: #6E93D6; font-size: 300%; font-weight: 300')
                with ui.card():
                    ui.label('pg_stat_replication')
                    try:
                        data_table = ui.table.from_pandas(get_info_1()).classes('w-full')
                    except:
                        pass
                    ui.label('pg_stat_wal_receiver')
                    try:
                        data_table = ui.table.from_pandas(get_info_2()).classes('w-full')
                    except:
                        pass
                    ui.label('Record count in test table in postgres-1')
                    try:
                        data_table = ui.table.from_pandas(get_n(connection_1)).classes('w-full')
                    except:
                        pass
                ui.button('POSTGERS-1 LEALLITASA', on_click=shutdown_docker_host).props('color=red')
            
            with ui.card():
                ui.label('postgres-2').style('color: #6E93D6; font-size: 300%; font-weight: 300')
                with ui.card():
                    ui.label('pg_stat_replication')
                    try:
                        data_table = ui.table.from_pandas(get_info_3()).classes('w-full')
                    except:
                        pass
                    ui.label('pg_stat_wal_receiver')
                    try:
                        data_table = ui.table.from_pandas(get_info_4()).classes('w-full')
                    except:
                        pass
                    ui.label('Record count in test table in postgres-2')
                    try:
                        data_table = ui.table.from_pandas(get_n(connection_2)).classes('w-full')
                    except:
                        pass
        
        connection_1.close()
        connection_2.close()
        connection_3.close()
