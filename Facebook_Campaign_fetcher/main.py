import flet as ft
from UI_Layout import AppView
from EventController import AppController
import Facebook_Campaign_fetcher
import Table_Print
import ExcelMaker
import ConfigReader
import flet


async def main(page: ft.Page):

    view = AppView(page)

    controller = AppController(view)

    page.add(view.build(controller))


if __name__ == "__main__":
    ft.run(main)
