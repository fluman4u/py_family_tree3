# 部署指南

## 1. 概述

本文档介绍族谱可视化系统的各种部署方式，包括本地运行、Web 服务部署和桌面应用打包。

## 2. 环境要求

### 2.1 系统要求

| 操作系统    | 支持版本                            |
| ------- | ------------------------------- |
| Windows | Windows 7 及以上                   |
| Linux   | 主流发行版（Ubuntu 18.04+, CentOS 7+） |
| macOS   | macOS 10.13 及以上                 |

### 2.2 Python 版本

- **最低版本**：Python 3.8
- **推荐版本**：Python 3.10 或 3.11

### 2.3 硬件要求

| 资源  | 最低配置   | 推荐配置     |
| --- | ------ | -------- |
| CPU | 双核     | 四核及以上    |
| 内存  | 2 GB   | 4 GB 及以上 |
| 磁盘  | 500 MB | 1 GB 及以上 |

## 3. 安装步骤

### 3.1 获取源码

**方式一：Git 克隆**

```bash
git clone https://github.com/your-username/py_family_tree3.git
cd py_family_tree3
```

**方式二：下载压缩包**

1. 下载项目 ZIP 文件
2. 解压到目标目录
3. 进入项目目录

### 3.2 创建虚拟环境（推荐）

**Windows**：

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**Linux/macOS**：

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.3 安装依赖

```bash
pip install -r requirements.txt
```

**依赖列表**：

| 包名          | 用途         |
| ----------- | ---------- |
| pyvis       | 网络图可视化     |
| networkx    | 图数据结构      |
| flask       | Web 框架     |
| pyyaml      | YAML 解析    |
| pyinstaller | 桌面应用打包     |
| selenium    | 浏览器自动化（可选） |
| pillow      | 图像处理（可选）   |

### 3.4 验证安装

```bash
python -c "from src.model import Person; print('安装成功')"
```

## 4. 运行方式

### 4.1 命令行版本

**适用场景**：快速生成静态 HTML 文件

**运行命令**：

```bash
python app.py
```

**输出**：

- 生成 `family.html` 文件
- 控制台输出迁徙时间轴

**使用方式**：

1. 运行命令
2. 用浏览器打开 `family.html`

### 4.2 Web 版本

**适用场景**：交互式操作，支持动态选择根节点和展开层数

**运行命令**：

```bash
python web/app.py
```

**访问地址**：`http://127.0.0.1:5000`

**功能特性**：

- 选择任意成员作为根节点
- 设置展开层数
- 实时生成族谱图
- 查看迁徙时间轴

### 4.3 桌面应用

**适用场景**：无需命令行，双击运行

**开发模式运行**：

```bash
python desktop/main.py
```

**打包为 EXE**：

```bash
pyinstaller --onefile --name "族谱可视化系统" desktop/main.py
```

**Debian/Linux 推荐打包命令（使用 spec）**：

```bash
pyinstaller --noconfirm desktop/main.spec
```

**运行方式（Debian/Linux）**：

```bash
chmod +x dist/family-tree
./dist/family-tree
```

**打包参数说明**：

| 参数           | 说明         |
| ------------ | ---------- |
| `--onefile`  | 打包为单个文件    |
| `--name`     | 指定输出文件名    |
| `--windowed` | 无控制台窗口（可选） |
| `--icon`     | 指定图标文件（可选） |

**打包后位置**：`dist/族谱可视化系统.exe`

## 5. Web 服务部署

### 5.1 开发服务器

**启动命令**：

```bash
python web/app.py
```

**配置**：

- Host: `127.0.0.1`
- Port: `5000`
- Debug: `True`

**注意**：开发服务器仅适用于开发和测试，不建议用于生产环境。

### 5.2 生产环境部署

#### 5.2.1 使用 Gunicorn（Linux/macOS）

**安装 Gunicorn**：

```bash
pip install gunicorn
```

**启动命令**：

```bash
gunicorn -w 4 -b 0.0.0.0:5000 web.app:app
```

**参数说明**：

| 参数                | 说明      |
| ----------------- | ------- |
| `-w 4`            | 4 个工作进程 |
| `-b 0.0.0.0:5000` | 绑定地址和端口 |
| `web.app:app`     | 应用入口    |

#### 5.2.2 使用 Waitress（Windows）

**安装 Waitress**：

```bash
pip install waitress
```

**启动脚本**：

```python
from waitress import serve
from web.app import app

serve(app, host='0.0.0.0', port=5000)
```

#### 5.2.3 使用 uWSGI

**安装 uWSGI**：

```bash
pip install uwsgi
```

**启动命令**：

```bash
uwsgi --http :5000 --wsgi-file web/app.py --callable app
```

### 5.3 Nginx 反向代理

**Nginx 配置示例**：

```nginx
server {
    listen 80;
    server_name family.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/py_family_tree3/web/static/;
    }
}
```

### 5.4 Systemd 服务（Linux）

**创建服务文件** `/etc/systemd/system/family-tree.service`：

```ini
[Unit]
Description=Family Tree Visualization Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/py_family_tree3
ExecStart=/path/to/py_family_tree3/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 web.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**管理命令**：

```bash
sudo systemctl daemon-reload
sudo systemctl start family-tree
sudo systemctl enable family-tree
sudo systemctl status family-tree
```

## 6. Docker 部署

### 6.1 创建 Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "web/app.py"]
```

