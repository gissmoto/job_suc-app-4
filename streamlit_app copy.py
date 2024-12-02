import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.express as px
from io import BytesIO

# 페이지 설정
st.set_page_config(
    page_title="취업 성공 예측 모델",
    page_icon=":briefcase:",
    layout="wide",
)

st.title(":briefcase: 취업 성공 예측 모듈")

# 페이지 선택
page_selection = st.sidebar.radio("페이지 선택", ["모델/데이터 불러오기", "취업 성취 스코어", "그룹별 특성 상세 보기", "개인별 상세 분석"])

# -------------------------------------------------------------------------
# 함수 정의

def prepare_data(data, model):
    if hasattr(model, "feature_names_in_"):
        required_features = list(model.feature_names_in_)
        missing_columns = [col for col in required_features if col not in data.columns]
        for col in missing_columns:
            data[col] = 0
        data = data[required_features]
    return data

def predict_success(model, data):
    probabilities = model.predict_proba(data) * 100 if hasattr(model, "predict_proba") else None
    return probabilities

def categorize_performance(score):
    if score >= 70:
        return "고성취"
    elif score >= 10:
        return "중성취"
    else:
        return "저성취"

def filter_data(data, performance_filter):
    if performance_filter == "전체":
        return data
    else:
        return data[data["성취 수준"] == performance_filter]

def create_colored_table(filtered_data):
    table = []
    for _, row in filtered_data.iterrows():
        if row["성취 수준"] == "고성취":
            performance = "🟢 고성취"
        elif row["성취 수준"] == "중성취":
            performance = "🟡 중성취"
        else:
            performance = "🔴 저성취"
        table.append({
            "학번": row["학번"],
            "이름": row["이름"],
            "학년": row.get("학년", "N/A"),
            "재학학기": row.get("재학학기", "N/A"),
            "취업 성공 가능 스코어 (%)": round(row["취업 성공 가능 스코어 (%)"], 2),
            "성취 수준": performance,
        })
    return pd.DataFrame(table)

def plot_feature_distribution_with_groups(data, available_features):
    """
    전체 그룹 선택 시 저성취, 중성취, 고성취 그룹을 구분하여 거미줄 그래프로 시각화.
    """
    st.subheader("주요 지표 중심 성취 수준별 분포 (거미줄 그래프)")

    group_order = ["저성취", "중성취", "고성취"]
    fig = go.Figure()

    for group in group_order:
        if group in data["성취 수준"].unique():
            group_data = data[data["성취 수준"] == group][available_features].mean()
            values = list(group_data) + [group_data[0]]  # 시작점으로 돌아가기 위해 첫 값을 추가
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=available_features + [available_features[0]],
                fill='toself',
                name=f"{group} 그룹"
            ))

    # 그래프 레이아웃 설정
    fig.update_layout(
        template="plotly_dark",  # Plotly Dark 테마 적용
        polar=dict(
            bgcolor="rgba(0,0,0,0)",  # 배경 투명 설정
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2],  # 축 범위 자동 조정
                tickfont=dict(size=12, color="white"),  # 축의 숫자 폰트 설정
                gridcolor="white",  # 그리드 색상
                linecolor="white",  # 축 선 색상
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color="white"),  # 각 축의 레이블 설정
                gridcolor="gray",
                linecolor="white",
            ),
        ),
        showlegend=True,
        legend=dict(
            font=dict(size=12, color="white"),  # 범례 폰트 설정
            bgcolor="rgba(0,0,0,0.5)",  # 범례 배경색 반투명
        ),
        width=800,
        height=600,
    )


    # Streamlit에 그래프 표시
     # Streamlit에 그래프 표시
    st.plotly_chart(fig, use_container_width=True)


# -------------------------------------------------------------------------
# 페이지: 파일 업로드
if page_selection == "모델/데이터 불러오기":
    st.write("취업지원센터")
    st.subheader("모델/데이터 불러오기")
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
# -------------------------------------------------------------------------
import plotly.express as px

