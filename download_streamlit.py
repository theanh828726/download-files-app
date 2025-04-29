import streamlit as st
import pandas as pd
import requests
import os

st.title("📥 TẢI FILE TỰ ĐỘNG TỪ LINK TRONG EXCEL")

uploaded_file = st.file_uploader("📂 Chọn file Excel chứa đường dẫn", type=["xlsx"])

if uploaded_file:
    # Tạo thư mục lưu file
    image_folder = "Downloaded_Images"
    pdf_folder = "Downloaded_PDFs"
    os.makedirs(image_folder, exist_ok=True)
    os.makedirs(pdf_folder, exist_ok=True)

    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df.columns = df.columns.str.strip()

        # Xác định cột
        column_name = "Documentpath"
        name_column = "Customercode"

        if column_name not in df.columns or name_column not in df.columns:
            st.error(f"❌ Không tìm thấy cột '{column_name}' hoặc '{name_column}' trong file Excel.")
            st.stop()

        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, row in df.iterrows():
            file_url = row[column_name]
            file_name = str(row[name_column])

            if pd.notna(file_url):
                try:
                    response = requests.get(file_url, stream=True)
                    if response.status_code == 200:
                        file_extension = os.path.splitext(file_url)[1].lower()

                        if file_extension in [".jpg", ".png", ".jpeg"]:
                            save_path = os.path.join(image_folder, file_name + file_extension)
                        elif file_extension == ".pdf":
                            save_path = os.path.join(pdf_folder, file_name + file_extension)
                        else:
                            st.warning(f"⚠️ Bỏ qua file không xác định: {file_url}")
                            continue

                        with open(save_path, "wb") as file:
                            for chunk in response.iter_content(1024):
                                file.write(chunk)

                        status_text.success(f"✅ Đã tải: {file_url}")
                    else:
                        status_text.error(f"❌ Lỗi tải: {file_url}")
                except Exception as e:
                    status_text.error(f"⚠️ Lỗi khi tải {file_url}: {e}")

            progress_bar.progress((idx + 1) / len(df))

        st.success("🎉 Hoàn thành tải toàn bộ file!")
    except Exception as e:
        st.error(f"❌ Lỗi khi đọc hoặc xử lý file: {e}")
