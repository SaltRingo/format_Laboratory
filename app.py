from flask import Flask, render_template, request
from collections import defaultdict
import datetime
import re

app = Flask(__name__)

FIELDS = [
    "Abbreviation", "Presentation Date", "Author", "Title", "Conference",
    "Publisher", "Volume", "Number", "Presentation Number", "Page",
    "Organizer", "Begin", "End", "Venue"
]

def fill_fields(raw_cells):
    cells = raw_cells[3:]
    while len(cells) < len(FIELDS):
        cells.append("")
    info = {}
    for i, key in enumerate(FIELDS):
        info[key] = cells[i].strip() if cells[i].strip() else "未入力"
    return info

def format_date(date_str):
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y/%m/%d")
        weekday = "日月火水木金土"[date_obj.weekday()]
        return f"{date_obj.month}/{date_obj.day}({weekday})"
    except Exception:
        return date_str

def extract_time(session_info):
    match = re.search(r'(\d{1,2}[:：]\d{2})[^0-9:：]{0,10}(\d{1,2}[:：]\d{2})', session_info)
    if match:
        start_time = match.group(1).replace("：", ":")
        end_time = match.group(2).replace("：", ":")
        return f"{start_time}-{end_time}"
    return "未入力"

def extract_session_code(session_info):
    match = re.search(r'[0-9A-Z]+(?:-[0-9A-Z]+)?', session_info)
    return match.group() if match else "未入力"

def format_entry(info):
    formatted_date = format_date(info["Presentation Date"])
    time_str = extract_time(info["Presentation Number"])
    session_code = extract_session_code(info["Presentation Number"])
    return f"{info['Author'].replace('，', ', ')}:\n**_{info['Title']}_**\n{formatted_date} {time_str} {session_code} セッション ({info['Page']})"

def group_entries(entries):
    grouped = defaultdict(list)
    for entry in entries:
        key = (entry["Conference"], entry["Abbreviation"])
        grouped[key].append(entry)
    return grouped

def format_all(entries):
    grouped = group_entries(entries)
    output_lines = []
    shown_conferences = set()

    for (conf, abbr), group in grouped.items():
        if conf not in shown_conferences:
            output_lines.append(conf)
            shown_conferences.add(conf)
        if abbr != "未入力" and abbr not in conf:
            output_lines.append(f"\n<{abbr}>\n")
        else:
            output_lines.append("")
        for entry in group:
            output_lines.append(format_entry(entry))
            output_lines.append("")  # 改行を各発表後に追加

    return "\n".join(line for line in output_lines if line.strip())

@app.route('/', methods=['GET', 'POST'])
def index():
    input_text = ''
    formatted = ''
    if request.method == 'POST':
        input_text = request.form['input_text']
        rows = [line for line in input_text.strip().split('\n') if line.strip()]
        entries = [fill_fields(row.split('\t')) for row in rows]
        formatted = format_all(entries)

    return render_template('index.html', input_text=input_text, formatted=formatted)

if __name__ == '__main__':
    app.run(debug=True)
