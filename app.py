"""
Discord 频道导出工具 - Flask后端
支持论坛频道和普通频道
"""

from flask import Flask, render_template, request, jsonify, send_file
import requests
import time
from datetime import datetime
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import os
import re

app = Flask(__name__)

# 默认Bot Token（从环境变量读取，或使用空字符串）
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")

API_BASE = "https://discord.com/api/v9"


def get_headers():
    return {"Authorization": f"Bot {BOT_TOKEN}"}


def snowflake_to_datetime(snowflake_id):
    timestamp_ms = (int(snowflake_id) >> 22) + 1420070400000
    return datetime.fromtimestamp(timestamp_ms / 1000)


def api_get(endpoint, params=None):
    url = f"{API_BASE}{endpoint}"
    while True:
        r = requests.get(url, headers=get_headers(), params=params)
        if r.status_code == 429:
            retry = r.json().get("retry_after", 1)
            time.sleep(retry)
            continue
        return r


def parse_discord_url(url):
    """从Discord URL提取服务器ID和频道ID"""
    match = re.search(r"/channels/(\d+)/(\d+)", url)
    if match:
        return match.group(1), match.group(2)  # guild_id, channel_id
    return None, None


def get_channel_info(channel_id):
    """获取频道信息"""
    r = api_get(f"/channels/{channel_id}")
    if r.status_code == 200:
        return r.json()
    return None


def get_all_threads(forum_id):
    """获取论坛所有帖子"""
    threads = []

    # 活跃帖子
    r = api_get(f"/channels/{forum_id}/threads/active")
    if r.status_code == 200:
        threads.extend(r.json().get("threads", []))

    # 归档帖子
    params = {"limit": 100}
    while True:
        r = api_get(f"/channels/{forum_id}/threads/archived/public", params)
        if r.status_code != 200:
            break
        data = r.json()
        archived = data.get("threads", [])
        if not archived:
            break
        threads.extend(archived)
        if not data.get("has_more"):
            break
        params["before"] = archived[-1]["thread_metadata"]["archive_timestamp"]

    return threads


def get_channel_messages(channel_id, date_from=None, date_to=None):
    """获取频道消息"""
    messages = []
    params = {"limit": 100}

    while True:
        r = api_get(f"/channels/{channel_id}/messages", params)
        if r.status_code != 200:
            break
        batch = r.json()
        if not batch:
            break

        for msg in batch:
            msg_time = snowflake_to_datetime(msg["id"])
            # 时间筛选
            if date_from and msg_time < date_from:
                continue
            if date_to and msg_time > date_to:
                continue
            messages.append(msg)

        if len(batch) < 100:
            break
        params["before"] = batch[-1]["id"]
        time.sleep(0.3)

    return messages


def export_to_excel(threads_data, filename):
    """导出到Excel"""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "消息导出"

    headers = [
        "频道/帖子",
        "创建时间",
        "消息作者",
        "消息时间",
        "消息内容",
        "附件",
        "消息链接",
    ]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill(
            start_color="5865F2", end_color="5865F2", fill_type="solid"
        )

    row = 2
    for thread in threads_data:
        for msg in thread["messages"]:
            ws.cell(row=row, column=1, value=thread["name"])
            ws.cell(row=row, column=2, value=thread["created"])
            ws.cell(row=row, column=3, value=msg["author"])
            ws.cell(row=row, column=4, value=msg["time"])
            ws.cell(row=row, column=5, value=msg["content"])
            ws.cell(row=row, column=6, value=msg["attachments"])
            ws.cell(row=row, column=7, value=msg["link"])
            row += 1

    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 18
    ws.column_dimensions["C"].width = 15
    ws.column_dimensions["D"].width = 20
    ws.column_dimensions["E"].width = 80
    ws.column_dimensions["F"].width = 50
    ws.column_dimensions["G"].width = 60

    wb.save(filename)
    return row - 1


def export_to_txt(threads_data, filename):
    """导出到TXT"""
    with open(filename, "w", encoding="utf-8") as f:
        for thread in threads_data:
            f.write(f"{'='*60}\n")
            f.write(f"频道/帖子: {thread['name']}\n")
            f.write(f"创建时间: {thread['created']}\n")
            f.write(f"{'='*60}\n\n")

            for msg in thread["messages"]:
                f.write(f"[{msg['time']}] {msg['author']}:\n")
                f.write(f"{msg['content']}\n")
                if msg["attachments"]:
                    f.write(f"附件: {msg['attachments']}\n")
                f.write(f"链接: {msg['link']}\n")
                f.write("\n")
            f.write("\n")


