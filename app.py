import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from streamlit_qr_scanner import streamlit_qr_scanner

st.set_page_config(page_title="Quét QR Vạn Ninh", layout="centered")

# --- KẾT NỐI GOOGLE SHEETS ---
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Không cần replace \n nữa vì ta dùng định dạng """ trong Secrets
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

SHEET_ID = "1me6PI665ZLycG2D4pCn0uVpVtCFTfcZaRR7m7KzqDXg"

st.title("📷 Quét QR Hợp Đồng")
st.write("Đưa mã QR vào khung camera bên dưới")

# --- CAMERA QUÉT QR ---
# Component này sẽ tự động trả về nội dung của QR khi tìm thấy
qr_code_content = streamlit_qr_scanner(key='qr_scanner')

if qr_code_content:
    st.audio("https://www.soundjay.com/buttons/beep-07.mp3") # Thêm tiếng beep cho vui tai
    st.success(f"Đã quét thành công mã QR!")
    
    # Tách lấy Contract ID từ Link
    contract_id = ""
    if "enContractId=" in qr_code_content:
        contract_id = qr_code_content.split("enContractId=")[-1]
    else:
        contract_id = qr_code_content
        
    st.code(f"ID bắt được: {contract_id}")

    # Nút bấm lưu
    if st.button("🚀 LƯU VÀO GOOGLE SHEETS"):
        try:
            client = get_gspread_client()
            sheet = client.open_by_key(SHEET_ID).sheet1
            
            # Lưu ID vào cột đầu tiên
            sheet.append_row([contract_id])
            
            st.balloons()
            st.success(f"Đã lưu ID {contract_id} vào Sheet!")
        except Exception as e:
            st.error(f"Lỗi: {e}")

# Nút để reset lại camera nếu muốn quét tiếp cái khác
if st.button("Quét mã khác"):
    st.rerun()