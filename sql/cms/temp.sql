with overpayment_sum as (
	select
		d.case_id,
		sum(pd.overpayment) overpayment
	from 
		payed_debts pd, 
		debts d 
	where 
		pd.debt_id = d.debt_id and 
		pd.deleted_at is null and 
		d.deleted_at is null
	group by 
		d.case_id
), last_payment_date as (
	select 
		p.case_id, 
		max(p.payment_date) as last_payment_date
	from 
		payments p 
	where 
		p.deleted_at is null 
	group by 
		p.case_id
)
select 
	c.partner_case_number,
	a.account_number,
	p.first_name,
	p.last_name,
	p.birth_name,
	c.closed_at, 
	c.current_amount, 
	c.current_interest_amount,
	os.overpayment,
	lpd.last_payment_date,
	c.current_due_date,
	h.valid_to,
	c.case_id, 
	a.bank_account_id,
	p.person_id
from 
	cases c,
	overpayment_sum os,
	last_payment_date lpd,
	account_holders h,
	persons p,
	debtors d,
	bank_accounts a
where 
	c.deleted_at is null and 
	(c.closed_at is null or (c.closed_at is not null and os.overpayment > 0)) and
	os.case_id = c.case_id and 
	lpd.case_id = c.case_id and
	h.person_id = p.person_id and 
	h.deleted_at is null and
	p.person_id = d.person_id and
	d.deleted_at is null and
	d.case_id = c.case_id and 
	a.bank_account_id = h.bank_account_id and 
	a.deleted_at is null and 
	h.valid_from < lpd.last_payment_date
