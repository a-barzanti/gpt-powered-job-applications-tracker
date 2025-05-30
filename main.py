from datetime import datetime

import flet as ft
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_sheet():
    creds = Credentials.from_service_account_file("creds.json", scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open("Job Applications Tracker").sheet1


def get_sheet_data_reversed(sheet):
    data = sheet.get_all_values()
    if not data or len(data) < 2:
        return data
    header = data[0]
    rows = data[1:]
    rows.reverse()
    return [header] + rows


def main(page: ft.Page):
    page.title = "Simple Job Applications Tracker"
    page.window_min_height = 600
    page.window_min_width = 800

    sheet = get_sheet()

    company_input = ft.TextField(label="Company", width=250)
    url_input = ft.TextField(label="Job URL", width=350)
    status_display = ft.Text()
    loader = ft.ProgressRing(visible=False)

    def create_table():
        loader.visible = True
        page.update()

        data = get_sheet_data_reversed(sheet)
        loader.visible = False

        if not data:
            return ft.Text("No data found.")

        headers = [
            ft.DataColumn(ft.Text(col, size=12, weight="bold")) for col in data[0]
        ]
        rows = []

        try:
            url_index = data[0].index("URL")
        except ValueError:
            url_index = -1

        for row in data[1:]:
            cells = []
            for col_idx, cell in enumerate(row):
                if col_idx == url_index:
                    cell_widget = ft.Container(
                        content=ft.Text(
                            spans=[
                                ft.TextSpan(
                                    text=cell,
                                    style=ft.TextStyle(
                                        color=ft.Colors.BLUE,
                                        decoration=ft.TextDecoration.UNDERLINE,
                                    ),
                                    url=cell,
                                )
                            ],
                            size=11,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        width=100,
                    )
                else:
                    cell_widget = ft.Text(cell, size=11)
                cells.append(ft.DataCell(cell_widget))
            rows.append(ft.DataRow(cells=cells))

        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.DataTable(
                        columns=headers,
                        rows=rows,
                        heading_row_color=ft.Colors.GREY_200,
                        show_checkbox_column=False,
                        data_row_color={
                            "even": ft.Colors.WHITE,
                            "odd": ft.Colors.GREY_100,
                        },
                        vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
                        horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
                        column_spacing=10,
                        divider_thickness=1,
                        heading_row_height=40,
                        heading_text_style=ft.TextStyle(weight="bold"),
                    ),
                    expand=True,
                    width=float("inf"),
                    border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300)),
                )
            ],
            expand=True,
        )

    def on_submit(e):
        company = company_input.value.strip()
        url = url_input.value.strip()
        if not company or not url:
            status_display.value = "Please fill in both fields."
            page.update()
            return

        date_applied = datetime.now().strftime("%d/%m/%Y")
        sheet.append_row([company, "Unknown Role", "Applied", date_applied, url])

        company_input.value = ""
        url_input.value = ""
        status_display.value = f"Added {company}"

        loader.visible = True
        page.update()

        table_wrapper.controls[0] = create_table()
        loader.visible = False
        page.update()

    table_wrapper = ft.Column(
        controls=[create_table()], expand=True, scroll=ft.ScrollMode.AUTO
    )

    table_box = ft.Container(
        content=table_wrapper,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=10,
        expand=True,
    )

    page.add(
        ft.Column(
            [
                ft.Text("Add a new job application", size=20, weight="bold"),
                ft.Row(
                    [
                        company_input,
                        url_input,
                        ft.ElevatedButton("Add", on_click=on_submit),
                    ]
                ),
                status_display,
                ft.Divider(),
                ft.Text("Your applications", size=18, weight="bold"),
                loader,
                table_box,
            ],
            expand=True,
        )
    )


ft.app(target=main)
