from flask import Flask, render_template, request

app = Flask(__name__)

# 必要なフィールド名（スプレッドシートの順に対応）
FIELDS = [
    "Abbreviation", "Presentation Date", "Author", "Title", "Conference",
    "Publisher", "Volume", "Number", "Presentation Number", "Page",
    "Organizer", "Begin", "End", "Venue"
]

def fill_fields(raw_cells):
    # 先頭の3列（◯）は無視
    cells = raw_cells[3:]
    while len(cells) < len(FIELDS):
        cells.append("")

    # 空のセルは「未入力」で補完
    info = {}
    for i, key in enumerate(FIELDS):
        info[key] = cells[i].strip() if cells[i].strip() else "未入力"
    return info

def format_text(info):
    import datetime
    import re

    # 日付の整形
    try:
        date_obj = datetime.datetime.strptime(info["Presentation Date"], "%Y/%m/%d")
        weekday = "日月火水木金土"[date_obj.weekday()]
        formatted_date = f"{date_obj.month}/{date_obj.day}({weekday})"
    except Exception:
        formatted_date = info["Presentation Date"]

    # セッション情報から時間抽出（表記揺れ対応）
    session_info = info["Presentation Number"]

    time_match = re.search(r'(\d{1,2}[:：]\d{2})[^0-9:：]{0,10}(\d{1,2}[:：]\d{2})', session_info)
    if time_match:
        start_time = time_match.group(1).replace("：", ":")
        end_time = time_match.group(2).replace("：", ":")
        time_str = f"{start_time}-{end_time}"
    else:
        time_str = "未入力"

    # セッションコード（最初の英数字記号群）
    session_code_match = re.search(r'[0-9A-Z]+(?:-[0-9A-Z]+)?', session_info)
    session_code = session_code_match.group() if session_code_match else "未入力"

    # ConferenceとAbbreviationの重複確認
    abbreviation_line = f"\n<{info['Abbreviation']}>" if info["Abbreviation"] not in info["Conference"] else ""

    # 出力整形
    output = f"""{info['Conference']}{abbreviation_line}

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
