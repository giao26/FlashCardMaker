import streamlit as st
import PyPDF2
import google.generativeai as genai
import pandas as pd
import io

# 1. Cấu hình giao diện Web
st.set_page_config(page_title="AI Flashcard Maker", page_icon="📚")
st.title("📚 Công Cụ Tạo Flashcard Từ Bài Giảng")
st.write("Tải file PDF lên và AI sẽ tự động tạo bộ câu hỏi ôn tập cho bạn!")

# 2. Nhập API Key
api_key = st.text_input("Nhập Gemini API Key của bạn để bắt đầu:", type="password")

# 3. Nơi tải file lên
uploaded_file = st.file_uploader("Chọn file bài giảng (PDF)", type="pdf")

# 4. Xử lý khi người dùng nhấn nút
if st.button("Tự động tạo Flashcard") and uploaded_file and api_key:
    try:
        genai.configure(api_key=api_key)
        # Sử dụng mô hình mới nhất theo đúng tài khoản của bạn
        model = genai.GenerativeModel('gemini-2.5-flash') 

        with st.spinner('Đang trích xuất văn bản từ PDF...'):
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

        with st.spinner('AI đang phân tích và soạn câu hỏi... (Có thể mất vài chục giây)'):
            # CẬP NHẬT PROMPT: Đổi vách ngăn thành ký tự |
            prompt = f"""
            Bạn là một trợ giảng đại học xuất sắc. Dựa vào nội dung bài giảng dưới đây, 
            hãy tạo ra 10 cặp câu hỏi và câu trả lời ngắn gọn để sinh viên làm flashcard.
            
            Yêu cầu định dạng BẮT BUỘC:
            Trả về dữ liệu dạng bảng, sử dụng duy nhất ký tự `|` (dấu gạch đứng) để ngăn cách. 
            Dòng đầu tiên BẮT BUỘC là header: CauHoi|TraLoi
            Không in thêm bất kỳ dòng chữ giải thích nào khác. Không dùng Markdown.

            Nội dung bài giảng:
            {text[:20000]} 
            """

            response = model.generate_content(prompt)
            raw_data = response.text.strip()
            
            # Dọn dẹp các ký tự rác nếu AI lỡ tay thêm vào
            raw_data = raw_data.replace("```text", "").replace("```csv", "").replace("```", "").strip()

        st.success("Hoàn thành!")
        st.subheader("Bảng Flashcard của bạn:")
        
        # CẬP NHẬT PANDAS: Đọc bảng với vách ngăn là ký tự |
        df = pd.read_csv(io.StringIO(raw_data), sep='|')
        st.dataframe(df, use_container_width=True)

        # 5. Tính năng tải file
        csv_buffer = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Tải file CSV (Dùng cho Anki/Quizlet)",
            data=csv_buffer,
            file_name="flashcards.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"Có lỗi xảy ra: {e}")