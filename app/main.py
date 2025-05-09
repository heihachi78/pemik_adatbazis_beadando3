import all_pages
import home_page
import theme
from nicegui import app, ui


@ui.page('/')
def index_page() -> None:
    app.storage.user['saved_data'] = {"case_id": -1, "open": False, "person_id": -1}
    with theme.frame('Home'):
        home_page.content()

all_pages.create()

ui.run(reload=True, title='PEMIK - haladó adatbázis technológiak beadandó - J0P7MF', port=8081, storage_secret='J0P7MF')
