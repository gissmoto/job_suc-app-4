import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# 개선 방안 추천 데이터 정의
improvement_suggestions = {
    "동아리수": "다양한 동아리 활동 참여를 유도. 학교 내 동아리 박람회에 참석하여 관심 분야를 탐색. 자신의 전공과 관련된 동아리에 적극적으로 가입.",
    "자격증수": "산업별로 필요한 자격증 리스트 작성 및 준비. 학내 또는 지역 사회에서 운영하는 자격증 취득 강좌 참여. 온라인 플랫폼(예: Coursera, Udemy)에서 자격증 과정 수강.",
    "토익수준": "주간 단위 목표 점수 설정 및 학습 스케줄 수립. 모의 토익 시험을 통해 실력 점검. 어휘, 문법, 듣기, 독해 영역별 약점 분석 후 집중 학습.",
    "수상빈도": "학교 및 지역 사회의 각종 대회(학업, 스포츠, 예술) 참여 기회 탐색. 대회 참여를 위해 필요한 역량(예: 발표 능력, 창의력) 강화. 팀 프로젝트 또는 단체 활동에서 리더 역할 수행.",
    "전공체험_소요시간": "전공 체험 프로그램(캠프, 워크숍 등)에 자주 참여. 교수님 또는 전문가와 상담하여 현장 경험 기회 탐색. 학과 연구실 참여 또는 전공 관련 실험에 자발적 참여.",
    "근로장학_근무시간": "학교 근로 장학 기회 적극 탐색 및 지원. 학교 내 부서에서 근무하며 행정 또는 지원 업무 경험. 시간 관리 능력을 통해 근무 시간 활용도를 높임.",
    "일경험_근로시간": "파트타임 직업 또는 인턴십 경험 확대. 전공과 연관된 일경험 기회를 우선적으로 탐색. 기업 연계 프로그램이나 산업체 견학에 참여.",
    "교수교류": "정기적으로 교수님과의 상담 시간을 요청. 연구 프로젝트 또는 학과 행사에서 교수와 협력. 교수님의 강의 시간 외 질의응답을 통해 학업적 도움 요청.",
    "선후배교류": "학과 동아리, 멘토링 프로그램 등을 통해 선후배와 교류. 선배의 진로 경험담 및 조언을 적극적으로 청취. 학과 행사나 친목 모임에서 네트워크 형성.",
    "친구교류": "그룹 스터디 참여를 통해 학업적 협력 강화. 다양한 배경의 친구들과의 대화와 활동으로 새로운 시각 확보. 교내 및 지역 커뮤니티 활동에 참여.",
    "창의융합": "창의력 관련 워크숍, 브레인스토밍 세션 참여. 다양한 전공의 학생들과 협력하여 새로운 아이디어 개발. 복합 문제를 해결하는 프로젝트 경험 확대.",
    "문제해결": "논리적 사고와 문제 해결 능력을 키우는 PBL 교과 수강, 사례 연구 참여. 케이스 스터디, 모의 토론 등의 활동으로 실전 경험 강화. 팀 프로젝트에서 해결책 제안을 통해 실무적 감각 습득.",
    "의사소통": "발표 능력 강화 프로그램(예: 스피치 강의, Toastmasters) 참여. 글쓰기 및 구두 표현의 균형을 맞추기 위한 학습. 친구, 동료와의 대화에서 적극적 경청과 표현 연습.",
    "리더십": "팀 프로젝트에서 리더 역할 맡아보기. 학내 행사 기획 및 운영 경험. 봉사 활동에서 그룹을 이끄는 역할 수행.",
    "학습지도": "학습 플래너 작성 및 자기 주도적 학습 습관 형성. 학습 자료를 정리하고 동료 학생들과 공유. 어려운 과목에서 튜터링 프로그램에 참여.",
    "전공기초": "전공의 기본 이론을 체계적으로 복습. 기초 강의나 온라인 코스를 통해 기본 개념 강화. 관련 문제 풀이를 통해 이해력 심화.",
    "전공전문성": "전공 심화 학습을 위해 고급 강의 수강. 논문 작성 및 발표를 통해 학문적 전문성 강화. 실무와 연계된 프로젝트나 인턴십 참여.",
    "자기관리": "시간 관리 앱이나 플래너를 활용해 스케줄 조정. 학업과 여가 시간을 균형 있게 조율. 스트레스 관리 프로그램(명상, 운동 등) 참여.",
    "대인관계": "동아리 활동, 워크숍 등을 통해 다양한 사람들과 교류. 공감 능력을 강화하기 위한 소셜 스킬 훈련. 갈등 상황에서 타협과 협력을 통해 관계 유지.",
    "글로벌시민의식": "외국어 학습 및 국제 교류 프로그램 참여. 다문화 환경에서의 봉사 활동 및 협력 경험. 세계적 문제(환경, 빈곤 등)에 관심을 갖고 토론에 참여.",
}