def export_to_html(threads_data, filename):
    """导出到HTML"""
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Discord导出</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #36393f; color: #dcddde; padding: 20px; }
        .thread { background: #2f3136; margin: 20px 0; border-radius: 8px; overflow: hidden; }
        .thread-header { background: #5865f2; color: white; padding: 15px; font-size: 18px; }
        .message { padding: 10px 15px; border-bottom: 1px solid #40444b; }
        .author { color: #7289da; font-weight: bold; }
        .time { color: #72767d; font-size: 12px; margin-left: 10px; }
        .content { margin-top: 5px; white-space: pre-wrap; }
        .attachment { color: #00aff4; font-size: 12px; margin-top: 5px; }
        .link { color: #00aff4; font-size: 12px; margin-top: 5px; }
        .link a { color: #00aff4; }
    </style>
</head>
<body>
"""

    for thread in threads_data:
        html += f'<div class="thread">\n'
        html += (
            f'<div class="thread-header">{thread["name"]} ({thread["created"]})</div>\n'
        )

        for msg in thread["messages"]:
            html += f'<div class="message">\n'
            html += f'<span class="author">{msg["author"]}</span>'
            html += f'<span class="time">{msg["time"]}</span>\n'
            html += f'<div class="content">{msg["content"]}</div>\n'
            if msg["attachments"]:
                html += f'<div class="attachment">附件: {msg["attachments"]}</div>\n'
            html += f'<div class="link"><a href="{msg["link"]}" target="_blank">查看原消息</a></div>\n'
            html += "</div>\n"

        html += "</div>\n"

    html += "</body></html>"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/check_token")
def check_token():
    """检查是否已设置Token"""
    return jsonify({"has_token": bool(BOT_TOKEN)})


@app.route("/api/set_token", methods=["POST"])
def set_token():
    global BOT_TOKEN
    data = request.json
    BOT_TOKEN = data.get("token", "")
    return jsonify({"success": True})


@app.route("/api/export", methods=["POST"])
def export():
    global BOT_TOKEN
    try:
        data = request.json

        urls = data.get("urls", [])
        date_from = data.get("date_from")
        date_to = data.get("date_to")
        export_format = data.get("format", "excel")

        if not BOT_TOKEN:
            return jsonify({"error": "请先设置Bot Token"}), 400

        if not urls:
            return jsonify({"error": "请输入至少一个频道链接"}), 400

        # 解析日期
        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d") if date_from else None
            date_to = datetime.strptime(date_to, "%Y-%m-%d") if date_to else None
            if date_to:
                date_to = date_to.replace(hour=23, minute=59, second=59)
        except:
            return jsonify({"error": "日期格式错误"}), 400

        # 收集所有消息
        all_threads_data = []
        total_messages = 0

        for url in urls:
            guild_id, channel_id = parse_discord_url(url)
            if not channel_id:
                continue

            # 获取频道信息
            channel_info = get_channel_info(channel_id)
            if not channel_info:
                continue

            channel_type = channel_info.get("type")
            channel_name = channel_info.get("name", "未知频道")

            # 类型15是论坛频道
            if channel_type == 15:
                # 论坛频道 - 获取帖子
                threads = get_all_threads(channel_id)

                for thread in threads:
                    thread_created = snowflake_to_datetime(thread["id"])

                    # 时间筛选
                    if date_from and thread_created < date_from:
                        continue
                    if date_to and thread_created > date_to:
                        continue

                    messages = get_channel_messages(thread["id"], date_from, date_to)
                    messages.sort(key=lambda m: m["id"])

                    thread_data = {
                        "name": thread["name"],
                        "created": thread_created.strftime("%Y-%m-%d %H:%M"),
                        "messages": [],
                    }

                    for msg in messages:
                        msg_data = {
                            "author": msg.get("author", {}).get("username", "未知"),
                            "time": snowflake_to_datetime(msg["id"]).strftime("%Y-%m-%d %H:%M:%S"),
                            "content": msg.get("content", ""),
                            "attachments": "\n".join([a.get("url", "") for a in msg.get("attachments", [])]),
                            "link": f"https://discord.com/channels/{guild_id}/{thread['id']}/{msg['id']}",
                        }
                        thread_data["messages"].append(msg_data)
                        total_messages += 1

                    if thread_data["messages"]:
                        all_threads_data.append(thread_data)

                    time.sleep(0.3)
            else:
                # 普通频道 - 直接获取消息
                messages = get_channel_messages(channel_id, date_from, date_to)
                messages.sort(key=lambda m: m["id"])

                if messages:
                    channel_created = snowflake_to_datetime(channel_id)
                    thread_data = {
                        "name": f"#{channel_name}",
                        "created": channel_created.strftime("%Y-%m-%d %H:%M"),
                        "messages": [],
                    }

                    for msg in messages:
                        msg_data = {
                            "author": msg.get("author", {}).get("username", "未知"),
                            "time": snowflake_to_datetime(msg["id"]).strftime("%Y-%m-%d %H:%M:%S"),
                            "content": msg.get("content", ""),
                            "attachments": "\n".join([a.get("url", "") for a in msg.get("attachments", [])]),
                            "link": f"https://discord.com/channels/{guild_id}/{channel_id}/{msg['id']}",
                        }
                        thread_data["messages"].append(msg_data)
                        total_messages += 1

                    all_threads_data.append(thread_data)

        if not all_threads_data:
            return jsonify({"error": "没有找到符合条件的消息"}), 400

        # 导出文件
        os.makedirs("exports", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if export_format == "excel":
            filename = f"exports/Discord导出_{timestamp}.xlsx"
            export_to_excel(all_threads_data, filename)
        elif export_format == "txt":
            filename = f"exports/Discord导出_{timestamp}.txt"
            export_to_txt(all_threads_data, filename)
        else:
            filename = f"exports/Discord导出_{timestamp}.html"
            export_to_html(all_threads_data, filename)

        return jsonify({
            "success": True,
            "filename": filename,
            "threads": len(all_threads_data),
            "messages": total_messages,
        })
    except Exception as e:
        return jsonify({"error": f"导出失败: {str(e)}"}), 500


@app.route("/api/download/<path:filename>")
def download(filename):
    filepath = os.path.join(os.getcwd(), filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({"error": "文件不存在"}), 404


if __name__ == "__main__":
    os.makedirs("exports", exist_ok=True)
    app.run(debug=True, port=5000)
