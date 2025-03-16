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
            srv1_conn = engine_1.connect()
        except:
            pass

        try:
            engine_2 = create_engine(config.database.SRV2_DB_CONN_INFO)
            srv2_conn = engine_2.connect()
        except:
            pass

        try:
            engine_3 = create_engine(config.database.POOL_CONN_INFO)
            pool_conn = engine_3.connect()
        except:
            pass

        try:
            engine_4 = create_engine(config.database.FIN_DB_CONN_INFO)
            fin_conn = engine_4.connect()
        except:
            pass

        #sector data for dropdown
        def get_info_pg_stat_replication(conn):
            try:
                return pd.read_sql_query('select r.usename, r.application_name, r.sync_state, r.replay_lag from pg_stat_replication r', con=conn)
            except:
                return None

        def get_info_pg_stat_wal_receiver(conn):
            try:
                return pd.read_sql_query('select r.status, r.sender_host, r.sender_port from pg_stat_wal_receiver r', con=conn)
            except:
                return None

        def get_info_pool_nodes(conn):
            try:
                return pd.read_sql_query('show pool_nodes', con=conn)
            except:
                return None
            
        def get_n_test(conn):
            try:
                return pd.read_sql_query('select count(*) from test', con=conn)
            except:
                return None

        def shutdown_docker_host():
            os.system("docker stop srv1")

        with ui.card():
            ui.label('pgpool').style('color: #6E93D6; font-size: 300%; font-weight: 300')
            with ui.card():
                ui.label('pool_nodes')
                try:
                    data_table = ui.table.from_pandas(get_info_pool_nodes(pool_conn)).classes('w-full')
                except:
                    pass

        with ui.row():
            with ui.card():
                ui.label('srv1').style('color: #6E93D6; font-size: 300%; font-weight: 300')
                with ui.card():
                    ui.label('pg_stat_replication')
                    try:
                        data_table = ui.table.from_pandas(get_info_pg_stat_replication(srv1_conn)).classes('w-full')
                    except:
                        pass
                    ui.label('pg_stat_wal_receiver')
                    try:
                        data_table = ui.table.from_pandas(get_info_pg_stat_wal_receiver(srv1_conn)).classes('w-full')
                    except:
                        pass
                    ui.label('Record count in test table')
                    try:
                        data_table = ui.table.from_pandas(get_n_test(srv1_conn)).classes('w-full')
                    except:
                        pass
                ui.button('SRV1 LEALLITASA', on_click=shutdown_docker_host).props('color=red')

            with ui.card():
                ui.label('srv2').style('color: #6E93D6; font-size: 300%; font-weight: 300')
                with ui.card():
                    ui.label('pg_stat_replication')
                    try:
                        data_table = ui.table.from_pandas(get_info_pg_stat_replication(srv2_conn)).classes('w-full')
                    except:
                        pass
                    ui.label('pg_stat_wal_receiver')
                    try:
                        data_table = ui.table.from_pandas(get_info_pg_stat_wal_receiver(srv2_conn)).classes('w-full')
                    except:
                        pass
                    ui.label('Record count in test table')
                    try:
                        data_table = ui.table.from_pandas(get_n_test(srv2_conn)).classes('w-full')
                    except:
                        pass

            with ui.card():
                ui.label('fin').style('color: #6E93D6; font-size: 300%; font-weight: 300')
                with ui.card():
                    ui.label('pg_stat_replication')
                    try:
                        data_table = ui.table.from_pandas(get_info_pg_stat_replication(fin_conn)).classes('w-full')
                    except:
                        pass
                    ui.label('pg_stat_wal_receiver')
                    try:
                        data_table = ui.table.from_pandas(get_info_pg_stat_wal_receiver(fin_conn)).classes('w-full')
                    except:
                        pass
                    ui.label('Record count in test table')
                    try:
                        data_table = ui.table.from_pandas(get_n_test(fin_conn)).classes('w-full')
                    except:
                        pass

        try:
            srv1_conn.close()
        except:
            pass
        try:
            srv2_conn.close()
        except:
            pass
        try:
            pool_conn.close()
        except:
            pass
        try:
            fin_conn.close()
        except:
            pass
