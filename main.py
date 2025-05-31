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
    page.title = "GPT-Powered Job Tracker"
    page.window_min_height = 600
    page.window_min_width = 800

    sheet = await get_sheet()

    url_input = ft.TextField(label="Job URL", width=500)
    status_display = ft.Text()
    loader = ft.ProgressRing(visible=False)

    gpt_output_text = ft.Text(value="", size=12, selectable=True)
    gpt_response_container = ft.Container(
        content=ft.Column(
            controls=[gpt_output_text],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        ),
        height=150,
        border=ft.border.all(1, ft.Colors.GREY_300),
        border_radius=8,
        padding=10,
    )

    async def create_table():
        loader.visible = True
        page.update()
        data = await get_sheet_data_reversed(sheet)
        loader.visible = False

        if not data:
            return ft.Text("No data found.")

        headers = [ft.DataColumn(ft.Text(col, size=12, weight="bold")) for col in data[0]]
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

    async def on_submit(e):
        url = url_input.value.strip()
        if not is_valid_url(url):
            status_display.value = "Invalid URL. Try something real."
            page.update()
            return

        loader.visible = True
        gpt_output_text.value = "Launching browser, scraping site, bribing GPT..."
        status_display.value = ""
        page.update()

        raw_text = await fetch_rendered_text(url)
        gpt_result = await extract_job_info(raw_text)

        gpt_output_text.value = gpt_result
        page.update()

        company, title = "Not found", "Not found"
        for line in gpt_result.splitlines():
            if "Company Name" in line:
                company = line.split(":", 1)[-1].strip()
            if "Job Title" in line:
                title = line.split(":", 1)[-1].strip()

        date_applied = datetime.now().strftime("%d/%m/%Y")
        await asyncio.to_thread(sheet.append_row, [company, title, "Applied", date_applied, url])

        url_input.value = ""
        status_display.value = f"Added {company} - {title}"
        table_wrapper.controls[0] = await create_table()
        loader.visible = False
        page.update()

    table_wrapper = ft.Column(
        controls=[await create_table()],
        expand=True,
        scroll=ft.ScrollMode.AUTO
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
                ft.Text("Auto-Fill Job Application from URL", size=20, weight="bold"),
                ft.Row([url_input, ft.ElevatedButton("Parse & Add", on_click=on_submit)]),
                status_display,
                loader,
                ft.Text("GPT Output", weight="bold", size=14),
                gpt_response_container,
                ft.Divider(),
                ft.Text("Your Applications", size=18, weight="bold"),
                table_box,
            ],
            expand=True,
        )
    )

ft.app(target=main)