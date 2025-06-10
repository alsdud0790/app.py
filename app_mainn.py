import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import fitz  # PyMuPDF

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 금칙어 리스트 정의
high_risk = [
    "총포", "도검류", "전기충격기", "도박", "카지노", "마약", "담배", "담배대용품",
    "혈액", "랜덤박스", "콘택트 렌즈", "성인 사이트", "성인 만화", "가상화폐", "NFT",
    "복권", "렌탈폰", "중고차", "청소년유해매체물", "청소년유해약물", "청소년 출입",
    "청소년고용금지업소", "대출", "외화환전", "주식정보", "암호화폐", "몰래카메라"
]
mid_risk = ["1일 10kg 감량", "100% 보장", "병원보다 낫다", "의사 추천", "지속적 효과", "부작용 없음", "즉시 효과", "무조건"]
low_risk = ["한정 수량", "무료 배송", "즉시 할인", "기간 한정", "인기 상품", "고객 만족", "베스트셀러"]

def classify_text(text):
    if any(word in text for word in high_risk):
        return "고위험"
    elif any(word in text for word in mid_risk):
        return "중위험"
    elif any(word in text for word in low_risk):
        return "저위험"
    else:
        return "안전"

def highlight_keywords(text):
    for word in high_risk:
        if word in text:
            text = text.replace(word, f"**:red[{word}]**")
    for word in mid_risk:
        if word in text:
            text = text.replace(word, f"**:orange[{word}]**")
    for word in low_risk:
        if word in text:
            text = text.replace(word, f"**:blue[{word}]**")
    return text

def count_keywords(text):
    return sum(text.count(word) for word in high_risk + mid_risk + low_risk)

def generate_pdf(text, result, keyword_count):
    doc = fitz.open()
    page = doc.new_page()
    content = f"광고 문구 위험도 분석 결과\n\n문구:\n{text}\n\n예측된 위험도: {result}\n금칙어 개수: {keyword_count}"
    page.insert_text((72, 72), content, fontsize=12)
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

# Streamlit UI
st.title("📢 광고 문구 위험도 분석기")
st.write("광고 문구에 포함된 금칙어를 기반으로 위험도를 분석합니다.")

user_input = st.text_area("🔍 광고 문구 입력", height=100)

if st.button("분석하기"):
    if user_input.strip() == "":
        st.warning("문구를 입력해 주세요.")
    else:
        result = classify_text(user_input)
        keyword_count = count_keywords(user_input)
        st.success(f"✅ 예측된 위험도: **{result}**")
        st.markdown(f"**🔢 금칙어 개수:** {keyword_count}")
        st.markdown("**🔎 금칙어 하이라이팅:**")
        st.markdown(highlight_keywords(user_input))

        # 사용자 피드백
        feedback = st.radio("이 예측이 정확했나요?", ("👍 맞아요", "👎 아니에요"), horizontal=True)
        st.write(f"피드백 감사합니다: {feedback}")

        # PDF 저장
        pdf_data = generate_pdf(user_input, result, keyword_count)
        st.download_button("📄 PDF로 저장", data=pdf_data, file_name="risk_analysis.pdf", mime="application/pdf")

# 업로드 기능 추가
st.markdown("---")
st.write("📄 여러 문구를 CSV로 업로드해 분석할 수도 있어요.")
uploaded_file = st.file_uploader("CSV 파일 업로드 (열 이름: 'text')", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if 'text' in df.columns:
        df["위험도"] = df["text"].apply(classify_text)
        df["금칙어 개수"] = df["text"].apply(count_keywords)
        st.write("🔎 분석 결과")
        st.dataframe(df)

        # 시각화
        st.markdown("### 📊 위험도 분포 시각화")
        fig, ax = plt.subplots()
        sns.countplot(data=df, x="위험도", order=["고위험", "중위험", "저위험", "안전"], palette="Set2", ax=ax)
        ax.set_title("문구 위험도 분포")
        st.pyplot(fig)

        # 다운로드
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 결과 다운로드 (CSV)", data=csv, file_name="risk_result.csv", mime="text/csv")
    else:
        st.error("⚠️ 'text' 열이 포함된 CSV 파일을 업로드해 주세요.")

