#https://www.bitdoze.com/nicegui-pages/
#https://www.youtube.com/watch?v=bW3ifL2hdfc

import all_pages
import home_page
import theme
from nicegui import app, ui



@ui.page('/')
def index_page() -> None:
    with theme.frame('Home'):
        home_page.content()

all_pages.create()

ui.run(reload=True, title='PEMIK - haladó adatbázis technológiak beadandó - J0P7MF', port=8081)