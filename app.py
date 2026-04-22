import streamlit as st
import pdfplumber
import requests
import re
import gspread
from google.oauth2.service_account import Credentials
from streamlit_qr_scanner import streamlit_qr_scanner

# 1. Cấu hình trang và Kết nối Google Sheets
st.set_page_config(page_title="Quản lý Hợp đồng Vạn Ninh", layout="centered")

def get_gspread_client():
    # Đọc thông tin bảo mật từ Secrets của Streamlit
    creds_dict = dict(st.secrets["gcp_service_account"])
    # Xử lý ký tự xuống dòng cho private_key
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

# ID file Sheet bạn đã gửi
SHEET_ID = "1me6PI665ZLycG2D4pCn0uVpVtCFTfcZaRR7m7KzqDXg"

def extract_info_from_pdf(contract_id):
    url = f"https://vpdk-snnmt.khanhhoa.gov.vn/Home/ShowContract/{contract_id}"
    response = requests.get(url)
    with open("temp.pdf", "wb") as f:
        f.write(response.content)
    
    with pdfplumber.open("temp.pdf") as pdf:
        full_text = "\n".join([page.extract_text() for page in pdf.pages])
        
        # Các quy tắc tìm kiếm dữ liệu (Regex)
        data = {
            "Số HĐ": re.search(r"Số:\s*([\w/-]+)", full_text).group(1) if re.search(r"Số:\s*([\w/-]+)", full_text) else "",
            "Tên": re.search(r"(?:Ông|Bà):\s*([^\n,]+)", full_text).group(1).strip() if re.search(r"(?:Ông|Bà):\s*([^\n,]+)", full_text) else "",
            "SĐT": re.search(r"Số điện thoại:\s*(\d+)", full_text).group(1) if re.search(r"Số điện thoại:\s*(\d+)", full_text) else "",
            "Tờ": re.search(r"Tờ bản đồ số:\s*(\d+)", full_text).group(1) if re.search(r"Tờ bản đồ số:\s*(\d+)", full_text) else "",
            "Thửa": re.search(r"Thửa đất số:\s*(\d+)", full_text).group(1) if re.search(r"Thửa đất số:\s*(\d+)", full_text) else "",
            "Địa chỉ": re.search(r"Địa chỉ thửa đất:\s*([^\n]+)", full_text).group(1).strip() if re.search(r"Địa chỉ thửa đất:\s*([^\n]+)", full_text) else ""
        }
        return data

# GIAO DIỆN CHÍNH
st.title("📲 Quét QR Hợp đồng - Vạn Ninh")
st.write("Dữ liệu sẽ được lưu vào Google Sheet của bạn.")

# Thành phần quét mã QR
qr_code = streamlit_qr_scanner()

if qr_code:
    if "enContractId=" in qr_code:
        contract_id = qr_code.split("enContractId=")[-1]
        st.info(f"Đã nhận diện hồ sơ: {contract_id}")
        
        with st.spinner("Đang bóc tách dữ liệu từ PDF..."):
            info = extract_info_from_pdf(contract_id)
            
        st.success("Trích xuất dữ liệu thành công!")
        st.write("### Kiểm tra thông tin:")
        st.table([info]) 
        
        if st.button("🚀 XÁC NHẬN VÀ LƯU VÀO SHEET"):
            try:
                client = get_gspread_client()
                sheet = client.open_by_key(SHEET_ID).sheet1
                # Chèn hàng mới vào dưới cùng
                sheet.append_row(list(info.values()))
                st.balloons()
                st.success("Đã thêm thành công một hàng vào Google Sheets!")
            except Exception as e:
                st.error(f"Lỗi khi lưu vào Sheet: {e}")