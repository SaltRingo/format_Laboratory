from flask import Flask, render_template, request

app = Flask(__name__)

FIELDS = [
    "Abbreviation", "Presentation Date", "Author", "Title", "Conference",
    "Publisher", "Volume", "Number", "Presentation Number", "Page",
    "Organizer", "Begin", "End", "Venue"
]

def fill_fields(raw_cells):
    # 最初の不要な3つをスキップ
    cells = raw_cells[3:]
    # 必要な14列に切り出して、不足している場合は "未入力" で補完
    while len(cells) < 17:
        cells.append("")

    info = {}
    for i, key in enumerate(FIELDS):
        value = cells[i] if cells[i] else "未入力"
        info[key] = value
    return info

def format_text(info):
    import datetime
    import re

    # 日付整形
    try:
        date_obj = datetime.datetime.strptime(info["Presentation Date"], "%Y/%m/%d")
        weekday = "日月火水木金土"[date_obj.weekday()]
        formatted_date = f"{date_obj.month}/{date_obj.day}({weekday})"
    except Exception:
        formatted_date = info["Presentation Date"]

    # 時間・セッション抽出
    session_info = info["Presentation Number"]
    time_match = re.search(r'\d{1,2}[:：]\d{2}〜\d{1,2}[:：]\d{2}', session_info)
    time_str = time_match.group().replace("：", ":").replace("〜", "-") if time_match else "未入力"

    session_code_match = re.search(r'[0-9A-Z\-]+', session_info)
    session_code = session_code_match.group() if session_code_match else "未入力"

    # フォーマット出力
    output = f"""{info['Conference']}

<{info['Abbreviation']}（AI）>

{info['Author'].replace('，', ', ')}:
**_{info['Title']}_**
{formatted_date} {time_str} {session_code} セッション ({info['Page']})
""".strip()

    return output

@app.route('/', methods=['GET', 'POST'])
def index():
    formatted = ''
    input_text = ''
    field_map = {}

    if request.method == 'POST':
        input_text = request.form['input_text']
        cells = input_text.strip().split('\t')
        field_map = fill_fields(cells)
        formatted = format_text(field_map)

    return render_template('index.html', input_text=input_text, formatted=formatted, field_map=field_map)

if __name__ == '__main__':
    app.run(debug=True)
