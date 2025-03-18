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
		SUM(c.amount) AS total_amount,
        SUM(c.current_amount) AS total_current_amount,
        SUM(c.current_interest_amount) AS total_current_interest_amount,
		AVG(c.amount) AS avg_amount,
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
),
payments_summary as (
	select 
		r.partner_id, 
		sum(p.amount) sum_payment
	from 
		payments p, 
		cases c,
		purchases r
	where 
		p.case_id = c.case_id and
		c.purchase_id = r.purchase_id
	group by 
		r.partner_id
),
coverage_summary as (
	select 
		p.partner_id,
		sum(t.debt_amount_covered) as debt_amount_covered,
		sum(t.interest_amount_covered) as interest_amount_covered
	from 
		payed_debts t, 
		debts d,
		cases c,
		purchases p
	where 
		d.debt_id = t.debt_id and
		c.case_id = d.case_id and
		p.purchase_id = c.purchase_id
	group by
		p.partner_id
),
interest_summary as (
	select
    	p.partner_id,
    	sum(d.interest_amount) as sum_interest
	from
    	debts d,
		cases c,
		purchases p
	where 
		c.case_id = d.case_id and
		p.purchase_id = c.purchase_id
	group by
		p.partner_id
)
SELECT 
	r."name" AS partner_neve,
    
	to_char(ps.total_purchase_value, '999 999 999 999D999') AS vasarlasi_ertek,
	to_char(cs.total_amount, '999 999 999 999D999') AS vasarolt_ugyek_osszerteke,
	ps.purchase_count AS vasarlasok_szama,
	cs.total_cases AS vasarolt_ugyek_szama,
	ds.total_debtors AS ugyfelek_szama,
	ps.first_purchase AS elso_vasarlas,
	ps.last_purchase AS utolso_vasarlas,

    to_char(cs.total_amount, '999 999 999 999D999') AS teljes_toke_tartozas,
    to_char(ct.debt_amount_covered, '999 999 999 999D999') as leosztott_toke_tartozas,
    to_char(cs.total_amount - ct.debt_amount_covered, '999 999 999 999D999') as befizetetlen_toke_tartozas,
    to_char(cs.total_current_amount, '999 999 999 999D999') as nyilvantartott_befizetetlen_toke_tartozas,
    
    to_char(it.sum_interest, '999 999 999 999D999') as nyilvantartott_kamat,
    to_char(ct.interest_amount_covered, '999 999 999 999D999') AS leosztott_kamat,
    to_char(it.sum_interest - ct.interest_amount_covered, '999 999 999 999D999') as befizetetlen_kamat,
    to_char(cs.total_current_interest_amount, '999 999 999 999D999') as nyilvantartott_befizetetlen_kamat_tartozas,
    
	to_char(ts.sum_payment, '999 999 999 999D999') AS osszes_befizetes,
	to_char(ct.debt_amount_covered + ct.interest_amount_covered, '999 999 999 999D999') AS leosztas_osszesen
FROM partners r
LEFT JOIN purchase_summary ps ON r.partner_id = ps.partner_id
LEFT JOIN case_summary cs ON r.partner_id = cs.partner_id
LEFT JOIN debtor_summary ds ON r.partner_id = ds.partner_id
LEFT JOIN payments_summary ts ON ts.partner_id = r.partner_id
LEFT JOIN coverage_summary ct ON ct.partner_id = r.partner_id
LEFT JOIN interest_summary it ON it.partner_id = r.partner_id
ORDER BY r."name" ASC
            '''
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