### 6.2 构建镜像

```bash
docker build -t family-tree:latest .
```

### 6.3 运行容器

```bash
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data --name family-tree family-tree:latest
```

**参数说明**：

| 参数                         | 说明     |
| -------------------------- | ------ |
| `-d`                       | 后台运行   |
| `-p 5000:5000`             | 端口映射   |
| `-v $(pwd)/data:/app/data` | 数据目录挂载 |
| `--name family-tree`       | 容器名称   |

### 6.4 Docker Compose

**docker-compose.yml**：

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    restart: always
```

**启动命令**：

```bash
docker-compose up -d
```

## 7. 数据准备

### 7.1 创建数据文件

**族谱数据**：编辑 `data/family.csv`

```csv
id,wbs,name,gender,birth_year,death_year,generation,clan_name,location,note
1,1,张始祖,M,1800,1870,1,张氏,陕西西安,始祖
2,1.1,张一,M,1825,1890,2,张氏,陕西西安,
...
```

**行辈配置**：编辑 `data/lineage.yaml`

```yaml
clan_name: 张氏
lineage_poem:
  - 忠
  - 厚
  - 传
  - 家
  - 久
```

### 7.2 生成测试数据

```bash
python src/generator.py
```

## 8. 配置说明

### 8.1 Web 应用配置

在 `web/app.py` 中可修改以下配置：

```python
app.run(
    debug=False,
    host='0.0.0.0',
    port=5000,
    use_reloader=False
)
```

| 参数           | 说明   | 默认值       |
| ------------ | ---- | --------- |
| debug        | 调试模式 | False     |
| host         | 监听地址 | 127.0.0.1 |
| port         | 监听端口 | 5000      |
| use_reloader | 自动重载 | False     |

### 8.2 可视化配置

在 `src/visualize.py` 中可修改以下配置：

```python
net = Network(
    height="800px",
    width="100%",
    bgcolor="#ffffff",
    font_color="black"
)
```

**布局选项**：

```python
net.set_options("""
{
  "layout": {
    "hierarchical": {
      "levelSeparation": 150,
      "nodeSpacing": 200
    }
  }
}
""")
```

## 9. 安全建议

### 9.1 生产环境安全

1. **关闭 Debug 模式**：
   
   ```python
   app.run(debug=False)
   ```

2. **使用环境变量管理敏感配置**：
   
   ```python
   import os
   SECRET_KEY = os.environ.get('SECRET_KEY', 'default-key')
   ```

3. **添加身份验证**（如需）：
   
   ```python
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   ```

### 9.2 数据安全

1. 定期备份 CSV 和 YAML 文件
2. 敏感信息可加密存储
3. 限制文件访问权限

## 10. 性能优化

### 10.1 数据规模建议

| 数据规模       | 建议配置      |
| ---------- | --------- |
| < 100 人    | 任意配置      |
| 100-500 人  | 推荐 4GB 内存 |
| 500-2000 人 | 推荐 8GB 内存 |
| > 2000 人   | 建议使用数据库存储 |

### 10.2 渲染优化

1. 使用 `max_depth` 限制展开层数
2. 使用 `gen_min/gen_max` 过滤世代范围
3. 分批渲染大型族谱

### 10.3 Web 服务优化

1. 启用 Gzip 压缩
2. 使用 CDN 加速静态资源
3. 配置浏览器缓存

## 11. 常见问题

### Q1: 端口被占用怎么办？

**解决方案**：更换端口或关闭占用进程

```bash
python web/app.py --port 5001
```

或修改代码：

```python
app.run(port=5001)
```

### Q2: 打包后的 EXE 无法运行？

**解决方案**：

1. 检查是否缺少数据文件
2. 使用 `--add-data` 参数添加数据文件
3. 检查杀毒软件是否拦截

### Q3: 中文显示乱码？

**解决方案**：

1. 确保 CSV 文件使用 UTF-8-BOM 编码
2. 确保系统支持中文字体

### Q4: 浏览器无法访问？

**解决方案**：

1. 检查防火墙设置
2. 确认服务已启动
3. 尝试使用 `0.0.0.0` 监听所有地址

## 12. 维护指南

### 12.1 日志记录

添加日志记录：

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='family_tree.log'
)
```

### 12.2 数据备份

定期备份数据文件：

```bash
cp data/family.csv backup/family_$(date +%Y%m%d).csv
```

### 12.3 版本更新

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```


### Q6: Linux 打包后报错 `No module named 'web'`？

**原因**：PyInstaller 未正确收集 `web` 包或模板/静态资源。

**解决方案**：

1. 使用仓库内 `desktop/main.spec` 进行打包：

```bash
pyinstaller --noconfirm desktop/main.spec
```

2. 确保在项目根目录执行打包命令。
3. 运行 `dist/family-tree`（Linux 可执行文件，不是 `.exe`）。


### Q7: Linux 打包后报错 `pyvis template.html not found`？

**原因**：PyInstaller 未收集 `pyvis/templates`。

**解决方案**：

1. 使用仓库内最新 `desktop/main.spec`（已包含 `pyvis/templates`）。
2. 重新打包：

```bash
pyinstaller --noconfirm desktop/main.spec
```
