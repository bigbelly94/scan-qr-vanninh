import streamlit as st
import pdfplumber
import requests
import re
import gspread
from google.oauth2.service_account import Credentials
from camera_input_live import camera_input_live # Thư viện mới ổn định hơn

st.set_page_config(page_title="Quản lý Hợp đồng Vạn Ninh", layout="centered")

def get_gspread_client():
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds)

SHEET_ID = "1me6PI665ZLycG2D4pCn0uVpVtCFTfcZaRR7m7KzqDXg"

def extract_info_from_pdf(contract_id):
    url = f"https://vpdk-snnmt.khanhhoa.gov.vn/Home/ShowContract/{contract_id}"
    response = requests.get(url)
    with open("temp.pdf", "wb") as f:
        f.write(response.content)
    with pdfplumber.open("temp.pdf") as pdf:
        full_text = "\n".join([page.extract_text() for page in pdf.pages])
        data = {
            "Số HĐ": re.search(r"Số:\s*([\w/-]+)", full_text).group(1) if re.search(r"Số:\s*([\w/-]+)", full_text) else "",
            "Tên": re.search(r"(?:Ông|Bà):\s*([^\n,]+)", full_text).group(1).strip() if re.search(r"(?:Ông|Bà):\s*([^\n,]+)", full_text) else "",
            "SĐT": re.search(r"Số điện thoại:\s*(\d+)", full_text).group(1) if re.search(r"Số điện thoại:\s*(\d+)", full_text) else "",
            "Tờ": re.search(r"Tờ bản đồ số:\s*(\d+)", full_text).group(1) if re.search(r"Tờ bản đồ số:\s*(\d+)", full_text) else "",
            "Thửa": re.search(r"Thửa đất số:\s*(\d+)", full_text).group(1) if re.search(r"Thửa đất số:\s*(\d+)", full_text) else "",
            "Địa chỉ": re.search(r"Địa chỉ thửa đất:\s*([^\n]+)", full_text).group(1).strip() if re.search(r"Địa chỉ thửa đất:\s*([^\n]+)", full_text) else ""
        }
        return data

st.title("📲 Quét QR Hợp đồng - Vạn Ninh")

# Giao diện quét mã mới
st.write("### Hướng camera vào mã QR")
image = camera_input_live()

# Lưu ý: Với thư viện này, nếu muốn quét QR từ ảnh camera, 
# ta cần thêm một bước giải mã. Để đơn giản nhất cho bạn, 
# mình thêm ô nhập mã bằng tay dự phòng ở đây.
contract_url = st.text_input("Hoặc dán Link QR vào đây (nếu camera chưa nhận):")

final_id = ""
if contract_url and "enContractId=" in contract_url:
    final_id = contract_url.split("enContractId=")[-1]

if final_id:
    st.info(f"Đang xử lý hồ sơ: {final_id}")
    with st.spinner("Đang bóc tách dữ liệu..."):
        info = extract_info_from_pdf(final_id)
    st.table([info]) 
    if st.button("🚀 LƯU VÀO SHEET"):
        try:
            client = get_gspread_client()
            sheet = client.open_by_key(SHEET_ID).sheet1
            sheet.append_row(list(info.values()))
            st.balloons()
            st.success("Đã lưu thành công!")
        except Exception as e:
            st.error(f"Lỗi: {e}")