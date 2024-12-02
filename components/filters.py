import pandas as pd
import streamlit as st
from components.visualizations import create_colored_table, show_pie_chart
from components.data_preparation import prepare_data, predict_success, categorize_performance
import plotly.express as px


def show_filters():
    if "model" in st.session_state and "uploaded_data" in st.session_state:
        model = st.session_state.model
        data = st.session_state.uploaded_data.copy()

        try:
            prepared_data = prepare_data(data.copy(), model)
            probabilities = predict_success(model, prepared_data)
            major_mapping = {
                1: "기계공학부", 2: "메카트로닉스공학부", 3: "전기전자통신공학부",
                4: "컴퓨터공학부", 5: "에너지신소재화학공학부", 6: "산업경영학부", 7: "디자인건축공학부"
            }
            data['전공'] = data['전공'].map(major_mapping)

            if probabilities is not None:
                data["취업 성공 가능 스코어 (%)"] = probabilities[:, 1]
                data["성취 수준"] = data["취업 성공 가능 스코어 (%)"].apply(categorize_performance)

            st.session_state["processed_data"] = data
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
        <p>예측 모델 기반으로 취업 성공 가능 스코어를 예측합니다.</p>
                        <p>학생 데이터는 모듈 검증을 위해 임의로 작성되었습니다. 추후 대학 DB와 실시간 연동이 필요합니다</p>
    </div>
    """, unsafe_allow_html=True)
            st.subheader("필터 옵션")
            col1, col2, col3 = st.columns(3)

            performance_filter = col1.selectbox(
                "성취 수준:",
                ["전체", "고성취", "중성취", "저성취"]
            )

            grade_filter = col2.selectbox(
                "학년:",
                ["전체"] + sorted(data["학년"].dropna().unique())
            )

            major_filter = col3.selectbox(
                "전공:",
                ["전체"] + sorted(data["전공"].dropna().unique())
            )

            col4, col5 = st.columns(2)

            sort_by = col4.selectbox(
                "정렬 기준:",
                ["학번", "이름", "학년", "취업 성공 가능 스코어 (%)"]
            )
            sort_order = col5.radio(
                "정렬 순서:",
                ["오름차순", "내림차순"]
            )

            def apply_filters(data, performance_filter, grade_filter, major_filter):
                filtered_data = data.copy()
                if performance_filter != "전체":
                    filtered_data = filtered_data[filtered_data["성취 수준"] == performance_filter]
                if grade_filter != "전체":
                    filtered_data = filtered_data[filtered_data["학년"] == grade_filter]
                if major_filter != "전체":
                    filtered_data = filtered_data[filtered_data["전공"] == major_filter]
                return filtered_data

            filtered_data = apply_filters(data, performance_filter, grade_filter, major_filter)
            ascending = True if sort_order == "오름차순" else False
            filtered_data = filtered_data.sort_values(by=sort_by, ascending=ascending)

            if not filtered_data.empty:
                colored_table = create_colored_table(filtered_data)
                st.subheader("필터링 및 정렬된 결과")
                st.table(colored_table)
            else:
                st.warning("선택된 조건에 해당하는 데이터가 없습니다.")

                        # 성취 수준별 비율, 학년별 비율, 전공별 비율을 가로 레이아웃으로 표시
            st.markdown("---")
            st.subheader("성취 수준, 학년별, 전공별 비율")

            # 세 개의 그래프를 가로로 배치
            col1, col2, col3 = st.columns(3)

            # 성취 수준별 비율
            with col1:
                st.markdown("#### 성취 수준별 비율")
                if "성취 수준" in data.columns:
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
                else:
                    st.warning("데이터에 '성취 수준' 컬럼이 없습니다. 성취 수준을 계산하세요.")

            # 학년별 성취 비율
            with col2:
                st.markdown("#### 학년별 성취 비율")
                grade_performance_counts = data.groupby(["학년", "성취 수준"]).size().reset_index(name="count")
                grade_chart = px.bar(
                    grade_performance_counts,
                    y="학년",  # Y축에 학년을 설정
                    x="count",  # X축에 비율 값을 설정
                    color="성취 수준",
                    orientation="h",  # 가로 막대 그래프
                    title="학년별 성취 수준 분포 (그룹)",
                    color_discrete_map={"고성취": "green", "중성취": "yellow", "저성취": "red"}
                )
                grade_chart.update_layout(barmode="group")  # 누적 그래프로 설정
                st.plotly_chart(grade_chart, use_container_width=True)


            # 전공별 성취 비율
            with col3:
                st.markdown("#### 전공별 성취 비율")
                major_performance_counts = data.groupby(["전공", "성취 수준"]).size().reset_index(name="count")
                major_chart = px.bar(
                    major_performance_counts,
                    x="전공",
                    y="count",
                    color="성취 수준",
                    title="전공별 성취 수준 분포",
                    color_discrete_map={"고성취": "green", "중성취": "yellow", "저성취": "red"}
                )
                st.plotly_chart(major_chart, use_container_width=True)

            st.markdown("---")
            st.markdown("#### 전공과 학년에 따른 성취 수준 (히트맵)")
            # 데이터 준비
            heatmap_data = data.groupby(["전공", "학년"])["취업 성공 가능 스코어 (%)"].mean().reset_index()

            # 히트맵 생성
            heatmap = px.density_heatmap(
              heatmap_data,
              x="전공",
              y="학년",
              z="취업 성공 가능 스코어 (%)",
              color_continuous_scale="Greens",
             labels={"전공": "전공", "학년": "학년", "취업 성공 가능 스코어 (%)": "평균 스코어"},
             title="전공과 학년에 따른 성취 수준 (히트맵)",
            )
            heatmap.update_layout(
               xaxis={"categoryorder": "category ascending"},  # 전공 정렬
              yaxis={"categoryorder": "category ascending"},  # 학년 정렬
            )
            st.plotly_chart(heatmap, use_container_width=True)

        except Exception as e:
            st.error(f"결과를 처리하는 중 오류가 발생했습니다: {e}")
    else:
        st.warning("먼저 '모델/데이터 불러오기' 페이지에서 데이터를 업로드하세요.")
