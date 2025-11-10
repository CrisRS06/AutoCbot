"""
Streamlit Monitoring Dashboard for Freqtrade
Run: streamlit run scripts/monitor.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

st.set_page_config(page_title="Freqtrade Monitor", layout="wide")

# ========== CONFIGURATION ==========
DB_PATH = Path(__file__).parent.parent / "user_data" / "tradesv3.sqlite"

# ========== LOAD DATA ==========
@st.cache_data(ttl=60)
def load_trades():
    """Load trades from database"""
    if not DB_PATH.exists():
        return pd.DataFrame()

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM trades", conn)
        conn.close()

        # Convert timestamps
        if not df.empty:
            df['open_date'] = pd.to_datetime(df['open_date'])
            if 'close_date' in df.columns:
                df['close_date'] = pd.to_datetime(df['close_date'])

        return df
    except Exception as e:
        st.error(f"Error loading trades: {e}")
        return pd.DataFrame()

df = load_trades()

# ========== HEADER ==========
st.title("🤖 Freqtrade Trading Monitor")
st.markdown(f"**Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if df.empty:
    st.warning("No trades found. Database may be empty or not yet created.")
    st.info(f"Looking for database at: {DB_PATH}")
    st.stop()

# ========== KEY METRICS ==========
st.subheader("📊 Key Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

closed_trades = df[df['close_date'].notna()]

if not closed_trades.empty:
    total_profit = closed_trades['close_profit_abs'].sum()
    win_rate = (closed_trades['close_profit_abs'] > 0).mean() * 100
    avg_duration = (closed_trades['close_date'] - closed_trades['open_date']).mean()
    avg_duration_hours = avg_duration.total_seconds() / 3600 if pd.notna(avg_duration) else 0

    col1.metric("Total Profit", f"${total_profit:.2f}")
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Total Trades", len(closed_trades))
    col4.metric("Open Trades", len(df[df['close_date'].isna()]))
    col5.metric("Avg Duration", f"{avg_duration_hours:.1f}h")
else:
    col1.metric("Total Profit", "$0.00")
    col2.metric("Win Rate", "N/A")
    col3.metric("Total Trades", "0")
    col4.metric("Open Trades", len(df[df['close_date'].isna()]))
    col5.metric("Avg Duration", "N/A")

# ========== PROFIT CHART ==========
if not closed_trades.empty:
    st.subheader("📈 Cumulative Profit")

    closed_trades_sorted = closed_trades.sort_values('close_date')
    closed_trades_sorted['cumulative_profit'] = closed_trades_sorted['close_profit_abs'].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=closed_trades_sorted['close_date'],
        y=closed_trades_sorted['cumulative_profit'],
        mode='lines',
        name='Cumulative Profit',
        line=dict(color='#00D9FF', width=2)
    ))

    fig.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Profit (USD)",
        hovermode='x unified',
        template='plotly_dark'
    )

    st.plotly_chart(fig, use_container_width=True)

# ========== PERFORMANCE STATISTICS ==========
if not closed_trades.empty:
    st.subheader("📊 Performance Statistics")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Trade Statistics**")
        winning_trades = closed_trades[closed_trades['close_profit_abs'] > 0]
        losing_trades = closed_trades[closed_trades['close_profit_abs'] <= 0]

        stats_df = pd.DataFrame({
            'Metric': [
                'Total Trades',
                'Winning Trades',
                'Losing Trades',
                'Win Rate',
                'Avg Win',
                'Avg Loss',
                'Profit Factor'
            ],
            'Value': [
                len(closed_trades),
                len(winning_trades),
                len(losing_trades),
                f"{win_rate:.2f}%",
                f"${winning_trades['close_profit_abs'].mean():.2f}" if not winning_trades.empty else "$0.00",
                f"${losing_trades['close_profit_abs'].mean():.2f}" if not losing_trades.empty else "$0.00",
                f"{abs(winning_trades['close_profit_abs'].sum() / losing_trades['close_profit_abs'].sum()):.2f}" if not losing_trades.empty and losing_trades['close_profit_abs'].sum() != 0 else "∞"
            ]
        })
        st.dataframe(stats_df, hide_index=True, use_container_width=True)

    with col2:
        st.markdown("**Profit Distribution**")

        fig_dist = go.Figure()
        fig_dist.add_trace(go.Histogram(
            x=closed_trades['close_profit_abs'],
            nbinsx=30,
            marker_color='#00D9FF',
            name='Trades'
        ))

        fig_dist.update_layout(
            height=300,
            xaxis_title="Profit (USD)",
            yaxis_title="Number of Trades",
            showlegend=False,
            template='plotly_dark'
        )

        st.plotly_chart(fig_dist, use_container_width=True)

# ========== RECENT TRADES ==========
st.subheader("📊 Recent Trades")

if not closed_trades.empty:
    recent = closed_trades.sort_values('close_date', ascending=False).head(20)

    display_df = recent[['pair', 'open_date', 'close_date', 'close_profit_abs', 'close_profit', 'enter_tag', 'exit_tag']].copy()
    display_df['close_profit'] = display_df['close_profit'].apply(lambda x: f"{x*100:.2f}%")
    display_df['close_profit_abs'] = display_df['close_profit_abs'].apply(lambda x: f"${x:.2f}")
    display_df.columns = ['Pair', 'Open Date', 'Close Date', 'Profit (USD)', 'Profit (%)', 'Entry Signal', 'Exit Signal']

    st.dataframe(display_df, hide_index=True, use_container_width=True)
else:
    st.info("No closed trades yet.")

# ========== OPEN TRADES ==========
open_trades = df[df['close_date'].isna()]

if not open_trades.empty:
    st.subheader("🔄 Open Trades")

    display_open = open_trades[['pair', 'open_date', 'stake_amount', 'enter_tag']].copy()
    display_open['open_date'] = display_open['open_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    display_open['stake_amount'] = display_open['stake_amount'].apply(lambda x: f"${x:.2f}")
    display_open.columns = ['Pair', 'Open Date', 'Stake Amount', 'Entry Signal']

    st.dataframe(display_open, hide_index=True, use_container_width=True)

# ========== PAIR PERFORMANCE ==========
if not closed_trades.empty:
    st.subheader("💹 Performance by Pair")

    pair_perf = closed_trades.groupby('pair').agg({
        'close_profit_abs': ['sum', 'count', 'mean']
    }).round(2)

    pair_perf.columns = ['Total Profit', 'Trade Count', 'Avg Profit']
    pair_perf = pair_perf.sort_values('Total Profit', ascending=False)

    # Format for display
    pair_perf_display = pair_perf.copy()
    pair_perf_display['Total Profit'] = pair_perf_display['Total Profit'].apply(lambda x: f"${x:.2f}")
    pair_perf_display['Avg Profit'] = pair_perf_display['Avg Profit'].apply(lambda x: f"${x:.2f}")

    st.dataframe(pair_perf_display, use_container_width=True)

# ========== REFRESH ==========
st.markdown("---")
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.markdown("*Data auto-refreshes every 60 seconds*")
