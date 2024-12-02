import streamlit as st
from components.filters import show_filters
from components.visualizations import (
    create_colored_table,
    plot_feature_distribution_with_groups,
    show_pie_chart,
)
from components.data_preparation import prepare_data, predict_success, categorize_performance
from components.recommendations import show_improvement_suggestions
from models.model_loader import load_model_and_data
import plotly.graph_objects as go
# 페이지 설정
st.set_page_config(
    page_title="취업 성공 예측 모델",
    page_icon=":briefcase:",
    layout="wide",
)

st.title(":briefcase: 취업 성공 예측 모듈")
page_selection = st.sidebar.radio("페이지 선택", ["모델/데이터 불러오기", "취업 성취 스코어", "그룹별 특성 상세 보기", "개인별 상세 분석"])

# -------------------------------------------------------------------------
if page_selection == "모델/데이터 불러오기":
    load_model_and_data()

elif page_selection == "취업 성취 스코어":
    show_filters()

elif page_selection == "그룹별 특성 상세 보기":
    if "processed_data" in st.session_state:
        data = st.session_state["processed_data"].copy()

        # 분석 가능한 특성 정의
        available_features = ["성적수준", "교류수준", "역량수준", "일경험수준", "비교과수준"]

        # 거미줄 그래프 표시
       # st.subheader("그룹별 특성 분포")
        # 각 열의 비율을 %로 계산
        col1_width = 50  # 왼쪽 열이 70%
        col2_width = 50  # 오른쪽 열이 30%

        # 비율 합계를 100으로 맞추고, Streamlit의 정수 비율로 변환
        total_width = col1_width + col2_width
        col1_ratio = int(col1_width / total_width * 100)
        col2_ratio = int(col2_width / total_width * 100)
        # 열 생성
        col1, col2 = st.columns([col1_ratio, col2_ratio])
        with col1:

            plot_feature_distribution_with_groups(data, available_features)

        with col2:
            st.subheader("")
            st.subheader("")
            st.subheader("")
            st.subheader("")
            st.subheader("")
            st.write("항목 설명")
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
        <p> 🟤 비교과수준: 동아리수, 자격증수, 토익수준, 수상빈도<br> </p>
        <p> 🟡 일경험수준: 전공체험_소요시간, 근로장학_근무시간 일경험_근로시간<br></p>
        <p> 🟤 교류수준: 교수교류, 선후배교류, 친구교류<br></p>
        <p> 🟡 역량수준: 창의융합, 문제해결, 의사소통, 리더십, 학습지도, 전공기초, 전공전문성, 자기관리, 대인관계, 글로벌시민의식<br></p>
        <p> 🟤 성적수준: 대학백분위점수, 성적 수준  <br></p>
                
    </div>
""", unsafe_allow_html=True)

            

        st.markdown("---")  # 구분선 추가
        # 데이터 분포 시각화
        st.subheader("성취 그룹별 데이터 분포 비교")

        # 전공 매핑
        major_mapping = {
            1: "기계공학부", 2: "메카트로닉스공학부", 3: "전기전자통신공학부",
            4: "컴퓨터공학부", 5: "에너지신소재화학공학부", 6: "산업경영학부", 7: "디자인건축공학부"
        }

        # 성취 수준별로 그룹화된 데이터 확인
        if "성취 수준" in data.columns:
            selected_feature = st.selectbox(
                "분포를 확인할 특성:",
                [col for col in data.columns if col not in ["학번", "이름", "성취 수준", "취업 성공 가능 스코어 (%)"]]
            )

            if selected_feature in data.columns:
                try:
                    # 그룹별로 선택한 특성의 분포 계산
                    grouped_data = data.groupby("성취 수준")[selected_feature].value_counts(normalize=True).unstack(fill_value=0)
                    data['전공'] = data['전공'].map(major_mapping)

                    # Plotly 데이터 준비
                    fig = go.Figure()

                    # 색상 매핑
                    color_mapping = {
                        "고성취": "blue",
                        "중성취": "skyblue",
                        "저성취": "orange"
                    }

                    for group in grouped_data.index:
                        fig.add_trace(
                            go.Bar(
                                x=grouped_data.columns,
                                y=grouped_data.loc[group],
                                name=group,
                                marker=dict(color=color_mapping[group])
                            )
                        )

                    # 그래프 레이아웃 설정
                    fig.update_layout(
                        title="성취 수준별 데이터 분포 비교",
                        xaxis=dict(title=selected_feature),
                        yaxis=dict(title="비율"),
                        barmode="stack",  # 누적 막대 그래프 형태
                        legend=dict(title="성취 수준"),
                        template="plotly_white"
                    )

                    # Plotly 그래프 표시
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as e:
                    st.error(f"'{selected_feature}' 특성의 분포를 시각화하는 중 오류가 발생했습니다: {e}")
            else:
                st.warning("선택한 특성이 데이터에 존재하지 않습니다.")
        else:
            st.warning("데이터에 '성취 수준' 컬럼이 없습니다. 먼저 데이터를 처리하세요.")


        # 텍스트 설명 추가
        
    else:
        st.warning("먼저 '취업 성취 스코어' 페이지에서 데이터를 처리하세요.")

elif page_selection == "개인별 상세 분석":
    show_improvement_suggestions()
