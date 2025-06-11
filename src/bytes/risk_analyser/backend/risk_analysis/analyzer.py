def analyze_quantitative_risk(kpis):
    risk_score = 0
    explanations = []

    if kpis.get("debt_to_equity") and kpis["debt_to_equity"] > 2.0:
        risk_score += 20
        explanations.append("High Debt to Equity Ratio")

    if kpis.get("liquidity_ratio") and kpis["liquidity_ratio"] < 1.0:
        risk_score += 20
        explanations.append("Low Liquidity Ratio")

    if kpis.get("sharpe_ratio") and kpis["sharpe_ratio"] < 1.0:
        risk_score += 20
        explanations.append("Low Sharpe Ratio")

    level = "Low"
    if risk_score >= 60:
        level = "High"
    elif risk_score >= 30:
        level = "Medium"

    return {"score": risk_score, "level": level, "explanations": explanations}
