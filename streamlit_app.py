import streamlit as st
import pandas as pd
import joblib
from io import BytesIO

# 페이지 설정
st.set_page_config(
    page_title="취업 성공 예측 모델",
    page_icon=":briefcase:",
    layout="wide",
)

st.title(":briefcase: 취업 성공 예측 모듈")

# 페이지 선택
page_selection = st.sidebar.radio("페이지 선택", ["파일 업로드", "결과 보기"])

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
    elif score >= 50:
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

def plot_feature_distribution(filtered_data, feature):
    """
    선택한 특성의 분포를 히스토그램으로 시각화.
    """
    st.subheader(f"{feature} 분포")
    if feature in filtered_data.columns:
        st.bar_chart(filtered_data[feature].value_counts())
    else:
        st.warning(f"'{feature}'는 데이터에 포함되지 않았습니다.")

# -------------------------------------------------------------------------
# 페이지: 파일 업로드
if page_selection == "파일 업로드":
    st.subheader("파일 업로드")
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

# -------------------------------------------------------------------------
# 페이지: 결과 보기
if page_selection == "결과 보기":
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

            # 필터 옵션
            st.subheader("성취 수준 필터")
            performance_filter = st.selectbox(
                "성취 수준을 선택하세요:",
                ["전체", "고성취", "중성취", "저성취"]
            )

            # 필터링 적용
            filtered_data = filter_data(data, performance_filter)

            # 컬러 테이블 생성
            if not filtered_data.empty:
                colored_table = create_colored_table(filtered_data)
                st.subheader("필터링된 결과")
                st.table(colored_table)

                # 특성 분포 시각화
                st.subheader("특성 분포 시각화")
                selected_feature = st.selectbox(
                    "특성 선택:",
                    [col for col in data.columns if col not in ["학번", "이름", "성취 수준", "취업 성공 가능 스코어 (%)"]]
                )
                plot_feature_distribution(filtered_data, selected_feature)
            else:
                st.warning("선택된 성취 수준에 해당하는 데이터가 없습니다.")
        except Exception as e:
            st.error(f"결과를 처리하는 중 오류가 발생했습니다: {e}")
    else:
        st.warning("먼저 '파일 업로드' 페이지에서 모델과 데이터를 업로드하세요.")
