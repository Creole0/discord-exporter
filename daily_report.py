"""
Discord 每日/每周报告自动化脚本
导出聊天记录 → Gemini 文字摘要 → 发送飞书群
"""

import requests as req
import time
import os
import re
import sys
from datetime import datetime, timedelta
from openai import OpenAI

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ========== 配置 ==========

DISCORD_BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
AI_API_BASE = os.environ.get("AI_API_BASE", "")
AI_API_KEY = os.environ.get("AI_API_KEY", "")
LARK_WEBHOOK = os.environ.get("LARK_WEBHOOK", "")

CHANNEL_URLS = [
    "https://discord.com/channels/1372503951869607976/1373976286736945243",
    "https://discord.com/channels/1372503951869607976/1399246576416981073",
    "https://discord.com/channels/1372503951869607976/1399305129483698216",
    "https://discord.com/channels/1372503951869607976/1463475928045715497",
    "https://discord.com/channels/1372503951869607976/1463475985499291698",
    "https://discord.com/channels/1372503951869607976/1374268433373335613",
]

DAYS_BACK = 7
API_BASE = "https://discord.com/api/v9"

# ========== Discord 抓取 ==========

def get_headers():
    return {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}


def snowflake_to_datetime(sid):
    return datetime.fromtimestamp(((int(sid) >> 22) + 1420070400000) / 1000)


def api_get(endpoint, params=None):
    url = f"{API_BASE}{endpoint}"
    while True:
        r = req.get(url, headers=get_headers(), params=params)
        if r.status_code == 429:
            retry = r.json().get("retry_after", 1)
            print(f"  速率限制，等待 {retry}s...")
            time.sleep(retry)
            continue
        return r


def parse_url(url):
    m = re.search(r"/channels/(\d+)/(\d+)", url)
    return (m.group(1), m.group(2)) if m else (None, None)


def get_channel_info(channel_id):
    r = api_get(f"/channels/{channel_id}")
    return r.json() if r.status_code == 200 else None


def get_all_threads(forum_id):
    threads = []
    r = api_get(f"/channels/{forum_id}/threads/active")
    if r.status_code == 200:
        threads.extend(r.json().get("threads", []))
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


def get_messages(channel_id, date_from, date_to):
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
            t = snowflake_to_datetime(msg["id"])
            if date_from and t < date_from:
                continue
            if date_to and t > date_to:
                continue
            messages.append(msg)
        if len(batch) < 100:
            break
        params["before"] = batch[-1]["id"]
        time.sleep(0.3)
    return messages


def export_channels(urls, date_from, date_to):
    all_text = []
    total_msgs = 0

    for url in urls:
        guild_id, channel_id = parse_url(url)
        if not channel_id:
            print(f"[跳过] 无效链接: {url}")
            continue

        info = get_channel_info(channel_id)
        if not info:
            print(f"[跳过] 无法获取频道信息: {channel_id}")
            continue

        ch_type = info.get("type")
        ch_name = info.get("name", "未知频道")
        print(f"[处理] #{ch_name} (type={ch_type})")

        if ch_type == 15:
            threads = get_all_threads(channel_id)
            print(f"  找到 {len(threads)} 个帖子")
            for thread in threads:
                tc = snowflake_to_datetime(thread["id"])
                if date_from and tc < date_from:
                    continue
                if date_to and tc > date_to:
                    continue
                msgs = get_messages(thread["id"], date_from, date_to)
                if msgs:
                    msgs.sort(key=lambda m: m["id"])
                    all_text.append(f"{'='*50}\n帖子: {thread['name']}\n{'='*50}")
                    for msg in msgs:
                        author = msg.get("author", {}).get("username", "未知")
                        t = snowflake_to_datetime(msg["id"]).strftime("%Y-%m-%d %H:%M:%S")
                        content = msg.get("content", "")
                        all_text.append(f"[{t}] {author}: {content}")
                        total_msgs += 1
                    all_text.append("")
                time.sleep(0.3)
        else:
            msgs = get_messages(channel_id, date_from, date_to)
            if msgs:
                msgs.sort(key=lambda m: m["id"])
                all_text.append(f"{'='*50}\n频道: #{ch_name}\n{'='*50}")
                for msg in msgs:
                    author = msg.get("author", {}).get("username", "未知")
                    t = snowflake_to_datetime(msg["id"]).strftime("%Y-%m-%d %H:%M:%S")
                    content = msg.get("content", "")
                    all_text.append(f"[{t}] {author}: {content}")
                    total_msgs += 1
                all_text.append("")

    return "\n".join(all_text), total_msgs

# ========== Gemini 摘要 ==========

