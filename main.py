import asyncio
from datetime import datetime
from urllib.parse import urlparse
from pathlib import Path

import flet as ft
import gspread
from bs4 import BeautifulSoup
from google.oauth2.service_account import Credentials
from openai import OpenAI
from playwright.async_api import async_playwright

# === OPENAI KEY MANAGEMENT ===
key_file = Path("openai_key.txt")
if not key_file.exists():
    raise FileNotFoundError("Missing 'openai_key.txt'. Please create it and paste your OpenAI API key inside.")
with key_file.open("r") as f:
    openai_api_key = f.read().strip()
if not openai_api_key.startswith("sk-"):
    raise ValueError("The OpenAI API key in 'openai_key.txt' is invalid or missing.")

client = OpenAI(api_key=openai_api_key)

# === CONFIG ===
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

# === HELPERS ===

def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return all([parsed.scheme, parsed.netloc])
    except Exception:
        return False

async def fetch_rendered_text(url):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_load_state("networkidle")
            content = await page.content()
            await browser.close()
            soup = BeautifulSoup(content, "html.parser")
            return soup.get_text(separator="\n", strip=True)
    except Exception as e:
        return f"Headless browser error: {e}"

async def extract_job_info(text):
    prompt = f"""
Given the raw text from a job listing page, extract the following:
- Company Name
- Job Title

Be concise. If not found, return "Not found".

Text:
{text[:4000]}
"""
    try:
        response = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error contacting GPT: {e}"

async def get_sheet():
    def connect():
        creds = Credentials.from_service_account_file("creds.json", scopes=SCOPES)
        client = gspread.authorize(creds)
        return client.open("Job Applications Tracker").sheet1
    return await asyncio.to_thread(connect)

async def get_sheet_data_reversed(sheet):
    def get_data():
        data = sheet.get_all_values()
        if not data or len(data) < 2:
            return data
        header, rows = data[0], data[1:]
        rows.reverse()
        return [header] + rows
    return await asyncio.to_thread(get_data)

# === MAIN APP ===

async def main(page: ft.Page):
    page.title = "GPT-Powered Job Application Tracker"
    page.window.min_height = 600
    page.window.min_width = 800
    page.padding = 0

    sheet = None

    url_input = ft.TextField(label="Job URL", width=500)
    status_display = ft.Text(size=12, color=ft.Colors.GREEN)
    loader = ft.ProgressRing(visible=False)

    gpt_output_text = ft.Text(value="", size=12, selectable=True)
    gpt_response_container = ft.Container(
        content=ft.Column(
            controls=[gpt_output_text],
            expand=True,
        ),
        expand=True,
        padding=10
    )

    async def on_refresh(e):
        nonlocal sheet

        loader.visible = True
        status_display.value = "Refreshing table…"
        page.update()
        if sheet is None:
            sheet = await get_sheet()
        table_wrapper.controls[0] = await create_table()
        status_display.value = "✅ Table refreshed"
        loader.visible = False
        page.update()

    async def create_table():
        nonlocal sheet

        loader.visible = True
        page.update()
        if sheet is None:
            sheet = await get_sheet()
        data = await get_sheet_data_reversed(sheet)
        loader.visible = False

        if not data:
            return ft.Text("No data found.")

        headers = [ft.DataColumn(ft.Text(col, size=12, weight=ft.FontWeight.BOLD)) for col in data[0]]
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

        return ft.Container(
            content=ft.DataTable(
                columns=headers,
                rows=rows,
                heading_row_color=ft.Colors.GREY_200,
                show_checkbox_column=False,
                vertical_lines=ft.BorderSide(1, ft.Colors.GREY_300),
                horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_300),
                column_spacing=10,
                divider_thickness=1,
                heading_row_height=40,
                heading_text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
            ),
            expand=True,
            width=float("inf"),
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_300)),
        )

    table_wrapper = ft.Column(
        controls=[ft.Text("")],
        expand=True,
        scroll=ft.ScrollMode.AUTO
    )


    async def on_submit(e):
        nonlocal sheet
        
        url = (url_input.value or "").strip()
        if not is_valid_url(url):
            status_display.value = "Invalid URL. Try something real."
            page.update()
            return

        loader.visible = True
        status_display.value = "Launching browser, scraping site, bribing GPT..."
        page.update()

        raw_text = await fetch_rendered_text(url)
        gpt_result = await extract_job_info(raw_text)

        gpt_output_text.value = gpt_result
        page.update()

        company, title = "Not found", "Not found"
        for line in (gpt_result or "").splitlines():
            if "Company Name" in line:
                company = line.split(":", 1)[-1].strip()
            if "Job Title" in line:
                title = line.split(":", 1)[-1].strip()

        date_applied = datetime.now().strftime("%d/%m/%Y")
        if sheet is not None:
            await asyncio.to_thread(sheet.append_row, [company, title, "Applied", date_applied, url])

        url_input.value = ""
        status_display.value = f"✅ Added {company} – {title}"
        table_wrapper.controls[0] = await create_table()
        loader.visible = False
        page.update()

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Applications",
                content=table_wrapper,
            ),
            ft.Tab(
                text="GPT Output",
                content=gpt_response_container
            ),
        ],
        expand=True,
        visible=False,  # Initially hidden, will be shown after first load
    )

    async def lazy_load_table():
        table = await create_table()
        table_wrapper.controls[0] = table
        tabs.visible = True
        page.update()  # Sync, not async

    asyncio.create_task(lazy_load_table())

    page.add(
        ft.Column(
            [
                ft.Container(
                    content= ft.Column(
                        [
                            ft.Text("Auto-Fill Job Application from URL", size=20, weight=ft.FontWeight.BOLD),
                            ft.Row([
                                url_input,
                                ft.ElevatedButton("Parse & Add", on_click=on_submit),
                                ft.IconButton(icon=ft.Icons.REFRESH, tooltip="Refresh Table", on_click=on_refresh)
                            ]),
                            status_display,
                            loader,
                        ],
                        expand=True,
                    ), 
                    padding=10,
                ),
 
                tabs,
            ],
            expand=True,
        )
    )

ft.app(target=main)