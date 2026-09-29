import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# -----------------------------------------------------------------------------
# CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Room State Dashboard",
    page_icon="🏨",  # <-- Đã sửa thành page_icon
    layout="wide",
    initial_sidebar_state="expanded"
)
)

# Custom CSS cho giao diện hiện đại & các ô thẻ phòng
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .room-box {
        border-radius: 8px;
        padding: 15px;
        color: white;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .status-available { background-color: #2e7d32; }
    .status-occupied { background-color: #c62828; }
    .status-cleaning { background-color: #f57f17; }
    .status-maintenance { background-color: #616161; }
    .room-header { font-size: 1.2rem; font-weight: bold; margin-bottom: 5px; }
    .room-type { font-size: 0.85rem; opacity: 0.9; }
    .room-detail { font-size: 0.8rem; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.3); padding-top: 5px; }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# MOCK DATA & STATE MANAGEMENT
# -----------------------------------------------------------------------------
STATUS_MAP = {
    "Trống": {"color": "#2e7d32", "class": "status-available", "icon": "🟢"},
    "Đang ở": {"color": "#c62828", "class": "status-occupied", "icon": "🔴"},
    "Đang dọn": {"color": "#f57f17", "class": "status-cleaning", "icon": "🟡"},
    "Bảo trì": {"color": "#616161", "class": "status-maintenance", "icon": "⚪"}
}

def init_session_state():
    if 'rooms_data' not in st.session_state:
        # Khởi tạo dữ liệu mẫu cho 12 phòng
        st.session_state.rooms_data = pd.DataFrame([
            {"room_id": "101", "floor": "Tầng 1", "type": "Single", "status": "Trống", "guest": "", "price": 500000},
            {"room_id": "102", "floor": "Tầng 1", "type": "Single", "status": "Đang ở", "guest": "Nguyễn Văn A", "price": 500000},
            {"room_id": "103", "floor": "Tầng 1", "type": "Double", "status": "Đang dọn", "guest": "", "price": 800000},
            {"room_id": "104", "floor": "Tầng 1", "type": "Deluxe", "status": "Bảo trì", "guest": "", "price": 1200000},
            {"room_id": "201", "floor": "Tầng 2", "type": "Single", "status": "Đang ở", "guest": "Trần Thị B", "price": 500000},
            {"room_id": "202", "floor": "Tầng 2", "type": "Double", "status": "Trống", "guest": "", "price": 800000},
            {"room_id": "203", "floor": "Tầng 2", "type": "Double", "status": "Đang ở", "guest": "Lê Văn C", "price": 800000},
            {"room_id": "204", "floor": "Tầng 2", "type": "Deluxe", "status": "Trống", "guest": "", "price": 1200000},
            {"room_id": "301", "floor": "Tầng 3", "type": "VIP Suite", "status": "Đang ở", "guest": "Phạm Minh D", "price": 2000000},
            {"room_id": "302", "floor": "Tầng 3", "type": "VIP Suite", "status": "Đang dọn", "guest": "", "price": 2000000},
            {"room_id": "303", "floor": "Tầng 3", "type": "Deluxe", "status": "Trống", "guest": "", "price": 1200000},
            {"room_id": "304", "floor": "Tầng 3", "type": "Single", "status": "Trống", "guest": "", "price": 500000},
        ])

init_session_state()

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
st.sidebar.title("🏨 Quản Lý Phòng")
st.sidebar.caption("Hệ thống theo dõi real-time")

# Bộ lọc
st.sidebar.subheader("🔍 Bộ Lọc Quick-View")
selected_floor = st.sidebar.multiselect("Chọn Tầng", options=st.session_state.rooms_data["floor"].unique(), default=st.session_state.rooms_data["floor"].unique())
selected_status = st.sidebar.multiselect("Chọn Trạng Thái", options=list(STATUS_MAP.keys()), default=list(STATUS_MAP.keys()))

# Form Cập Nhật Trạng Thái
st.sidebar.divider()
st.sidebar.subheader("⚡ Cập Nhật Nhanh")
with st.sidebar.form("update_room_form"):
    target_room = st.selectbox("Chọn Phòng", options=st.session_state.rooms_data["room_id"].tolist())
    new_status = st.selectbox("Trạng Thái Mới", options=list(STATUS_MAP.keys()))
    new_guest = st.text_input("Tên Khách Hàng (Nếu có)")
    submit_btn = st.form_submit_button("Cập Nhật", use_container_width=True)

if submit_btn:
    idx = st.session_state.rooms_data[st.session_state.rooms_data["room_id"] == target_room].index[0]
    st.session_state.rooms_data.at[idx, "status"] = new_status
    st.session_state.rooms_data.at[idx, "guest"] = new_guest if new_status == "Đang ở" else ""
    st.toast(f"✅ Đã cập nhật Phòng {target_room} sang '{new_status}'!", icon="🎉")
    st.rerun()

# -----------------------------------------------------------------------------
# MAIN DASHBOARD CONTENT
# -----------------------------------------------------------------------------
st.title("📌 Sơ Đồ & Tình Trạng Phòng Real-time")

# 1. Thống kê nhanh (Metrics)
df_data = st.session_state.rooms_data
total_rooms = len(df_data)
occupied_count = len(df_data[df_data["status"] == "Đang ở"])
available_count = len(df_data[df_data["status"] == "Trống"])
cleaning_count = len(df_data[df_data["status"] == "Đang dọn"])
occupancy_rate = round((occupied_count / total_rooms) * 100, 1)

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
col_m1.metric("Tổng Số Phòng", total_rooms)
col_m2.metric("Phòng Trống", available_count)
col_m3.metric("Đang Có Khách", occupied_count)
col_m4.metric("Đang Dọn/Bảo Trì", cleaning_count + len(df_data[df_data["status"] == "Bảo trì"]))
col_m5.metric("Tỷ Lệ Lấp Đầy", f"{occupancy_rate}%")

st.divider()

# 2. Hiển thị Grid sơ đồ phòng
filtered_df = df_data[
    (df_data["floor"].isin(selected_floor)) & 
    (df_data["status"].isin(selected_status))
]

floors = filtered_df["floor"].unique()

if len(filtered_df) == 0:
    st.info("Không có phòng nào phù hợp với bộ lọc hiện tại.")
else:
    for floor in sorted(floors):
        st.subheader(f"🏢 {floor}")
        floor_rooms = filtered_df[filtered_df["floor"] == floor]
        cols = st.columns(4) # Mỗi hàng tối đa 4 phòng
        
        for index, room in floor_rooms.reset_index().iterrows():
            col_idx = index % 4
            status_info = STATUS_MAP[room["status"]]
            
            with cols[col_idx]:
                guest_info = f"👤 {room['guest']}" if room['guest'] else "—"
                price_info = f"{room['price']:,} VNĐ"
                
                # HTML Render Thẻ Phòng
                st.markdown(f"""
                <div class="room-box {status_info['class']}">
                    <div class="room-header">P.{room['room_id']} - {status_info['icon']} {room['status']}</div>
                    <div class="room-type">Loại: {room['type']} | {price_info}</div>
                    <div class="room-detail">
                        Khách: {guest_info}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# 3. Analytics & Thống kê đồ họa
st.divider()
st.subheader("📊 Biểu Đồ Thống Kê")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # Biểu đồ tròn về tỷ lệ trạng thái
    status_counts = df_data["status"].value_counts().reset_index()
    status_counts.columns = ["Trạng Thái", "Số Lượng"]
    
    fig_pie = px.pie(
        status_counts, 
        names="Trạng Thái", 
        values="Số Lượng",
        title="Tỷ lệ trạng thái phòng hiện tại",
        color="Trạng Thái",
        color_discrete_map={k: v["color"] for k, v in STATUS_MAP.items()},
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    # Biểu đồ cột về tình trạng từng tầng
    floor_status = df_data.groupby(["floor", "status"]).size().reset_index(name="Số Lượng")
    fig_bar = px.bar(
        floor_status,
        x="floor",
        y="Số Lượng",
        color="status",
        title="Phân bổ trạng thái phòng theo tầng",
        barmode="stack",
        color_discrete_map={k: v["color"] for k, v in STATUS_MAP.items()}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