# 페이지: 취업 성취 스코어
if page_selection == "취업 성취 스코어":
    if "model" in st.session_state and "uploaded_data" in st.session_state:
        model = st.session_state.model
        data = st.session_state.uploaded_data.copy()

        try:
            # 데이터 준비
            prepared_data = prepare_data(data.copy(), model)

            # 예측 수행
            probabilities = predict_success(model, prepared_data)
            if probabilities is not None:
                data["취업 성공 가능 스코어 (%)"] = probabilities[:, 1]
                data["성취 수준"] = data["취업 성공 가능 스코어 (%)"].apply(categorize_performance)

            # 처리된 데이터를 세션 상태에 저장
            st.session_state["processed_data"] = data

            # 전공 이름 매핑
            major_mapping = {
                1: "기계공학부", 2: "메카트로닉스공학부", 3: "전기전자통신공학부",
                4: "컴퓨터공학부", 5: "에너지신소재화학공학부", 6: "산업경영학부", 7: "디자인건축공학부"
            }
            data['전공'] = data['전공'].map(major_mapping)

            # 멀티 필터 옵션
            st.subheader("필터 옵션")
            col1, col2, col3 = st.columns(3)

            # 성취 수준 필터
            performance_filter = col1.selectbox(
                "성취 수준:",
                ["전체", "고성취", "중성취", "저성취"]
            )

            # 학년 필터
            grade_filter = col2.selectbox(
                "학년:",
                ["전체"] + sorted(data["학년"].dropna().unique())
            )

            # 전공 필터
            major_filter = col3.selectbox(
                "전공:",
                ["전체"] + sorted(data["전공"].dropna().unique())
            )

            # 정렬 옵션
            st.subheader("정렬 옵션")
            col4, col5 = st.columns(2)

            sort_by = col4.selectbox(
                "정렬 기준:",
                ["학번", "이름", "학년", "취업 성공 가능 스코어 (%)"]
            )
            sort_order = col5.radio(
                "정렬 순서:",
                ["오름차순", "내림차순"]
            )

            # 필터링 적용 함수
            def apply_filters(data, performance_filter, grade_filter, major_filter):
                filtered_data = data.copy()

                # 성취 수준 필터
                if performance_filter != "전체":
                    filtered_data = filtered_data[filtered_data["성취 수준"] == performance_filter]

                # 학년 필터
                if grade_filter != "전체":
                    filtered_data = filtered_data[filtered_data["학년"] == grade_filter]

                # 전공 필터
                if major_filter != "전체":
                    filtered_data = filtered_data[filtered_data["전공"] == major_filter]

                return filtered_data

            # 필터링 적용
            filtered_data = apply_filters(data, performance_filter, grade_filter, major_filter)

            # 정렬 적용
            if not filtered_data.empty:
                ascending = True if sort_order == "오름차순" else False
                filtered_data = filtered_data.sort_values(by=sort_by, ascending=ascending)

                # 컬러 테이블 생성
                colored_table = create_colored_table(filtered_data)
                st.subheader("필터링 및 정렬된 결과")
                st.table(colored_table)

            else:
                st.warning("선택된 조건에 해당하는 데이터가 없습니다.")

            # 성취 수준별 비율 파이 차트 (하단에 표시)
            st.markdown("---")  # 구분선 추가
            st.subheader("성취 수준별 비율")
            performance_counts = data["성취 수준"].value_counts(normalize=True) * 100
            pie_chart = px.pie(
                names=performance_counts.index,
                values=performance_counts.values,
                title="성취 수준별 학생 비율",
                color=performance_counts.index,
                color_discrete_map={"고성취": "green", "중성취": "yellow", "저성취": "red"}
            )
            pie_chart.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(pie_chart, use_container_width=True)

        except Exception as e:
            st.error(f"결과를 처리하는 중 오류가 발생했습니다: {e}")
    else:
        st.warning("먼저 '파일 업로드' 페이지에서 모델과 데이터를 업로드하세요.")

    st.write("*필터링 및 정렬 기능이 포함된 성취 수준 스코어 화면*")


# -------------------------------------------------------------------------
# 페이지: 그룹별 특성 상세 보기
if page_selection == "그룹별 특성 상세 보기":
    if "processed_data" in st.session_state:
        data = st.session_state["processed_data"].copy()

        # 분석 가능한 특성 정의
        available_features = ["성적수준", "교류수준", "역량수준", "일경험수준", "비교과수준"]

        # 거미줄 그래프 표시
        st.subheader("그룹별 특성 분포")
        plot_feature_distribution_with_groups(data, available_features)

        import plotly.graph_objects as go
        st.subheader("항목 설명")
        st.markdown(
            """
            - **비교과수준** = (동아리수 + 자격증수 + 토익수준 + 수상빈도) / 재학학기  
            - **일경험수준** = (전공체험_소요시간 + 근로장학_근무시간 + 일경험_근로시간) / 재학학기  
            - **교류수준** = (교수교류 + 선후배교류 + 친구교류) / 재학학기  
            - **역량수준** = (창의융합 + 문제해결 + 의사소통 + 리더십 + 학습지도 + 전공기초 + 전공전문성 + 자기관리 + 대인관계 + 글로벌시민의식) / 10  
            - **성적수준** = 대학백분위점수, 성적 수준 (5점 계산) * 3 / 5  
            """
        )
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


# -------------------------------------------------------------------------
# 페이지: 개인별 상세 분석
if page_selection == "개인별 상세 분석":
    if "processed_data" in st.session_state and "model" in st.session_state:
        data = st.session_state["processed_data"].copy()
        model = st.session_state.model
        st.subheader("개인별 상세 분석")

        # Feature 중요도 기반 결정적인 변수 추출
        if hasattr(model, "feature_importances_"):
            feature_importances = pd.Series(
                model.feature_importances_, index=model.feature_names_in_
            ).sort_values(ascending=False)

            # 상위 5개의 중요한 변수 선택
            key_features = feature_importances.head(5).index.tolist()
            key_features_def = ["성적수준", "교류수준", "역량수준", "일경험수준", "비교과수준"]
        else:
            st.warning("모델에 feature_importances_ 속성이 없습니다. 기본 변수를 사용합니다.")
            key_features_def = ["성적수준", "교류수준", "역량수준", "일경험수준", "비교과수준"]

        # 기본적으로 포함할 컬럼
        base_columns = ["학번", "학년", "전공", "재학학기", "성취 수준"]
        display_columns = base_columns + key_features_def

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
        improvement_suggestions = {
            "동아리수": "다양한 동아리 활동 참여를 유도. 학교 내 동아리 박람회에 참석하여 관심 분야를 탐색. 자신의 전공과 관련된 동아리에 적극적으로 가입.",
            "자격증수": "산업별로 필요한 자격증 리스트 작성 및 준비. 학내 또는 지역 사회에서 운영하는 자격증 취득 강좌 참여. 온라인 플랫폼(예: Coursera, Udemy)에서 자격증 과정 수강.",
            "토익수준": "주간 단위 목표 점수 설정 및 학습 스케줄 수립. 모의 토익 시험을 통해 실력 점검. 어휘, 문법, 듣기, 독해 영역별 약점 분석 후 집중 학습.",
            "수상빈도": "학교 및 지역 사회의 각종 대회(학업, 스포츠, 예술) 참여 기회 탐색. 대회 참여를 위해 필요한 역량(예: 발표 능력, 창의력) 강화. 팀 프로젝트 또는 단체 활동에서 리더 역할 수행.<추가 정보 습득>",
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
