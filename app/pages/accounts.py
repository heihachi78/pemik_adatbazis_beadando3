from sqlalchemy import create_engine, text
from nicegui import ui, app
import pandas as pd
import theme
import config.database


def show_accounts():
    with theme.frame('Bankszámlák karbantartása'):
        ui.page_title('Bankszámlák karbantartása')

        engine = create_engine(config.database.POOL_CONN_INFO)
        connection = engine.connect()

        #database functions
        def select_rows():
            return pd.read_sql_query('select a.bank_account_id, a.account_number, a.created_at::date from bank_accounts a where a.deleted_at is null ORDER BY a.bank_account_id desc', con=connection)


        def insert_row(account_number: str):
            connection.execute(text("insert into bank_accounts (account_number) values (:account_number)"), {"account_number": account_number})
            connection.commit()
            ui.notify('Az új rekord felvétele sikeres volt.')
            return select_rows()


        def delete_row(bank_account_id: int):
            connection.execute(text("update bank_accounts set deleted_at = now() where bank_account_id = :bank_account_id"), {"bank_account_id": bank_account_id})
            connection.commit()
            ui.notify('A rekord törölve lett.')
            return select_rows()


        def update_row(bank_account_id: int, account_number: str):
            connection.execute(text("update bank_accounts set account_number = :account_number, updated_at = now() where bank_account_id = :bank_account_id"), {"bank_account_id": bank_account_id, "account_number": account_number})
            connection.commit()
            ui.notify('A rekord módosítva lett.')
            return select_rows()

        def has_payment(bank_account_id: int):
            return connection.execute(text("select count(*) from payments where bank_account_id = :bank_account_id and deleted_at is null"),  {"bank_account_id": bank_account_id}).fetchone()[0]


        #button functions
        def add_data():
            if new_account_number.value:
                data_table.update_from_pandas(insert_row(new_account_number.value))
                new_account_number.set_value(None)
                toggle_add_button()


        def delete_data():
            for row_data in data_table.selected:
                delete_row(row_data["bank_account_id"])
            data_table.update_from_pandas(select_rows())
            toggle_delete_button()


        def update_data():
            if update_account_number.value and len(data_table.selected) == 1:
                for row_data in data_table.selected:
                    data_table.update_from_pandas(update_row(row_data["bank_account_id"], update_account_number.value))
                update_account_number.set_value(None)
                toggle_update_button()


        #button toggles
        def toggle_add_button():
            if new_account_number.value and validate_an(new_account_number.value) is None:
                add_button.enable()
            else:
                add_button.disable()


        def toggle_delete_button():
            if data_table.selected:
                delete_button.enable()
            else:
                delete_button.disable()


        def toggle_update_button():
            if update_account_number.value and validate_an(update_account_number.value) is None and data_table.selected:
                update_button.enable()
            else:
                update_button.disable()


        #validation functions
        def validate_an(value):
            if value and (len(value) not in (17, 26) or '-' not in value):
                return 'A számlaszám 12345678-12345678 vagy 12345678-12345678-12345678 formátumban kell legyen!'
            return None


        #visibility toggles
        def toggle_new_card_visibility():
            delete_card.set_visibility(False)
            update_card.set_visibility(False)
            new_card.set_visibility(not(new_card.visible))
            data_table.set_selection('none')
            data_table.selected = []
            update_account_number.set_value(None)
            new_account_number.set_value(None)
            toggle_add_button()


        def toggle_delete_card_visibility():
            new_card.set_visibility(False)
            update_card.set_visibility(False)
            delete_card.set_visibility(not(delete_card.visible))
            if delete_card.visible:
                data_table.set_selection('multiple')
            else:
                data_table.set_selection('none')
            data_table.selected = []
            update_account_number.set_value(None)
            new_account_number.set_value(None)
            toggle_delete_button()


        def toggle_update_card_visibility():
            delete_card.set_visibility(False)
            new_card.set_visibility(False)
            update_card.set_visibility(not(update_card.visible))
            if update_card.visible:
                data_table.set_selection('single')
            else:
                data_table.set_selection('none')
            data_table.selected = []
            update_account_number.set_value(None)
            new_account_number.set_value(None)
            toggle_update_button()


        #record selection handling
        def handle_selection():
            if delete_card.visible and data_table.selected:
                s = []
                for sl in data_table.selected:
                    if has_payment(sl['bank_account_id']) > 0:
                        s.append(sl)
                for ss in s:
                    data_table.selected.remove(ss)
                data_table.update()
            if data_table.selected:
                update_account_number.set_value(data_table.selected[0]['account_number'])
            else:
                update_account_number.set_value(None)
            toggle_delete_button()
            toggle_update_button()

        def on_row_dblclick(e):
            app.storage.user['saved_data']["bank_account"] = e.args[1]["account_number"]
            ui.navigate.to('/bank_accounts/', new_tab=False)


        #table column definitions
        columns=[
                {'name': 'bank_account_id', 'label': 'Bankszámla ID', 'field': 'bank_account_id', 'sortable': True},
                {'name': 'account_number', 'label': 'Számlaszám', 'field': 'account_number', 'sortable': True},
                {'name': 'created_at', 'label': 'Létrehozás időpontja', 'field': 'created_at', 'sortable': True}
            ]


        #UI element definitions
        ui.label('Bankszámlák karbantartása').style('color: #6E93D6; font-size: 300%; font-weight: 300')

        with ui.row():
            new_card_button = ui.button('+', on_click=toggle_new_card_visibility).props('color=blue')
            delete_card_button = ui.button('-', on_click=toggle_delete_card_visibility).props('color=red')
            update_card_button = ui.button('!', on_click=toggle_update_card_visibility).props('color=green')

        new_card = ui.card()
        with new_card:
            new_account_number = ui.input(label= 'Számlaszám', placeholder='írja be az új számlaszámot', on_change=toggle_add_button, validation=validate_an).props('clearable').props('size=100')
            add_button = ui.button('Új számla hozzáadása', on_click=add_data).props('color=blue')

        delete_card = ui.card()
        with delete_card:
            delete_button = ui.button('A kijelölt számla(számlák) törlése', on_click=delete_data).props('color=red')

        update_card = ui.card()
        with update_card:
            update_account_number = ui.input(label= 'Számlaszám', on_change=toggle_update_button, validation=validate_an).props('clearable').props('size=100')
            update_button = ui.button('A kijelölt számla módosítása', on_click=update_data).props('color=green')

        search_field = ui.input('Keresés', placeholder='írja be a keresendő bankszámla valamely adatát').props('clearable').props('size=100')
        data_table = ui.table.from_pandas(select_rows(), row_key='bank_account_id', on_select=handle_selection, pagination=5, columns=columns).classes('w-full').on('rowDblclick', on_row_dblclick)
        data_table.set_filter(str(app.storage.user['saved_data']["account"]))
        search_field.bind_value(data_table, 'filter')


        #initial visibility settings
        toggle_add_button()
        toggle_delete_button()
        toggle_update_button()
        new_card.set_visibility(False)
        delete_card.set_visibility(False)
        update_card.set_visibility(False)

    #connection.close()
