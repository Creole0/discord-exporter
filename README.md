# Discord 频道导出工具

导出Discord论坛帖子和普通频道消息到Excel/TXT/HTML

## 功能

- 支持论坛频道和普通文字频道
- 按日期时间范围筛选（精确到小时和分钟）
- 导出格式：Excel、TXT、HTML
- 包含消息原始链接
- 后台异步处理，避免超时

## 部署到Zeabur

1. Fork这个仓库到你的GitHub
2. 登录 [Zeabur](https://zeabur.com)
3. 创建新项目 → 从GitHub导入
4. 选择这个仓库
5. 等待部署完成

## 本地运行

### Windows 用户（推荐）

**首次使用**：
```bash
双击运行 "首次安装.bat"
```

**日常启动**：
```bash
双击运行 "启动.bat"
```

更多批处理文件说明请查看 [批处理文件说明.md](批处理文件说明.md)

### 手动运行

```bash
pip install -r requirements.txt
python app.py
```

访问 http://localhost:5000
