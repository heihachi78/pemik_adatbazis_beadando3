from nicegui import ui, app

def clear_storage():
    app.storage.user['saved_data']["person_id"] = ''
    app.storage.user['saved_data']["case_id"] = ''
    app.storage.user['saved_data']["sector_name"] = ''
    app.storage.user['saved_data']["partner_name"] = ''
    app.storage.user['saved_data']["person_name"] = ''
    app.storage.user['saved_data']["account"] = ''
    app.storage.user['saved_data']["bank_account"] = ''


def menu() -> None:
    ui.link('Home', '/').classes(replace='text-black')
    ui.link('Szektorok', '/sectors/').classes(replace='text-black')
    ui.link('Partnerek', '/partners/').classes(replace='text-black').on('click', clear_storage)
    ui.link('Vásárlások', '/purchases/').classes(replace='text-black').on('click', clear_storage)
    ui.link('Nyitott ügyek', '/opencases/').classes(replace='text-black')
    ui.link('Zárt ügyek', '/closedcases/').classes(replace='text-black')
    ui.link('Adósok', '/debtors/').classes(replace='text-black').on('click', clear_storage)
    ui.link('Személyek', '/persons/').classes(replace='text-black').on('click', clear_storage)
    ui.link('Számlatulajok', '/bank_accounts/').classes(replace='text-black').on('click', clear_storage)
    ui.link('Bankszámlák', '/accounts/').classes(replace='text-black').on('click', clear_storage)
    ui.link('Riport', '/report/').classes(replace='text-black')
    ui.link('Info', '/info/').classes(replace='text-black')