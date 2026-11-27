"""첫 화면(src/index.html)의 목록으로 docs/QR활동목록.xlsx 를 만든다: 과정별 시트에 차시·게임 이름·URL·QR 이미지.
사용: python tools/build_qr_excel.py   (playwright + Edge, openpyxl 필요)
QR은 첫 화면의 「QR 저장」 그림과 같다(내용은 index.html의 PROD 주소).
"""
import functools
import http.server
import io
import sys
import tempfile
import threading
from pathlib import Path
from openpyxl import Workbook
from openpyxl.drawing.image import Image as XImage
from openpyxl.drawing.spreadsheet_drawing import AnchorMarker, OneCellAnchor
from openpyxl.drawing.xdr import XDRPositiveSize2D
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils.units import pixels_to_EMU as EMU
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'docs' / 'QR활동목록.xlsx'
COLOR = {'성인 전기': 'F07C54', '성인 중기': '3DA27C', '성인 후기': '8E5AA8'}
W = 170   # 엑셀에 보이는 QR 폭(px). 그림 자체는 640px 그대로 들어간다


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def collect():
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT / 'src')))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel='msedge')
        g = b.new_page(viewport={'width': 1200, 'height': 900}, accept_downloads=True)
        g.goto(f'http://127.0.0.1:{srv.server_port}/index.html')
        g.wait_for_timeout(1500)
        data = g.evaluate('SECTIONS.map(([t,,l])=>[t,l.map(x=>({code:x.code,name:x.name,url:x.href?gameUrl(x.href):""}))])')
        i = 0
        for title, games in data:
            for x in games:
                x['png'] = None
                if x['url']:
                    with g.expect_download() as d:
                        g.locator('button.qr').nth(i).dispatch_event('click')
                    t = Path(tempfile.mkdtemp()) / 'q.png'
                    d.value.save_as(t)
                    x['png'] = t.read_bytes()
                    i += 1
            rows.append((title, games))
        b.close()
    srv.shutdown()
    return rows


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    wb = Workbook()
    wb.remove(wb.active)
    thin = Side(style='thin', color='D8C9B3')
    box = Border(thin, thin, thin, thin)
    F = '맑은 고딕'
    for title, games in collect():
        ws = wb.create_sheet(title)
        for c, w in zip('ABCD', (11, 38, 54, 28)):
            ws.column_dimensions[c].width = w
        ws['A1'] = f'QR활동 목록 · {title}'
        ws['A1'].font = Font(name=F, size=16, bold=True, color=COLOR[title])
        ws.row_dimensions[1].height = 34
        ws['A1'].alignment = Alignment(vertical='center')
        for c, t in enumerate(('차시', '게임 이름', 'URL', 'QR코드'), 1):
            h = ws.cell(2, c, t)
            h.font = Font(name=F, size=11, bold=True, color='FFFFFF')
            h.fill = PatternFill('solid', fgColor=COLOR[title])
            h.alignment = Alignment(horizontal='center', vertical='center')
            h.border = box
        ws.row_dimensions[2].height = 24
        for r, x in enumerate(games, 3):
            vals = (x['code'], x['name'], x['url'] or '개발 전', None if x['png'] else '개발 전')
            for c, v in enumerate(vals, 1):
                k = ws.cell(r, c, v)
                k.font = Font(name=F, size=11, bold=c == 1)
                k.alignment = Alignment(horizontal='left' if c in (2, 3) and x['url'] or c == 2 else 'center', vertical='center', wrap_text=True)
                k.border = box
            if x['url']:
                ws.cell(r, 3).hyperlink = x['url']
                ws.cell(r, 3).font = Font(name=F, size=10, color='0563C1', underline='single')
            ws.row_dimensions[r].height = 40
            if x['png']:
                w0, h0 = Image.open(io.BytesIO(x['png'])).size
                H = round(W * h0 / w0)
                ws.row_dimensions[r].height = (H + 16) * .75
                im = XImage(io.BytesIO(x['png']))
                im.anchor = OneCellAnchor(AnchorMarker(3, EMU(15), r - 1, EMU(8)), XDRPositiveSize2D(EMU(W), EMU(H)))
                ws.add_image(im)
        ws.freeze_panes = 'A3'
        ws.sheet_view.showGridLines = False
        ws.page_setup.paperSize = 9
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.print_title_rows = '1:2'
        ws.sheet_properties.tabColor = COLOR[title]
        print(title, len(games), sum(1 for x in games if x['png']))
    wb.save(OUT)
    print(OUT.name, OUT.stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
