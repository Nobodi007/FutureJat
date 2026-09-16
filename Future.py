"""
Basis Arbitrage Simulator: Spot vs Futures
- Cash & Carry (Contango / ขาขึ้น)
- Reverse Cash & Carry (Backwardation / ขาลง)
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ----------------------------------------------------
# 1. PAGE CONFIG & THEME
# ----------------------------------------------------
st.set_page_config(page_title="Spot-Futures Basis Arbitrage", layout="wide")

PRIMARY_COLOR = "#00E676"
ACCENT_RED = "#FF4D4D"
BG_COLOR = "#0d1117"
PANEL_COLOR = "#161b22"
TEXT_COLOR = "#f0f6fc"
MUTED = "#8b949e"

st.markdown(f"""
    <style>
    .stApp {{ background-color: {BG_COLOR}; color: {TEXT_COLOR}; font-family: 'Inter', sans-serif; }}
    div[data-testid="stMetric"] {{ background-color: {PANEL_COLOR}; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }}
    div[data-testid="stMetricValue"] {{ color: {PRIMARY_COLOR} !important; font-weight: bold; }}
    </style>
""", unsafe_allow_html=True)

st.title("⚖️ Spot vs Futures Basis Arbitrage")
st.markdown(f"<span style='color:{MUTED};'>ระบบจำลองการล็อกกำไรจากส่วนต่าง (Basis) แบบ Delta Neutral ไม่สนทิศทางตลาด</span>", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------------------------------
# 2. MARKET DATA INPUTS
# ----------------------------------------------------
st.sidebar.header("⚙️ กำหนดราคาตลาด (Market Data)")
spot_price = st.sidebar.number_input("ราคา Spot ปัจจุบัน (THB)", value=70000.0, step=100.0)
futures_price = st.sidebar.number_input("ราคา Futures ปัจจุบัน (THB)", value=71000.0, step=100.0)
trade_size = st.sidebar.number_input("ขนาดไม้เทรด (BTC)", value=1.0, step=0.1)

basis = futures_price - spot_price
locked_profit = abs(basis) * trade_size

# ----------------------------------------------------
# 3. STRATEGY ENGINE (ประเมินสภาวะตลาด)
# ----------------------------------------------------
st.subheader("1. วิเคราะห์สภาวะตลาด & กลยุทธ์ (Strategy Engine)")

col1, col2, col3 = st.columns(3)
col1.metric("ราคา Spot", f"{spot_price:,.2f} THB")
col2.metric("ราคา Futures", f"{futures_price:,.2f} THB")
col3.metric("ส่วนต่าง (Basis)", f"{basis:+,.2f} THB/BTC")

if basis > 0:
    market_condition = "📈 Contango (ตลาดมองขึ้น / Futures แพงกว่า)"
    strategy_name = "Cash & Carry Arbitrage"
    action_spot = f"🛒 ซื้อ (Long) Spot ที่ {spot_price:,.2f}"
    action_futures = f"📉 ขาย (Short) Futures ที่ {futures_price:,.2f}"
    explanation = "ตลาดมองขึ้น Futures เลยแพงกว่า เราจึงซื้อของถูก (Spot) และชอร์ตของแพง (Futures) เพื่อล็อกส่วนต่าง"
    color = PRIMARY_COLOR
elif basis < 0:
    market_condition = "📉 Backwardation (ตลาดมองลง / Spot แพงกว่า)"
    strategy_name = "Reverse Cash & Carry Arbitrage"
    action_spot = f"📉 ยืมขาย (Short) Spot ที่ {spot_price:,.2f}"
    action_futures = f"🛒 ซื้อ (Long) Futures ที่ {futures_price:,.2f}"
    explanation = "ตลาดมองลง Spot เลยแพงกว่า เราจึงยืมของมาเทขายแพง (Spot) และซื้อล่วงหน้าถูก (Futures) เพื่อล็อกส่วนต่าง"
    color = ACCENT_RED
else:
    market_condition = "⚖️ Flat (ราคาเท่ากัน)"
    strategy_name = "No Arbitrage Opportunity"
    action_spot = "รอดูสถานการณ์"
    action_futures = "รอดูสถานการณ์"
    explanation = "ไม่มีส่วนต่างให้ทำกำไร"
    color = MUTED

st.markdown(f"**สภาวะตลาด:** <span style='color:{color}; font-size:18px;'>{market_condition}</span>", unsafe_allow_html=True)
st.info(f"**Action ของบอท ({strategy_name}):**\n1. {action_spot}\n2. {action_futures}\n\n*เหตุผล: {explanation}*")

if basis != 0:
    st.success(f"🎯 **กำไรที่ถูกล็อกไว้แน่นอน (Locked Profit) = {locked_profit:,.2f} THB**")

st.markdown("---")

# ----------------------------------------------------
# 4. SCENARIO ANALYSIS (พิสูจน์ Delta Neutral)
# ----------------------------------------------------
if basis != 0:
    st.subheader("2. พิสูจน์ความอมตะ (Scenario Analysis ณ วันหมดอายุสัญญา)")
    st.markdown(f"<span style='color:{MUTED};'>ไม่ว่าราคา Settlement ตอนจบสัญญาจะไปทางไหน กำไรสุทธิของพอร์ตจะต้องเท่ากับกำไรที่ล็อกไว้เสมอ</span>", unsafe_allow_html=True)

    # จำลอง 3 สถานการณ์: ราคาดิ่งยับ, ราคาคงที่, ราคาพุ่งกาว
    settlement_prices = [spot_price - 15000, spot_price, spot_price + 15000]
    scenarios = []

    for settle in settlement_prices:
        if basis > 0: # Cash & Carry (Long Spot, Short Fut)
            spot_pnl = (settle - spot_price) * trade_size
            fut_pnl = (futures_price - settle) * trade_size
        else: # Reverse (Short Spot, Long Fut)
            spot_pnl = (spot_price - settle) * trade_size
            fut_pnl = (settle - futures_price) * trade_size
        
        net_pnl = spot_pnl + fut_pnl
        scenarios.append({
            "ราคาจบสัญญา (Settlement)": f"{settle:,.2f}",
            "กำไร/ขาดทุน ขา Spot": f"{spot_pnl:+,.2f}",
            "กำไร/ขาดทุน ขา Futures": f"{fut_pnl:+,.2f}",
            "กำไรสุทธิรวม (Net PnL)": f"{net_pnl:+,.2f} THB"
        })

    df_scenarios = pd.DataFrame(scenarios)
    st.table(df_scenarios)
    
    st.caption("💡 **สังเกตที่คอลัมน์ขวาสุด (Net PnL):** ขาดทุนจากฝั่งนึง จะถูกชดเชยด้วยกำไรจากอีกฝั่งเป๊ะๆ ทำให้กำไรสุทธิเท่าเดิมทุกราคา!")