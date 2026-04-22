import streamlit as st
import cv2
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
from camera_input_live import camera_input_live

st.set_page_config(page_title="Quét QR Vạn Ninh", layout="centered")

# --- KẾT NỐI GOOGLE SHEETS ---
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

SHEET_ID = "1me6PI665ZLycG2D4pCn0uVpVtCFTfcZaRR7m7KzqDXg"

st.title("📷 Quét QR Hợp Đồng")

# --- CAMERA QUÉT QR ---
st.write("Hãy đưa mã QR vào khung bên dưới:")
image = camera_input_live()

qr_id = ""

if image is not None:
    # Chuyển đổi ảnh từ camera sang định dạng OpenCV
    bytes_data = image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # Bộ giải mã QR của OpenCV
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(cv2_img)
    
    if data:
        st.success("🎯 Đã nhận diện mã!")
        if "enContractId=" in data:
            qr_id = data.split("enContractId=")[-1]
        else:
            qr_id = data

# Ô nhập liệu dự phòng
st.write("---")
manual_input = st.text_input("Hoặc dán Link/ID vào đây:", value=qr_id)
final_id = manual_input if manual_input else qr_id

if final_id:
    st.info(f"ID hiện tại: **{final_id}**")
    if st.button("🚀 XÁC NHẬN LƯU VÀO SHEET"):
        try:
            client = get_gspread_client()
            sheet = client.open_by_key(SHEET_ID).sheet1
            sheet.append_row([final_id])
            st.balloons()
            st.success(f"Đã lưu thành công mã {final_id}")
        except Exception as e:
            st.error(f"Lỗi: {e}")