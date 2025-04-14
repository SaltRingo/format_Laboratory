from flask import Flask, render_template, request

app = Flask(__name__)

def format_text(input_text):
    # タブ区切りで分割
    cells = input_text.strip().split('\t')

    if len(cells) < 13:
        return "⚠ 入力データが不足しています。"

    group = cells[0]  # 人工知能と知識処理研究会
    date = cells[1]   # 2025/2/19
    authors = cells[2]  # 中村詩織，菊地真人，大囿忠親
    title = cells[3]  # 発表タイトル
    event = cells[4]  # SMASH25 Winter Symposium
    session_info = cells[7]  # SIG-AI(2) 11:50-12:10
    page = cells[8]   # 6p

    # 日付の整形
    import datetime
    try:
        date_obj = datetime.datetime.strptime(date, '%Y/%m/%d')
        weekday = '日月火水木金土'[date_obj.weekday()]
        formatted_date = f"{date_obj.month}/{date_obj.day}({weekday})"
    except Exception as e:
        formatted_date = date

    # 時間抽出
    import re
    time_match = re.search(r'\d{1,2}:\d{2}-\d{2}:\d{2}', session_info)
    time_str = time_match.group() if time_match else ''

    # セッション抽出
    session_match = re.search(r'SIG-[^\s]+', session_info)
    session = session_match.group() if session_match else ''

    # 整形済み出力
    output = f"""{event}

<{group}（AI）>

{authors.replace('，', ', ')}:
**_{title}_**
{formatted_date} {time_str} {session} セッション ({page})
""".strip()

    return output


@app.route('/', methods=['GET', 'POST'])
def index():
    formatted = ''
    input_text = ''
    if request.method == 'POST':
        input_text = request.form['input_text']
        formatted = format_text(input_text)
    return render_template('index.html', input_text=input_text, formatted=formatted)


if __name__ == '__main__':
    app.run(debug=True)