# 학생 개선 방안 표시 함수
def show_improvement_suggestions():
    if "processed_data" in st.session_state and "model" in st.session_state:
        data = st.session_state["processed_data"].copy()
        model = st.session_state.model
        st.subheader("개인별 상세 분석")
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
        <p>학생 데이터는 모듈 검증을 위해 임의로 작성되었습니다. </p>
    </div>
    """, unsafe_allow_html=True)

        # Feature 중요도 기반 결정적인 변수 추출
        if hasattr(model, "feature_importances_"):
            feature_importances = pd.Series(
                model.feature_importances_, index=model.feature_names_in_
            ).sort_values(ascending=False)

            # 상위 5개의 중요한 변수 선택
            #key_features = feature_importances.head(7).index.tolist()
            key_features = ["대학백분위점수", "학습성과수준", "일경험", "역량", "교류"]
            #key_features_def = ["성적수준", "교류수준", "역량수준", "일경험수준", "비교과수준"]
        else:
            st.warning("모델에 feature_importances_ 속성이 없습니다. 기본 변수를 사용합니다.")
            key_features = ["성적수준", "교류수준", "역량수준", "일경험수준", "비교과수준"]

        # 기본적으로 포함할 컬럼
        base_columns = ["학번", "학년", "전공", "재학학기", "성취 수준"]
        display_columns = base_columns + key_features

        # 학생 선택 옵션
        student_options = data["이름"].unique()
        selected_student = st.selectbox("학생을 선택하세요:", student_options)

        # 선택된 학생 데이터 필터링
        student_data = data[data["이름"] == selected_student]

        # 주요 열 정의
        target_columns = [
            "동아리수", "자격증수", "토익수준", "수상빈도", 
            "전공체험_소요시간", "근로장학_근무시간", "일경험_근로시간",
            "교수교류빈도", "선후배교류", "친구교류", 
            "창의융합", "문제해결", "의사소통", "리더십",
            "학습지도", "전공기초", "전공전문성", "자기관리", "대인관계", "글로벌시민의식"
        ]
        
        # 값이 1 이하인 항목의 인덱스 및 값 표시
        if not student_data.empty:
            st.markdown(f"### **{selected_student} 학생 상세 분석**")
            
            # 선택된 학생의 주요 데이터 추출
            student_key_data = student_data[display_columns].reset_index(drop=True)  # 인덱스 제거
            st.write("**결정적인 변수 및 학생 기본 정보:**")
            st.table(student_key_data)

            # Feature 중요도 시각화
            #st.subheader("결정적인 변수 중요도")
            #student_features = student_data[display_columns].iloc[0]

           # Feature 중요도 시각화 함수 호출
            #plot_student_feature_importance_with_points(student_features, feature_importances)
 # 전체 학생 대비 선택된 학생의 위치 시각화
            st.subheader(f"{selected_student} 학생의 스코어 위치")
            score_column = "취업 성공 가능 스코어 (%)"

            fig = go.Figure()

            # 히스토그램: 전체 학생 스코어 분포
            fig.add_trace(
                go.Histogram(
                    x=data[score_column],
                    name="전체 학생",
                    opacity=0.75,
                    marker=dict(color="lightblue"),
                    nbinsx=20,
                )
                
            )

            # 선택된 학생의 스코어 강조
            selected_score = student_data[score_column].iloc[0]
            fig.add_trace(
                go.Scatter(
                    x=[selected_score],
                    y=[0],  # 위치는 상대적으로 0으로 설정
                    mode="markers+text",
                    marker=dict(color="red", size=10, symbol="diamond"),
                    text=f"{selected_student} ({selected_score:.2f})",
                    textposition="top center",
                    name="선택된 학생",
                )
            )

            # 그래프 레이아웃 설정
            fig.update_layout(
                title=f"{score_column} 분포에서 {selected_student} 학생의 위치",
                xaxis=dict(title=score_column),
                yaxis=dict(title="학생 수"),
                bargap=0.2,
                showlegend=True,
                template="plotly_white",
            )

            st.plotly_chart(fig, use_container_width=True)

            st.write("위의 데이터는 선택된 학생의 예측 결과와 관련된 주요 변수와 기본 정보를 포함합니다.")
           # 값이 평균의 하위 퍼센트에 해당하는 항목 필터링
            st.subheader("평균 하위 퍼센트 기준 설정")
            percentage_threshold = st.slider("하위 퍼센트 기준을 선택하세요 (기본값: 30%)", min_value=1, max_value=50, value=30, step=1)

            low_thresholds = data[target_columns].mean() * (percentage_threshold / 100)  # 사용자 설정 기준
            below_threshold = student_data[target_columns].loc[:, (student_data[target_columns] <= low_thresholds).any()]

            if not below_threshold.empty:
                st.subheader(f"평균 하위 {percentage_threshold}%에 해당하는 항목")
                for col in below_threshold.columns:
                    low_values = below_threshold[below_threshold[col] <= low_thresholds[col]][col]
                    if not low_values.empty:
                        for idx, value in low_values.items():
                            st.markdown("---")
                            st.markdown(
    f"""
    <div style="background-color: #333333; padding: 15px; border-radius: 8px; border-left: 5px solid #ff4b4b; margin-bottom: 15px;">
        <p style="color: #FFD700; font-size: 16px; margin-bottom: 10px;">
            - 학생의 <b style="color: #00BFFF;">{col}</b> 수준은 상위 그룹 학생들에 비해 부족합니다. 이 부분에 대한 개선이 필요해 보입니다.
        </p>
        <b style="color: #ff4b4b;">개선 방안:</b>
        <ul style="color: #ffffff; font-size: 14px; line-height: 1.5; margin-left: 20px;">
            {improvement_suggestions[col]}
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)
                        if st.button("관련 대학프로그램 소개 전송", key=f"program_button_{col}"):
                           st.write(f"{col} 관련 대학 프로그램 정보를 학생에게 전송했습니다!")
            else:
                st.info(f"평균 하위 {percentage_threshold}%에 해당하는 항목이 없습니다.")

            # 추가 설명
            
        else:
            st.warning("선택된 학생에 대한 데이터가 없습니다.")
    else:
        st.warning("먼저 '취업 성취 스코어' 페이지에서 데이터를 처리하세요.")
