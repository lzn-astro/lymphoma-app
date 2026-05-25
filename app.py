import streamlit as st

st.set_page_config(
    page_title="淋巴瘤导航器",
    layout="centered",
    initial_sidebar_state="expanded"
)

# =========================
# 样式优化（关键）
# =========================
st.markdown("""
<style>
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: #f8f9fa;
    margin-bottom: 15px;
}
.big-font {
    font-size:18px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Sidebar
# =========================
page = st.sidebar.radio(
    "导航",
    ["🏠 首页", "🪜 路径导航", "🧬 DLBCL"]
)

st.sidebar.markdown("---")
st.sidebar.caption("⚠️ 仅供科普参考")

# =========================
# 首页
# =========================
if page == "🏠 首页":
    st.title("🧭 淋巴瘤路径导航器")

    st.warning("本工具仅用于健康科普，不替代医生诊断")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🪜 路径导航")
        st.write("帮助你判断下一步应该做什么")
        if st.button("进入导航"):
            st.session_state.page = "🪜 路径导航"

    with col2:
        st.markdown("### 🧬 疾病了解")
        st.write("了解淋巴瘤类型和治疗")
        if st.button("查看 DLBCL"):
            st.session_state.page = "🧬 DLBCL"

# =========================
# 路径导航
# =========================
elif page == "🪜 路径导航":

    st.title("🪜 路径导航")

    stage = st.radio(
        "请选择你的当前阶段：",
        ["🟡 未确诊", "🟠 检查中", "🔴 已确诊", "🟢 治疗中"]
    )

    st.markdown("---")

    # -------- 未确诊 --------
    if stage == "🟡 未确诊":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🟡 未确诊阶段")

        st.markdown("""
**常见情况：**
- 淋巴结肿大  
- 发热 / 盗汗 / 体重下降  
""")

        st.info("👉 建议尽快去血液科或肿瘤科检查")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------- 检查中 --------
    elif stage == "🟠 检查中":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🟠 检查阶段")

        st.warning("🔬 活检是确诊的关键步骤")

        st.markdown("""
你可能正在：
- 做CT / 血液检查  
- 等待病理结果  
""")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------- 已确诊 --------
    elif stage == "🔴 已确诊":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔴 已确诊阶段")

        lymphoma = st.selectbox(
            "你的类型（如果知道）：",
            ["不清楚", "DLBCL"]
        )

        if lymphoma == "DLBCL":
            st.success("DLBCL 是常见类型，可治疗性较好")

            if st.button("👉 查看详细说明"):
                st.session_state.page = "🧬 DLBCL"

        st.markdown("""
下一步通常：
- 分型  
- 分期  
- 制定治疗方案  
""")

        st.markdown('</div>', unsafe_allow_html=True)

    # -------- 治疗中 --------
    elif stage == "🟢 治疗中":
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🟢 治疗阶段")

        treatment = st.selectbox(
            "了解治疗方式：",
            ["化疗", "免疫治疗", "CAR-T"]
        )

        if treatment == "化疗":
            st.info("化疗是常见治疗方式，分周期进行")
        elif treatment == "免疫治疗":
            st.info("帮助免疫系统识别肿瘤")
        elif treatment == "CAR-T":
            st.info("用于部分复发或难治情况")

        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DLBCL 页面（美化版）
# =========================
elif page == "🧬 DLBCL":

    st.title("🧬 DLBCL（弥漫大B细胞淋巴瘤）")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 📌 什么是 DLBCL？")
    st.write("一种进展较快的非霍奇金淋巴瘤，起源于B细胞")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### ⚠️ 常见症状")
        st.write("淋巴结肿大 / 发热 / 盗汗 / 体重下降")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🔬 如何确诊")
        st.write("👉 活检是确诊金标准")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### 💊 常见治疗")
    st.write("化疗 + 免疫治疗 / CAR-T（部分情况）")
    st.markdown('</div>', unsafe_allow_html=True)

    st.warning("⚠️ 本内容仅用于科普")

# =========================
# 页面跳转逻辑
# =========================
if "page" in st.session_state:
    page = st.session_state.page
    del st.session_state.page
    st.rerun()
