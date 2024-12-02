import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def create_colored_table(data):
    """
    데이터프레임에서 컬러 및 아이콘이 포함된 테이블 생성.
    """
    
    table = []
    for _, row in data.iterrows():
        # 성취 수준에 따른 아이콘과 색상 설정
        if row["성취 수준"] == "고성취":
            performance = "🟢 고성취"
        elif row["성취 수준"] == "중성취":
            performance = "🟡 중성취"
        else:
            performance = "🔴 저성취"

        # 테이블 행 데이터 추가
        table.append({
            "학번": row["학번"],
            "이름": row["이름"],
            "학년": row.get("학년", "N/A"),
            "재학학기": row.get("재학학기", "N/A"),
            "취업 성공 가능 스코어 (%)": round(row["취업 성공 가능 스코어 (%)"], 2),
            "성취 수준": performance,
        })

    return pd.DataFrame(table)


def show_pie_chart(data):
    """
    성취 수준별 학생 비율을 나타내는 파이 차트 생성.
    """
    if "성취 수준" in data.columns:
        performance_counts = data["성취 수준"].value_counts(normalize=True) * 100
        pie_chart = px.pie(
            names=performance_counts.index,
            values=performance_counts.values,
            title="성취 수준별 학생 비율",
            color=performance_counts.index,
            color_discrete_map={"고성취": "green", "중성취": "yellow", "저성취": "#E16868FF"}
        )
        pie_chart.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(pie_chart, use_container_width=True)
    else:
        st.warning("데이터에 '성취 수준' 컬럼이 없습니다. 성취 수준을 계산하세요.")


def plot_feature_distribution_with_groups(data, available_features):
    """
    성취 수준별 주요 지표의 거미줄 그래프를 생성.
    """
    st.subheader("주요 지표 중심 성취 수준별 분포")

    if "성취 수준" not in data.columns:
        st.warning("데이터에 '성취 수준' 컬럼이 없습니다. 먼저 데이터를 처리하세요.")
        return

    group_order = ["저성취", "중성취", "고성취"]
    fig = go.Figure()

    for group in group_order:
        if group in data["성취 수준"].unique():
            group_data = data[data["성취 수준"] == group][available_features].mean()
            values = list(group_data) + [group_data.iloc[0]]  # 시작점으로 돌아가기 위해 첫 값을 추가
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
        width=700,
        height=600,
    )


    if fig.data:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("그릴 데이터가 부족합니다. 조건을 변경하거나 데이터를 확인하세요.")
