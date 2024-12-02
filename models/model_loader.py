import streamlit as st
import pandas as pd
import joblib
from io import BytesIO


def load_model_and_data():
    st.markdown("""
    <style>
    .box-with-shadow {
        background-color: #C1C1C1FF; /* 박스 배경색 */
        padding: 15px; /* 박스 내부 여백 */
        border-radius: 10px; /* 박스 모서리 둥글게 */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); /* 그림자 효과 */
        margin-bottom: 15px; /* 박스 하단 간격 */
    }
    .box-with-shadow p {
        margin-bottom: 1px; /* 텍스트 줄 간격 */
        font-size: 16px; /* 글자 크기 조정 */
        font-weight: bold; /* 글자 굵기 */
        color: #333; /* 텍스트 색상 */
    }
    </style>
    <div class="box-with-shadow">
        <p>이 모듈(POC 1.0 버전)은 성공 예측 모델 기반으로 취업 가능성을 예측합니다.</p>
        <p>취업 성공 가능성이 낮은 학생들을 조기 발굴하고 이를 개선하기 위한 방안을 마련할 수 있습니다.</p>
        <p>학생 데이터는 모듈 검증을 위해 임의로 작성되었습니다. 추후 대학 DB와 실시간 연동이 필요합니다</p>
                
    </div>
    """, unsafe_allow_html=True)

    st.subheader("AI 모델 및 데이터 불러오기")
    uploaded_model = st.file_uploader("예측 모델 (.joblib 파일) 업로드", type="joblib")
    uploaded_data = st.file_uploader("테스트 데이터 (.csv 파일) 업로드", type="csv")
    if uploaded_model and uploaded_data:
        try:
            model = joblib.load(BytesIO(uploaded_model.read()))
            st.session_state.model = model
            data = pd.read_csv(uploaded_data, dtype={"학번": str})
            st.session_state.uploaded_data = data
            st.success("모델과 데이터가 성공적으로 업로드되었습니다.")
        except Exception as e:
            st.error(f"업로드 중 오류가 발생했습니다: {e}")
    st.write("*추후 아우누리 학생 DB 연동 필요*")

            
