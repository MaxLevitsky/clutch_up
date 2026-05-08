# Feature: Dashboard
# Traceability: UC-DASH-1.1, UC-DASH-2.1, UC-DASH-3.1

import os
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
from datetime import datetime, timedelta

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///../clutchup.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})


def query(sql: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_query(text(sql), conn)


st.set_page_config(page_title="ClutchUp Dashboard", layout="wide")
st.title("ClutchUp Internal Dashboard")

tab1, tab2, tab3 = st.tabs(["System Health", "Product Health", "Unit Economics"])

# ── Tab 1: System Health ─────────────────────────────────────────────────────
with tab1:
    st.header("System Health")

    logs = query("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 5000")

    if logs.empty:
        st.info("No request logs yet. Make some API calls first.")
    else:
        logs["timestamp"] = pd.to_datetime(logs["timestamp"])
        last_24h = logs[logs["timestamp"] > datetime.utcnow() - timedelta(hours=24)]

        col1, col2, col3 = st.columns(3)
        total = len(last_24h)
        errors = last_24h[last_24h["status_code"] >= 400]
        error_rate = round(len(errors) / total * 100, 1) if total else 0
        avg_latency = round(last_24h["duration_ms"].mean(), 1) if total else 0
        p95_latency = round(last_24h["duration_ms"].quantile(0.95), 1) if total else 0

        col1.metric("Error Rate (24h)", f"{error_rate}%", delta_color="inverse")
        col2.metric("Avg Latency (24h)", f"{avg_latency} ms")
        col3.metric("P95 Latency (24h)", f"{p95_latency} ms")

        if error_rate > 5:
            st.error(f"⚠️ Error rate {error_rate}% exceeds threshold of 5%")

        # Requests per hour chart
        hourly = last_24h.set_index("timestamp").resample("1h").size().reset_index(name="requests")
        fig = px.bar(hourly, x="timestamp", y="requests", title="Requests per Hour (last 24h)")
        st.plotly_chart(fig, use_container_width=True)

        # Top errors
        st.subheader("Recent Errors")
        err_df = last_24h[last_24h["status_code"] >= 400][["timestamp", "method", "path", "status_code", "duration_ms"]].head(20)
        st.dataframe(err_df, use_container_width=True)

# ── Tab 2: Product Health ────────────────────────────────────────────────────
with tab2:
    st.header("Product Health")

    players_df = query("SELECT id, created_at FROM players")
    regs_df = query("SELECT player_id, MIN(registered_at) as first_reg FROM tournament_registrations GROUP BY player_id")
    teams_df = query("SELECT COUNT(*) as team_count FROM teams")

    if players_df.empty:
        st.info("No players yet.")
    else:
        players_df["created_at"] = pd.to_datetime(players_df["created_at"])
        total_players = len(players_df)

        if not regs_df.empty:
            regs_df["first_reg"] = pd.to_datetime(regs_df["first_reg"])
            merged = players_df.merge(regs_df, left_on="id", right_on="player_id", how="left")
            merged["days_to_first"] = (merged["first_reg"] - merged["created_at"]).dt.days
            activated = merged[(merged["days_to_first"].notna()) & (merged["days_to_first"] <= 7)]
            activation_rate = round(len(activated) / total_players * 100, 1)
        else:
            activation_rate = 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Players", total_players)
        col2.metric("Activation Rate (7d)", f"{activation_rate}%")
        col3.metric("Total Teams", int(teams_df["team_count"].iloc[0]) if not teams_df.empty else 0)

        # Registration funnel
        regs_total = query("SELECT COUNT(DISTINCT player_id) as n FROM tournament_registrations")
        matches_total = query("SELECT COUNT(DISTINCT winner_id) as n FROM matches WHERE winner_id IS NOT NULL")

        funnel_data = pd.DataFrame({
            "Stage": ["Registered Players", "Joined a Tournament", "Won a Match"],
            "Count": [
                total_players,
                int(regs_total["n"].iloc[0]) if not regs_total.empty else 0,
                int(matches_total["n"].iloc[0]) if not matches_total.empty else 0,
            ]
        })
        fig2 = px.funnel(funnel_data, x="Count", y="Stage", title="Onboarding Funnel")
        st.plotly_chart(fig2, use_container_width=True)

        # Daily new players
        players_df["date"] = players_df["created_at"].dt.date
        daily = players_df.groupby("date").size().reset_index(name="new_players")
        fig3 = px.line(daily, x="date", y="new_players", title="Daily New Players")
        st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Unit Economics ────────────────────────────────────────────────────
with tab3:
    st.header("Unit Economics")

    logs_all = query("SELECT path, duration_ms, timestamp FROM system_logs ORDER BY timestamp DESC LIMIT 10000")

    if logs_all.empty:
        st.info("No logs yet.")
    else:
        logs_all["timestamp"] = pd.to_datetime(logs_all["timestamp"])

        col1, col2 = st.columns(2)

        # Requests per day
        logs_all["date"] = logs_all["timestamp"].dt.date
        rpd = logs_all.groupby("date").size().reset_index(name="requests")
        fig4 = px.bar(rpd, x="date", y="requests", title="Requests per Day")
        col1.plotly_chart(fig4, use_container_width=True)

        # Top endpoints by volume
        top_paths = logs_all["path"].value_counts().head(10).reset_index()
        top_paths.columns = ["path", "count"]
        fig5 = px.bar(top_paths, x="count", y="path", orientation="h", title="Top 10 Endpoints by Volume")
        col2.plotly_chart(fig5, use_container_width=True)

        # Top endpoints by avg latency
        lat = logs_all.groupby("path")["duration_ms"].mean().sort_values(ascending=False).head(10).reset_index()
        lat.columns = ["path", "avg_latency_ms"]
        fig6 = px.bar(lat, x="avg_latency_ms", y="path", orientation="h", title="Top 10 Endpoints by Avg Latency (ms)")
        st.plotly_chart(fig6, use_container_width=True)

        # DB size
        db_file = "../clutchup.db"
        if os.path.exists(db_file):
            size_kb = round(os.path.getsize(db_file) / 1024, 1)
            st.metric("Database Size", f"{size_kb} KB")
