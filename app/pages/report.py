from math import e
from sqlalchemy import create_engine, text
from nicegui import ui
import pandas as pd
import theme
import config.database


def show_report():
    with theme.frame('Riport'):
        ui.page_title('Riport')

        sql = f'''
                    WITH purchase_summary AS (
                        SELECT 
                            p.partner_id,
                            SUM(p.batch_purchase_value) AS total_purchase_value,
                            COUNT(DISTINCT p.batch_number) AS purchase_count,
                            MIN(p.purchased_at) AS first_purchase,
                            MAX(p.purchased_at) AS last_purchase
                        FROM purchases p
                        GROUP BY p.partner_id
                    ),
                    case_summary AS (
                        SELECT 
                            p.partner_id,
                            SUM(c.calculated_purchase_value) AS total_calculated_value,
                            SUM(c.amount) AS total_calculated_amount,
                            COUNT(DISTINCT c.case_id) AS total_cases
                        FROM purchases p
                        JOIN cases c ON c.purchase_id = p.purchase_id
                        GROUP BY p.partner_id
                    ),
                    debtor_summary AS (
                        SELECT 
                            p.partner_id,
                            COUNT(DISTINCT d.person_id) AS total_debtors
                        FROM purchases p
                        JOIN cases c ON c.purchase_id = p.purchase_id
                        JOIN debtors d ON d.case_id = c.case_id
                        GROUP BY p.partner_id
                    )
                    SELECT 
                        r."name" AS partner_neve,
                        ps.total_purchase_value AS vasarlasi_ertek,
                        cs.total_calculated_value AS vasarlas_kalkulalt_erteke,
                        cs.total_calculated_amount AS vasarolt_ugyek_osszerteke,
                        cs.total_calculated_amount - ps.total_purchase_value AS kulonbozet,
                        ps.purchase_count AS vasarlasok_szama,
                        cs.total_cases AS vasarolt_ugyek_szama,
                        ds.total_debtors AS ugyfelek_szama,
                        ps.first_purchase AS elso_vasarlas,
                        ps.last_purchase AS utolso_vasarlas
                    FROM partners r
                    JOIN purchase_summary ps ON r.partner_id = ps.partner_id
                    JOIN case_summary cs ON r.partner_id = cs.partner_id
                    JOIN debtor_summary ds ON r.partner_id = ds.partner_id
                    ORDER BY r."name" ASC'''
        with ui.card():
            ui.label('Osszegzett adatok').style('color: #6E93D6; font-size: 300%; font-weight: 300')
            try:
                engine = create_engine(config.database.SRV1_DB_CONN_INFO)
                connection = engine.connect()
                data = pd.read_sql_query(text(sql), con=connection)
                data_table = ui.table.from_pandas(data).classes('w-full')
                connection.close()
            except:
                pass
