import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from streamlit_reader import pwa_install_button, qr_scanner # Thư viện quét QR ổn định

st.set_page_config(page_title="Quét QR Vạn Ninh", layout="centered")

# --- KẾT NỐI GOOGLE SHEETS ---
def get_gspread_client():
    # Lấy thông tin từ Secrets (Bạn nhớ dùng định dạng 3 dấu ngoặc kép """ như mình hướng dẫn nhé)
    creds_dict = dict(st.secrets["gcp_service_account"])
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

SHEET_ID = "1me6PI665ZLycG2D4pCn0uVpVtCFTfcZaRR7m7KzqDXg"

st.title("📷 Quét QR Hợp Đồng")
st.write("Đưa mã QR vào khung camera")

# --- CAMERA QUÉT QR ---
# Component này sẽ tự động hiện khung camera và trả về data ngay khi nhận diện được
qr_data = qr_scanner()

if qr_data:
    # Tự động tách ID từ link
    contract_id = ""
    if "enContractId=" in qr_data:
        contract_id = qr_data.split("enContractId=")[-1]
    else:
        contract_id = qr_data
    
    st.success(f"🎯 Đã bắt được ID: {contract_id}")

    # Nút bấm lưu
    if st.button("🚀 XÁC NHẬN LƯU VÀO SHEET"):
        try:
            client = get_gspread_client()
            sheet = client.open_by_key(SHEET_ID).sheet1
            
            # Lưu ID vào cột mới
            sheet.append_row([contract_id])
            
            st.balloons()
            st.success("Đã ghi vào Google Sheets thành công!")
        except Exception as e:
            st.error(f"Lỗi: {e}")

# Tiện ích: Nút cài đặt app vào màn hình chính điện thoại cho vợ
pwa_install_button()