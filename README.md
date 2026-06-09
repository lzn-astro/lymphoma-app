# 淋巴瘤路径导航器

一个面向患者和家属的 Streamlit 科普导航应用，用于整理淋巴瘤常见检查、分型、治疗方案、药物副作用和随访路径。

## 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud 部署

1. 将 `app.py`、`requirements.txt`、`README.md` 和 `.streamlit/config.toml` 推送到 GitHub 仓库。
2. 打开 Streamlit Community Cloud，新建应用。
3. 选择仓库、分支和主文件 `app.py`。
4. 点击部署，等待构建完成后即可获得公开链接。

## 注意

本应用仅供健康科普参考，不能替代医生诊断或治疗建议。
