import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Bắt ID Hợp Đồng", layout="centered")

# --- KẾT NỐI GOOGLE SHEETS ---
def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

# ID file Sheet của bạn
SHEET_ID = "1me6PI665ZLycG2D4pCn0uVpVtCFTfcZaRR7m7KzqDXg"

st.title("🔗 Trích xuất Contract ID")
st.write("Dán link quét từ Zalo vào đây để lấy mã ID")

# Ô nhập Link
input_link = st.text_input("Dán link QR của bạn:", placeholder="https://...enContractId=abc_123")

if input_link:
    contract_id = ""
    
    # Logic tách ID từ link
    if "enContractId=" in input_link:
        # Lấy phần chữ sau dấu "="
        contract_id = input_link.split("enContractId=")[-1]
    else:
        # Nếu người dùng dán nhầm ID luôn thì lấy luôn ID đó
        contract_id = input_link.strip()

    if contract_id:
        st.success(f"Đã tìm thấy ID: **{contract_id}**")
        
        # Nút xác nhận lưu
        if st.button("Lưu ID này vào Google Sheets"):
            try:
                client = get_gspread_client()
                sheet = client.open_by_key(SHEET_ID).sheet1
                
                # Lưu vào cột đầu tiên của hàng mới
                sheet.append_row([contract_id])
                
                st.balloons()
                st.info("Đã lưu mã ID vào file Google Sheets thành công!")
            except Exception as e:
                st.error(f"Lỗi: {e}")
    else:
        st.warning("Link không đúng định dạng, vui lòng kiểm tra lại.")