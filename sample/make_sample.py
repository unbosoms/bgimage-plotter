#!/usr/bin/env python3
"""サンプル画像（架空のシェアオフィスの座席図）と、座席の座標・利用状況の CSV を作る。

- 座席図：floor-plan.png（1600×1000 px）。会社名・地名などは架空。
- 座席の座標：seats.csv（ツールの出力と同じ形。X・Y は Tableau 用に Y を上向きにした値）
- 利用状況：seat-status.csv（座席ID・エリア・状況。状況は「空席」「使用中」の架空のデータ）
- 完成イメージ：preview.png（座席図を薄くして、状況の色の丸を重ねたもの。Tableau の見た目の例）

必要なもの：Pillow、日本語フォント（既定は Noto Sans JP。FONT で変える）
使い方：python3 make_sample.py
"""
import csv
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
FONT = os.environ.get('FONT', str(Path.home() / 'Library/Fonts/NotoSansJP-VariableFont_wght.ttf'))
W, H = 1600, 1000
WALL, INK, MUTED, DESK, CHAIR = '#3c4047', '#3c4047', '#8a9099', '#e9e4da', '#c9ced6'


def font(size, weight=500):
    f = ImageFont.truetype(FONT, size)
    try:
        f.set_variation_by_axes([weight])      # 可変フォントの太さ（Noto Sans JP は既定が最も細いため）
    except OSError:
        pass                                   # 可変でないフォントはそのまま
    return f


def chair(d, cx, cy, seats, sid, area):
    d.rounded_rectangle((cx - 17, cy - 14, cx + 17, cy + 14), radius=7, fill=CHAIR, outline='#a7adb6', width=2)
    seats.append((sid, area, cx, cy))


def label(d, xy, text, size=13, fill='#6b717a', anchor='mm'):
    d.text(xy, text, font=font(size), fill=fill, anchor=anchor)


def draw_plan():
    im = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(im)
    seats = []

    # 外壁と窓（上の辺）
    d.rectangle((40, 40, W - 40, H - 40), outline=WALL, width=8)
    for x in range(120, W - 120, 160):
        d.line((x, 40, x + 110, 40), fill='#9cc3e0', width=8)

    # 間仕切り
    d.line((440, 40, 440, 560), fill=WALL, width=5)          # 受付・ラウンジ｜オープン席
    d.line((40, 560, 300, 560), fill=WALL, width=5)          # 受付｜ラウンジ（340〜440 は通路）
    d.line((1120, 40, 1120, 380), fill=WALL, width=5)        # オープン席｜集中ブース
    d.line((1120, 470, 1120, H - 40), fill=WALL, width=5)    # オープン席｜会議室（380〜470 は通路）
    d.line((1120, 380, 1180, 380), fill=WALL, width=5)
    d.line((1260, 380, W - 40, 380), fill=WALL, width=5)     # 集中ブース｜会議室（入口 1180〜1260）
    d.line((1120, 680, W - 40, 680), fill=WALL, width=5)     # 会議室A｜会議室B

    # 入口（左下）
    d.line((40, 820, 40, 920), fill='white', width=10)
    label(d, (95, 870), '入口', 15, INK)

    # 受付
    label(d, (240, 90), '受付', 18, INK)
    d.rounded_rectangle((120, 140, 360, 200), radius=8, fill=DESK, outline='#c9bfae', width=2)
    # 待合のソファ（座席ではないので点は置かない）
    for y in (300, 420):
        d.rounded_rectangle((110, y, 370, y + 60), radius=14, fill='#dde3ea', outline='#b8c0ca', width=2)
    label(d, (240, 510), '待合', 14)

    # ラウンジ：カウンター席（L-01〜L-03）。ツールで名前を表示したときに重ならないよう、席の間を 110 px あける
    label(d, (240, 600), 'ラウンジ', 18, INK)
    d.rounded_rectangle((90, 650, 390, 700), radius=8, fill=DESK, outline='#c9bfae', width=2)
    for i, x in enumerate((130, 240, 350)):
        chair(d, x, 725, seats, f'L-{i + 1:02d}', 'ラウンジ')
        label(d, (x, 675), f'L-{i + 1:02d}', 11)

    # オープン席：島3つ × 8席（A-01〜A-24）
    label(d, (780, 80), 'オープン席', 18, INK)
    n = 0
    for iy, top in enumerate((150, 430, 710)):
        d.rounded_rectangle((540, top, 1020, top + 90), radius=6, fill=DESK, outline='#c9bfae', width=2)
        d.line((540, top + 45, 1020, top + 45), fill='#d3cab9', width=1)
        for row, cy in ((0, top - 22), (1, top + 112)):
            for k in range(4):
                cx = 600 + k * 120
                n += 1
                chair(d, cx, cy, seats, f'A-{n:02d}', 'オープン席')
                label(d, (cx, top + 22 if row == 0 else top + 68), f'A-{n:02d}', 11)

    # 集中ブース：2列 × 3（B-01〜B-06）
    label(d, (1340, 75), '集中ブース', 18, INK)
    b = 0
    for r, top in enumerate((110, 245)):
        for c in range(3):
            x0 = 1150 + c * 130
            d.rectangle((x0, top, x0 + 115, top + 115), outline=MUTED, width=3)
            d.rectangle((x0 + 10, top + 10, x0 + 105, top + 42), fill=DESK, outline='#c9bfae', width=2)
            b += 1
            chair(d, x0 + 57, top + 72, seats, f'B-{b:02d}', '集中ブース')
            label(d, (x0 + 57, top + 26), f'B-{b:02d}', 11)

    # 会議室A・B：テーブル1つ＋6席（MA-1〜6、MB-1〜6）
    for name, key, top in (('会議室A', 'MA', 400), ('会議室B', 'MB', 700)):
        label(d, (1340, top + 30), name, 18, INK)
        d.rounded_rectangle((1190, top + 110, 1490, top + 180), radius=10, fill=DESK, outline='#c9bfae', width=2)
        k = 0
        for cy in (top + 86, top + 204):
            for cx in (1220, 1340, 1460):
                k += 1
                chair(d, cx, cy, seats, f'{key}-{k}', name)

    # 図の注記
    label(d, (W - 60, H - 20), '架空のシェアオフィス（サンプル）', 13, MUTED, 'rm')
    return im, seats


