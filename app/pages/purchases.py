from datetime import date
from sqlalchemy import create_engine, text
from nicegui import ui, run
from datetime import datetime
import pandas as pd
import theme
import config.database
import process.load_purchase_data



def show_purchases():
    with theme.frame('Vasarlasok karbantartása'):
        ui.page_title('Vasarlasok karbantartása')

        engine = create_engine(config.database.SRV1_DB_CONN_INFO)
        connection = engine.connect()


        #sector data for dropdown
        def get_partners():
            qr = pd.read_sql_query('SELECT partner_id, name FROM partners WHERE deleted_at is null ORDER BY name', con=connection)
            ret = {}
            for i in range(len(qr)):
                ret[int(qr['partner_id'][i])] = qr['name'][i]
            return ret


        #database functions
        def select_rows():
            return pd.read_sql_query('SELECT p.purchase_id, p.partner_id, s.name as partner_name, p.batch_number, p.purchased_at, p.batch_purchase_value, p.created_at, p.updated_at, p.deleted_at FROM purchases p, partners s WHERE p.partner_id = s.partner_id and p.deleted_at is null ORDER BY p.purchase_id desc', con=connection)


        def insert_row(batch_number: str, partner_id: int, purchased_at: date, batch_purchase_value: int):
            connection.execute(text("insert into purchases (batch_number, partner_id, batch_purchase_value, purchased_at) values (:batch_number, :partner_id, :batch_purchase_value, :purchased_at)"), 
                               {"batch_number": batch_number, "partner_id": partner_id, "batch_purchase_value": batch_purchase_value, "purchased_at": purchased_at})
            connection.commit()
            ui.notify('Az új rekord felvétele sikeres volt.')
            return select_rows()


        def delete_row(purchase_id: int):
            connection.execute(text("update purchases set deleted_at = now() where purchase_id = :purchase_id"), {"purchase_id": purchase_id})
            connection.commit()
            ui.notify('A rekord törölve lett.')
            return select_rows()


        def update_row(purchase_id: int, batch_number: str, partner_id: int, purchased_at: date, batch_purchase_value: int):
            connection.execute(text("update purchases set batch_number = :batch_number, partner_id = :partner_id, purchased_at = :purchased_at, batch_purchase_value = :batch_purchase_value, updated_at = now() where purchase_id = :purchase_id"), 
                               {"purchase_id": purchase_id, "batch_number": batch_number, "partner_id": partner_id, "purchased_at": purchased_at, "batch_purchase_value": batch_purchase_value})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()


        def generate(partner_id: int, purchase_id: int, purchased_at: date, batch_purchase_value: int, created_at: date):
            process.load_purchase_data.new_purchase(partner_id=partner_id, purchase_id=purchase_id, purchased_at=datetime.strptime(purchased_at, "%Y-%m-%d").date(), batch_purchase_value=batch_purchase_value, created_at=datetime.fromisoformat(created_at).date())
            ui.notify('Az uj rekordok be lettek töltve.')
            return select_rows()


        #button functions
        def add_data():
            toggle_add_button()
            data_table.update_from_pandas(insert_row(new_purchase_batch_number.value, new_purchase_partner_id.value, new_purchase_date.value, new_purchase_batch_purchase_value.value))
            clear_new_values()

        def delete_data():
            toggle_delete_button()
            for row_data in data_table.selected:
                delete_row(row_data["purchase_id"])
            data_table.update_from_pandas(select_rows())

        def update_data():
            toggle_update_button()
            for row_data in data_table.selected:
                data_table.update_from_pandas(update_row(row_data["purchase_id"], updated_purchase_batch_number.value, updated_purchase_partner_id.value, updated_purchase_date.value, updated_purchase_batch_purchase_value.value))
            clear_updated_values()

        def load_data():
            toggle_load_button()
            for row_data in data_table.selected:
                generate(partner_id=row_data["partner_id"], purchase_id=row_data["purchase_id"], purchased_at=row_data["purchased_at"], batch_purchase_value=row_data["batch_purchase_value"], created_at=row_data["created_at"])
            data_table.selected = []

        #button toggles
        def toggle_add_button():
            new_purchase_batch_purchase_value.sanitize()
            if new_purchase_batch_number.value and validate_batch_number(new_purchase_batch_number.value) is None and \
                new_purchase_partner_id.value and new_purchase_partner_id.value in partner_list.keys() and \
                new_purchase_batch_purchase_value.value > 0 and validate_batch_purchase_value(new_purchase_batch_purchase_value.value) is None and \
                new_purchase_date.value:
                add_button.enable()
            else:
                add_button.disable()


        def toggle_delete_button():
            if data_table.selected:
                delete_button.enable()
            else:
                delete_button.disable()


        def toggle_update_button():
            updated_purchase_batch_purchase_value.sanitize()
            if updated_purchase_batch_number.value and validate_batch_number(updated_purchase_batch_number.value) is None and \
                updated_purchase_partner_id.value and updated_purchase_partner_id.value in partner_list.keys() and \
                updated_purchase_batch_purchase_value.value > 0 and validate_batch_purchase_value(updated_purchase_batch_purchase_value.value) is None and \
                updated_purchase_date.value and \
                data_table.selected:
                update_button.enable()
            else:
                update_button.disable()

        def toggle_load_button():
            if data_table.selected:
                load_button.enable()
            else:
                load_button.disable()

        #validation functions
        def validate_batch_number(value):
            if value and len(value) < 3:
                return 'A batch szamanak legalább 3 karakter hosszúnak kell lennie!'
            if value and len(value) > 100:
                return 'A batch szama maximum 100 karakter hosszú lehet!'
            return None

        def validate_batch_purchase_value(value):
            if value and value < 1:
                return 'A batch erteke nem lehet 0 Ft vagy negativ!'
            if value and value > 100_0000_000:
                return 'A batch erteke nem lehet 1000000000 Ft-nal nagyobb!'
            return None


        #visibility toggles
        def toggle_new_card_visibility():
            data_table.selected = []
            delete_card.set_visibility(False)
            update_card.set_visibility(False)
            load_card.set_visibility(False)
            new_card.set_visibility(not(new_card.visible))
            data_table.set_selection('none')
            clear_updated_values()
            clear_new_values()
            toggle_add_button()


        def toggle_delete_card_visibility():
            data_table.selected = []
            new_card.set_visibility(False)
            update_card.set_visibility(False)
            load_card.set_visibility(False)
            delete_card.set_visibility(not(delete_card.visible))
            if delete_card.visible:
                data_table.set_selection('multiple')
            else:
                data_table.set_selection('none')
            clear_updated_values()
            clear_new_values()
            toggle_delete_button()


        def toggle_update_card_visibility():
            data_table.selected = []
            delete_card.set_visibility(False)
            new_card.set_visibility(False)
            load_card.set_visibility(False)
            update_card.set_visibility(not(update_card.visible))
            if update_card.visible:
                data_table.set_selection('single')
            else:
                data_table.set_selection('none')
            clear_updated_values()
            clear_new_values()
            toggle_update_button()

        def toggle_load_card_visibility():
            data_table.selected = []
            delete_card.set_visibility(False)
            new_card.set_visibility(False)
            update_card.set_visibility(False)
            load_card.set_visibility(not(load_card.visible))
            if load_card.visible:
                data_table.set_selection('single')
            else:
                load_card.set_selection('none')
            clear_updated_values()
            clear_new_values()
            toggle_load_button()


        #record selection handling
        def handle_selection():
            toggle_delete_button()
            toggle_update_button()
            toggle_load_button()
            if data_table.selected:
                updated_purchase_batch_number.set_value(data_table.selected[0]['batch_number'])
                updated_purchase_batch_purchase_value.set_value(data_table.selected[0]['batch_purchase_value'])
                updated_purchase_date.set_value(data_table.selected[0]['purchased_at'])
                updated_purchase_partner_id.set_value(data_table.selected[0]['partner_id'])
            else:
                clear_updated_values()
                clear_new_values()

        def clear_updated_values():
            updated_purchase_batch_number.set_value(None)
            updated_purchase_batch_purchase_value.set_value(None)
            updated_purchase_date.set_value(None)
            updated_purchase_partner_id.set_value(None)

        def clear_new_values():
            new_purchase_batch_number.set_value(None)
            new_purchase_partner_id.set_value(None)
            new_purchase_batch_purchase_value.set_value(None)
            new_purchase_date.set_value(None)


        #table column definitions
        #p.purchase_id, p.partner_id, s.name as partner_name, p.batch_number, p.purchased_at, p.batch_purchase_value, p.created_at, p.updated_at, p.deleted_at
        columns=[
                {'name': 'purchase_id', 'label': 'Vasarlas ID', 'field': 'purchase_id', 'sortable': True},
                {'name': 'partner_id', 'label': 'Partner ID', 'field': 'partner_id', 'sortable': True, 'classes': 'hidden', 'headerClasses': 'hidden'},
                {'name': 'partner_name', 'label': 'Partner', 'field': 'partner_name', 'sortable': True},
                {'name': 'batch_number', 'label': 'Batch szama', 'field': 'batch_number', 'sortable': True},
                {'name': 'purchased_at', 'label': 'Vasarlas datuma', 'field': 'purchased_at', 'sortable': True},
                {'name': 'batch_purchase_value', 'label': 'Vasarlas erteke', 'field': 'batch_purchase_value', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]

        partner_list = get_partners()


        #UI element definitions
        ui.label('Vasarlasok karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            new_card_button = ui.button('+', on_click=toggle_new_card_visibility).props('color=blue')
            delete_card_button = ui.button('-', on_click=toggle_delete_card_visibility).props('color=red')
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')
            load_card_button = ui.button('#', on_click=toggle_load_card_visibility).props('color=purple')

        new_card = ui.card()
        with new_card:
            new_purchase_batch_number = ui.input(label= 'Uj batch szama', placeholder='írja be az új batch szamat', on_change=toggle_add_button, validation=validate_batch_number).props('clearable').props('size=100')
            new_purchase_partner_id = ui.select(label= 'Partner választása', options=partner_list, with_input=True, on_change=toggle_add_button).props('size=100')
            new_purchase_batch_purchase_value = ui.number(label= 'Uj batch erteke', placeholder='írja be az új batch erteket', suffix='Ft', format="%.0f", min=1, max=100_0000_000, on_change=toggle_add_button, validation=validate_batch_purchase_value, precision=0).props('clearable').props('size=100')
            with ui.input('Date', on_change=toggle_add_button) as new_purchase_date:
                with ui.menu().props('no-parent-event') as menu:
                    with ui.date().bind_value(new_purchase_date):
                        with ui.row().classes('justify-end'):
                            ui.button('Close', on_click=menu.close).props('flat')
                with new_purchase_date.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            add_button = ui.button('Új vasarlas hozzáadása', on_click=add_data).props('color=blue')

        delete_card = ui.card()
        with delete_card:
            delete_button = ui.button('A kijelölt vasarlas(ok) törlése', on_click=delete_data).props('color=red')

        update_card = ui.card()
        with update_card:
            updated_purchase_batch_number = ui.input(label= 'Uj batch szama', on_change=toggle_update_button, validation=validate_batch_number).props('clearable').props('size=100')
            updated_purchase_partner_id = ui.select(label= 'Partner választása', options=partner_list, with_input=True, on_change=toggle_update_button).props('size=100')
            updated_purchase_batch_purchase_value = ui.number(label= 'Uj batch erteke', suffix='Ft', format="%.0f", min=1, max=100_0000_000, on_change=toggle_update_button, validation=validate_batch_purchase_value, precision=0).props('clearable').props('size=100')
            with ui.input('Date', on_change=toggle_update_button) as updated_purchase_date:
                with ui.menu().props('no-parent-event') as menu:
                    with ui.date().bind_value(updated_purchase_date):
                        with ui.row().classes('justify-end'):
                            ui.button('Close', on_click=menu.close).props('flat')
                with updated_purchase_date.add_slot('append'):
                    ui.icon('edit_calendar').on('click', menu.open).classes('cursor-pointer')
            update_button = ui.button('Vasarlas modositasa', on_click=update_data).props('color=green')

        load_card = ui.card()
        with load_card:
            load_button = ui.button('Adatok betoltese a kijelolt vasarlashoz', on_click=load_data).props('color=purple')

        search_field = ui.input('Keresés', placeholder='írja be a keresendő vasarlas valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='purchase_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full')
        search_field.bind_value(data_table, 'filter')

        #initial visibility settings
        toggle_add_button()
        toggle_delete_button()
        toggle_update_button()
        toggle_load_button()
        new_card.set_visibility(False)
        delete_card.set_visibility(False)
        update_card.set_visibility(False)
        load_card.set_visibility(False)

    #connection.close()
