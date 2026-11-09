import streamlit as st
import requests
import os
import pandas as pd
import altair as alt
from datetime import datetime

# ================= 页面基础配置 =================
st.set_page_config(page_title="智慧交通 AI 监控大屏", page_icon="🚦", layout="wide")

# 自定义 CSS：极简亮色 + 玻璃拟物 + 柔和阴影
custom_css = """
<style>
    .stApp { background-color: #F4F7F6; color: #1E293B; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF; border-radius: 16px; padding: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #E2E8F0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08); }
    div[data-testid="stMetricValue"] { color: #0F172A !important; font-weight: 700 !important; }
    h1 {
        background: -webkit-linear-gradient(45deg, #2563EB, #06B6D4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important;
    }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 1px solid #E2E8F0; }
    
    /* 浅蓝色定制按钮 */
    div[data-testid="stFormSubmitButton"] > button, button[kind="primary"] {
        background-color: #3B82F6 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stFormSubmitButton"] > button:hover, button[kind="primary"]:hover {
        background-color: #2563EB !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8000"

# ================= 状态管理 =================
if "token" not in st.session_state:
    st.session_state.token = None


# ================= 登录页面 =================
def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h1 style='text-align: center;'>🚦 智慧交通 AI 监控平台</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h4 style='text-align: center; color: #64748B; font-weight: 400;'>Enterprise AI Video Analytics System</h4>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.container(border=True):
            with st.form("login_form"):
                st.markdown(
                    "<p style='color: #334155; font-weight: 500;'>管理员安全登录</p>",
                    unsafe_allow_html=True,
                )
                username = st.text_input("用户名", placeholder="请输入 admin")
                password = st.text_input(
                    "密码", type="password", placeholder="请输入 123456"
                )
                submit = st.form_submit_button("进入大屏", use_container_width=True)

                if submit:
                    response = requests.post(
                        f"{API_URL}/api/auth/login",
                        data={"username": username, "password": password},
                    )
                    if response.status_code == 200:
                        st.session_state.token = response.json().get("access_token")
                        st.rerun()
                    else:
                        st.error("用户名或密码错误！")


if st.session_state.token is None:
    login_page()
    st.stop()

# ================= 侧边栏控制台 =================
with st.sidebar:
    st.markdown("<h2 style='color: #0F172A;'>控制面板</h2>", unsafe_allow_html=True)
    st.info("👤 身份：超级管理员")
    st.markdown("---")
    st.markdown("### ⚙️ 系统状态")
    st.success("🟢 后端服务：正常")
    st.success("🟢 AI 引擎：YOLOv11 (ONNX)")
    st.success("🟢 消息队列：Redis")
    st.success("🟢 数据库：MySQL")

    st.markdown("---")
    st.markdown("### 📊 数据查询")
    # 滑块拉取数据条数
    query_limit = st.slider(
        "拉取历史报警条数", min_value=10, max_value=500, value=20, step=10
    )

    # 刷新按钮
    if st.button("🔄 刷新大屏数据", use_container_width=True):
        st.rerun()

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.token = None
        st.rerun()

# ================= 主页面 =================

# 请求头
headers = {"Authorization": f"Bearer {st.session_state.token}"}

# 拉取数据
cameras_resp = requests.get(f"{API_URL}/api/cameras/", headers=headers)
alerts_resp = requests.get(
    f"{API_URL}/api/alerts/?limit={query_limit}", headers=headers
)

st.markdown(
    "<h1 style='margin-bottom: 0;'>城市交通 AI 实时监控大屏</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='color: #64748B; font-size: 14px; margin-bottom: 20px;'>Urban Traffic Intelligent Monitoring & Alarm Platform</p>",
    unsafe_allow_html=True,
)

if cameras_resp.status_code == 200 and alerts_resp.status_code == 200:
    cameras_data = cameras_resp.json()
    alerts_data = alerts_resp.json()
    alerts_list = alerts_data.get("data", [])
    total_alerts = alerts_data.get("total", 0)

    # --- 顶部数据统计卡片 ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📹 在线设备", len(cameras_data.get("data", [])), "运行正常")
    col2.metric("🚨 累计报警", total_alerts, "需关注")
    col3.metric("🤖 AI 推理耗时", "4.4 ms", "极速响应", delta_color="off")
    col4.metric("⚡ 系统并发", "高", "Redis 削峰", delta_color="off")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- 下半部分：左侧图表 + 右侧图片墙 ---
    left_col, right_col = st.columns([1.2, 2])

    # 左侧：报警趋势图
    with left_col:
        with st.container(border=True):
            st.markdown(
                "<h4 style='color: #334155; margin-top:0;'>📊 报警趋势分析</h4>",
                unsafe_allow_html=True,
            )
            if len(alerts_list) > 0:
                df = pd.DataFrame(alerts_list)
                df["created_at"] = pd.to_datetime(df["created_at"])
                df["Time"] = df["created_at"].dt.strftime("%H:%M")

                chart = (
                    alt.Chart(df)
                    .mark_area(
                        line={"color": "#2563EB"},
                        color=alt.Gradient(
                            gradient="linear",
                            stops=[
                                alt.GradientStop(color="#DBEAFE", offset=0),
                                alt.GradientStop(color="#FFFFFF", offset=1),
                            ],
                            x1=1,
                            x2=1,
                            y1=1,
                            y2=0,
                        ),
                    )
                    .encode(
                        x=alt.X(
                            "Time",
                            sort=None,
                            title="时间",
                            axis=alt.Axis(labelAngle=-45),
                        ),
                        y=alt.Y("count()", title="报警数量"),
                        tooltip=["count()"],
                    )
                    .properties(height=280)
                    .configure_axis(
                        grid=True,
                        gridColor="#F1F5F9",
                        labelColor="#64748B",
                        titleColor="#64748B",
                    )
                    .configure_view(strokeWidth=0)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("暂无数据可绘制图表")

    # 右侧：抓拍图片墙
    with right_col:
        with st.container(border=True):
            st.markdown(
                "<h4 style='color: #334155; margin-top:0;'>📸 最新抓拍取证</h4>",
                unsafe_allow_html=True,
            )
            if len(alerts_list) == 0:
                st.info("✅ 当前路况良好，无报警记录。")
            else:
                display_alerts = alerts_list[:6]
                cols = st.columns(3)
                for index, alert in enumerate(display_alerts):
                    with cols[index % 3]:
                        img_path = alert["snapshot_path"]
                        if os.path.exists(img_path):
                            st.image(img_path, use_container_width=True)
                            if "traffic_jam" in alert["alert_type"]:
                                st.markdown(
                                    f"<span style='color: #EF4444; font-size: 13px; font-weight: 600;'>🚨 拥堵 | 置信度: {alert['confidence']:.2f}</span>",
                                    unsafe_allow_html=True,
                                )
                            else:
                                st.markdown(
                                    f"<span style='color: #F59E0B; font-size: 13px; font-weight: 600;'>⚠️ 行人 | 置信度: {alert['confidence']:.2f}</span>",
                                    unsafe_allow_html=True,
                                )
                        else:
                            st.warning("图片已损坏")

    # --- 历史报警记录查询区 ---
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📜 展开查看完整历史报警记录（数据表）", expanded=True):
        if len(alerts_list) > 0:
            df_history = pd.DataFrame(alerts_list)
            df_history = df_history[
                ["id", "alert_type", "confidence", "snapshot_path", "created_at"]
            ]
            df_history.columns = [
                "记录ID",
                "报警类型",
                "置信度",
                "截图路径",
                "发生时间",
            ]

            st.dataframe(
                df_history, use_container_width=True, hide_index=True, height=300
            )
            st.caption(
                f"💡 当前显示最近 {len(df_history)} 条记录（可在左侧侧边栏调整拉取条数）。总计历史报警：{total_alerts} 条。"
            )
        else:
            st.info("暂无历史报警记录。")

else:
    st.error("❌ 无法连接到后端服务，请确保 FastAPI (main.py) 正在运行！")