def write_csvs(seats):
    # ツールの出力と同じ形（番号・名前・X・Y・画素X・画素Y。Y は上向き）
    with open(HERE / 'seats.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['番号', '名前', 'X', 'Y', '画素X', '画素Y'])
        for i, (sid, _, x, y) in enumerate(seats, 1):
            w.writerow([i, sid, x, H - y, x, y])
    # 利用状況（架空）。乱数の種を固定して、毎回同じ結果にする。集中ブースは全部使用中（満席の例）
    rnd = random.Random(20261104)
    status = {}
    for sid, area, _, _ in seats:
        status[sid] = '使用中' if area == '集中ブース' or rnd.random() < 0.45 else '空席'
    for sid in [s for s, a, _, _ in seats if a == '会議室B']:
        status[sid] = '空席'                  # 会議室Bは空き（全部空席の例）
    with open(HERE / 'seat-status.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['座席ID', 'エリア', '状況'])
        for sid, area, _, _ in seats:
            w.writerow([sid, area, status[sid]])
    return status


def draw_preview(plan, seats, status):
    # Tableau で「ウォッシュアウト」をかけたときに近い見た目：画像を白に寄せ、状況の色の丸を重ねる
    im = Image.blend(plan, Image.new('RGB', plan.size, 'white'), 0.45)
    d = ImageDraw.Draw(im)
    color = {'空席': '#1f77b4', '使用中': '#ff7f0e'}
    for sid, _, x, y in seats:
        d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=color[status[sid]], outline='white', width=2)
    # 凡例
    d.rounded_rectangle((180, 850, 380, 930), radius=6, fill='white', outline='#c9ced6')
    for i, (k, c) in enumerate(color.items()):
        y = 873 + i * 34
        d.ellipse((196, y - 10, 216, y + 10), fill=c)
        n = sum(1 for v in status.values() if v == k)
        d.text((228, y), f'{k}（{n}席）', font=font(16), fill=INK, anchor='lm')
    return im


def main():
    plan, seats = draw_plan()
    plan.save(HERE / 'floor-plan.png', optimize=True)
    status = write_csvs(seats)
    draw_preview(plan, seats, status).save(HERE / 'preview.png', optimize=True)
    print(f'{len(seats)} seats')


if __name__ == '__main__':
    main()
