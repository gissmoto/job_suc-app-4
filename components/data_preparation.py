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