SUMMARY_PROMPT = """你是一个 Discord 社群运营分析师。请根据以下聊天记录生成一份详细的周报。

格式要求：
- 用中文书写
- 支持飞书卡片的轻量 Markdown：**加粗** 和 [链接](url) 可以用，但不要用 # 标题、``` 代码块、> 引用块、表格
- 用 ━━━ 作为板块之间的分隔符（独占一行）
- 引用用户原文时用「」括起来

报告结构（必须包含以下所有板块）：

**📊 概览**
统计周期、总消息数、活跃用户数、涉及频道数

━━━

**👍 好评**
用户对产品/社群的正面反馈，列出 2-5 条，每条附上用户名和原文引用

**😐 中评**
用户提出的建议或改进意见，列出 2-5 条，每条附上用户名和原文引用

**👎 差评**
用户的不满、抱怨或 bug 反馈，列出 2-5 条，每条附上用户名和原文引用
（如果某个类别没有相关内容，写"本周暂无"）

━━━

**🔥 讨论热点 TOP 3-5**
每个热点包含：话题名称、简要总结(50字内)、相关关键词

━━━

**📢 重要消息与公告**
列出 2-5 条重要消息，每条包含：发送者、时间、消息原文

━━━

**🔗 实用资源与链接**
如果聊天中有人分享了链接、教程、工具等资源，列出来，包含：分享者、资源描述、原始链接URL
（如果没有分享链接，写"本周暂无资源分享"）

━━━

**💬 精彩对话与金句**
挑选 2-3 段有趣/有价值的对话片段，直接引用用户原文

━━━

**❓ 问题与解答**
如果有用户提问并得到回答，列出 2-3 组 Q&A，附上提问者和回答者

━━━

**👤 活跃用户 TOP 5**
用户名、消息数、一句话概括其发言特点

━━━

**💡 一句话总结**
用一句话概括本周社群氛围

聊天记录如下：
"""


def generate_summary(chat_text):
    client = OpenAI(base_url=AI_API_BASE, api_key=AI_API_KEY)

    model_name = "gemini-3-flash"
    for attempt in range(3):
        try:
            print(f"  尝试模型: {model_name} (第{attempt+1}次)")
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SUMMARY_PROMPT.strip()},
                    {"role": "user", "content": chat_text},
                ],
            )
            text = response.choices[0].message.content or ""
            if text.strip():
                print(f"  成功使用模型: {model_name}")
                return text.strip()
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                wait = 15 * (attempt + 1)
                print(f"  额度限制，等待 {wait}s 后重试...")
                time.sleep(wait)
            elif "503" in err_str or "UNAVAILABLE" in err_str:
                wait = 10 * (attempt + 1)
                print(f"  服务暂不可用，等待 {wait}s 后重试...")
                time.sleep(wait)
            else:
                print(f"  出错: {err_str[:200]}")
                break
    return "摘要生成失败"

# ========== 飞书卡片发送 ==========

def build_card(report, period):
    sections = report.split("━━━")
    elements = []
    for section in sections:
        text = section.strip()
        if not text:
            continue
        elements.append({"tag": "markdown", "content": text})
        elements.append({"tag": "hr"})
    if elements and elements[-1].get("tag") == "hr":
        elements.pop()

    return {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"content": f"📋 Discord 社群周报 ({period})", "tag": "plain_text"},
                "template": "purple",
            },
            "elements": elements,
        },
    }


def send_lark(report, period):
    payload = build_card(report, period)
    r = req.post(LARK_WEBHOOK, json=payload)
    print(f"[飞书] 状态码={r.status_code}, 返回={r.text}")
    return r.status_code == 200

# ========== 主流程 ==========

def main():
    now = datetime.now()
    date_from = now - timedelta(days=DAYS_BACK)
    date_to = now
    period = f"{date_from.strftime('%m/%d')} - {date_to.strftime('%m/%d')}"

    print(f"\n{'='*60}")
    print(f"  Discord 周报自动生成")
    print(f"  时间范围: {period}")
    print(f"  频道数: {len(CHANNEL_URLS)}")
    print(f"{'='*60}\n")

    # 1. 导出
    print("[Step 1/3] 导出聊天记录...")
    chat_text, total = export_channels(CHANNEL_URLS, date_from, date_to)

    if not chat_text.strip():
        print("[结束] 没有找到消息，跳过后续步骤")
        return

    print(f"  导出完成: {total} 条消息\n")

    # 保存到本地
    os.makedirs("exports", exist_ok=True)
    txt_path = f"exports/周报原始_{now.strftime('%Y%m%d_%H%M%S')}.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(chat_text)
    print(f"  已保存到: {txt_path}\n")

    # 2. Gemini 摘要
    print("[Step 2/3] 生成 Gemini 摘要...")
    summary = generate_summary(chat_text)
    print(f"  摘要长度: {len(summary)} 字\n")
    print("--- 摘要预览 ---")
    print(summary[:500])
    if len(summary) > 500:
        print("...(截断)")
    print("--- 预览结束 ---\n")

    # 3. 发送飞书
    if "摘要生成失败" in summary:
        print("[跳过] 摘要生成失败，不发送到飞书\n")
    else:
        print("[Step 3/3] 发送到飞书群...")
        ok = send_lark(summary, period)
        if ok:
            print("  发送成功!\n")
        else:
            print("  发送失败，请检查 Webhook URL\n")

    print(f"{'='*60}")
    print(f"  全部完成!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
