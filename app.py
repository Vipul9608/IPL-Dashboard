import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="IPL Matches Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: #08080f; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d22 0%, #0a0a18 100%);
        border-right: 1px solid #1e1e40;
    }
    .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    h1, h2, h3 { color: #ffffff !important; }
    .stMetric {
        background: linear-gradient(135deg, #111128 0%, #181835 100%);
        border: 1px solid #2a2a55;
        border-radius: 12px;
        padding: 14px 10px;
    }
    .stMetric label { color: #9090bb !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
    .stMetric [data-testid="stMetricValue"] { color: #f5a623 !important; font-size: 26px !important; font-weight: 800; }
    .sec {
        color: #f5a623; font-size: 16px; font-weight: 700;
        border-left: 4px solid #f5a623; padding-left: 10px;
        margin: 14px 0 8px 0;
    }
    div[data-baseweb="tab-list"] { background: #111128; border-radius: 10px; padding: 4px; gap: 4px; }
    div[data-baseweb="tab"] { color: #9090bb !important; border-radius: 8px; }
    div[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #f5a623, #e8890a) !important;
        color: #000000 !important; font-weight: 700;
    }
    .highlight-box {
        background: linear-gradient(135deg, #1a1a35, #222244);
        border: 1px solid #3a3a70; border-radius: 10px;
        padding: 16px; margin: 6px 0;
        text-align: center;
    }
    .highlight-val { color: #f5a623; font-size: 22px; font-weight: 800; }
    .highlight-lbl { color: #aaaacc; font-size: 12px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ──────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("data.csv")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    # Normalise old names
    rename = {
        "Delhi Daredevils":        "Delhi Capitals",
        "Kings XI Punjab":         "Punjab Kings",
        "Deccan Chargers":         "Deccan Chargers",
    }
    for col in ["team1", "team2", "winner", "toss_winner"]:
        df[col] = df[col].replace(rename)
    df["toss_win_match"] = df["toss_winner"] == df["winner"]
    df["win_type"] = np.where(df["win_by_runs"] > 0, "By Runs",
                     np.where(df["win_by_wickets"] > 0, "By Wickets", "Tie/NR"))
    return df

df = load()

# ── TEAM COLOURS ──────────────────────────────────────────────────────────────
TCOLORS = {
    "Chennai Super Kings":       "#f9cd05",
    "Mumbai Indians":            "#005ea6",
    "Kolkata Knight Riders":     "#6a3fa0",
    "Royal Challengers Bangalore":"#c8102e",
    "Sunrisers Hyderabad":       "#f7610b",
    "Delhi Capitals":            "#004c97",
    "Rajasthan Royals":          "#2d4fa1",
    "Punjab Kings":              "#dd1f2d",
    "Kings XI Punjab":           "#dd1f2d",
    "Deccan Chargers":           "#f5a623",
    "Kochi Tuskers Kerala":      "#f26522",
    "Gujarat Lions":             "#e87722",
    "Rising Pune Supergiants":   "#9b59b6",
    "Pune Warriors":             "#003a70",
}
BG   = "rgba(0,0,0,0)"
FONT = "#ddddee"
GRID = "#1a1a30"
GOLD = "#f5a623"
TEAL = "#00d4aa"
RED  = "#ff4c4c"
BLUE = "#4c8dff"

def base(fig, h=370, xangle=0, showlegend=True):
    fig.update_layout(
        plot_bgcolor=BG, paper_bgcolor=BG,
        font=dict(color=FONT, size=11),
        height=h,
        margin=dict(l=6, r=6, t=36, b=6),
        legend=dict(bgcolor="rgba(0,0,0,0.45)", bordercolor="#2a2a50",
                    borderwidth=1, font=dict(size=10),
                    visible=showlegend),
        xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, tickangle=xangle),
        yaxis=dict(gridcolor=GRID, zerolinecolor=GRID),
    )
    return fig

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏏 IPL 2008–2016")
    st.markdown("---")

    seasons = sorted(df["season"].unique())
    sel_seasons = st.multiselect("📅 Seasons", seasons, default=seasons)

    all_teams = sorted(set(df["team1"].dropna()) | set(df["team2"].dropna()))
    sel_teams  = st.multiselect("🏟️ Teams", all_teams, default=all_teams)

    all_cities = sorted(df["city"].dropna().unique())
    sel_cities = st.multiselect("🌆 Cities", all_cities, default=all_cities)

    st.markdown("---")
    st.caption(f"📋 Total matches: {len(df):,}")
    st.caption(f"🏆 Seasons: {min(seasons)} – {max(seasons)}")
    st.caption(f"🏟️ Venues: {df['venue'].nunique()}")

# ── FILTER ────────────────────────────────────────────────────────────────────
fdf = df[
    df["season"].isin(sel_seasons) &
    (df["team1"].isin(sel_teams) | df["team2"].isin(sel_teams)) &
    df["city"].isin(sel_cities)
].copy()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("# 🏏 IPL Matches Analytics — 2008 to 2016")
st.markdown(f"<span style='color:#9090bb'>Analysing <b style='color:#f5a623'>{len(fdf):,}</b> matches across <b style='color:#f5a623'>{fdf['season'].nunique()}</b> seasons</span>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("🏟️ Matches",        f"{len(fdf):,}")
k2.metric("🏆 Seasons",        f"{fdf['season'].nunique()}")
k3.metric("👥 Teams",          f"{fdf['team1'].nunique()}")
k4.metric("🌆 Cities",         f"{fdf['city'].nunique()}")
k5.metric("🎯 Toss→Win %",     f"{fdf['toss_win_match'].mean()*100:.1f}%")
k6.metric("🏅 Unique POTM",    f"{fdf['player_of_match'].nunique()}")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏆 Team Performance",
    "🎲 Toss & Strategy",
    "📊 Win Patterns",
    "🌍 Venues & Cities",
    "🏅 Player of the Match"
])

# ═══════════════════════ TAB 1 – TEAM PERFORMANCE ════════════════════════════
with tab1:

    wins = (fdf["winner"].value_counts()
            .reset_index().rename(columns={"winner":"Team","count":"Wins"}))
    wins = wins[wins["Team"].isin(sel_teams)]

    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.markdown('<div class="sec">🏆 All-Time Wins Leaderboard</div>', unsafe_allow_html=True)
        colors = [TCOLORS.get(t, GOLD) for t in wins["Team"]]
        fig = go.Figure(go.Bar(
            x=wins["Wins"], y=wins["Team"], orientation="h",
            marker=dict(color=colors, line=dict(color="#ffffff22", width=0.5)),
            text=wins["Wins"], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Wins: %{x}<extra></extra>"
        ))
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(base(fig, 430), use_container_width=True)

    with col2:
        st.markdown('<div class="sec">🥧 Win Share by Team</div>', unsafe_allow_html=True)
        fig2 = px.pie(wins.head(10), values="Wins", names="Team", hole=0.48,
                      color="Team", color_discrete_map=TCOLORS)
        fig2.update_traces(textposition="inside", textinfo="percent+label",
                           textfont_size=10)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(base(fig2, 430, showlegend=False), use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="sec">📈 Season-wise Wins per Team</div>', unsafe_allow_html=True)
        top8 = wins.head(8)["Team"].tolist()
        season_wins = (fdf[fdf["winner"].isin(top8)]
                       .groupby(["season","winner"]).size()
                       .reset_index(name="wins"))
        fig3 = px.line(season_wins, x="season", y="wins", color="winner",
                       markers=True, color_discrete_map=TCOLORS,
                       labels={"winner":"Team","wins":"Wins"})
        fig3.update_traces(line_width=2.5)
        st.plotly_chart(base(fig3, 370, xangle=-30), use_container_width=True)

    with col4:
        st.markdown('<div class="sec">⚔️ Head-to-Head Showdown</div>', unsafe_allow_html=True)
        popular = wins.head(10)["Team"].tolist()
        hA = st.selectbox("Team A", popular, index=0)
        hB = st.selectbox("Team B", [t for t in popular if t != hA], index=1)
        h2h = fdf[
            ((fdf["team1"]==hA)&(fdf["team2"]==hB)) |
            ((fdf["team1"]==hB)&(fdf["team2"]==hA))
        ]
        wA = (h2h["winner"]==hA).sum()
        wB = (h2h["winner"]==hB).sum()
        tie = len(h2h) - wA - wB

        fig4 = go.Figure(go.Bar(
            x=[hA, hB, "Tie/NR"],
            y=[wA, wB, tie],
            marker_color=[TCOLORS.get(hA, GOLD), TCOLORS.get(hB, TEAL), "#555555"],
            text=[wA, wB, tie], textposition="outside",
        ))
        fig4.update_layout(title=f"Total encounters: {len(h2h)}", title_font_color="#aaaacc")
        st.plotly_chart(base(fig4, 340), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="sec">📊 Matches Played vs Won (Efficiency)</div>', unsafe_allow_html=True)
    played = pd.concat([fdf["team1"], fdf["team2"]]).value_counts().reset_index()
    played.columns = ["Team","Played"]
    efficiency = wins.merge(played, on="Team")
    efficiency["Win%"] = (efficiency["Wins"] / efficiency["Played"] * 100).round(1)
    efficiency = efficiency[efficiency["Team"].isin(sel_teams)].sort_values("Win%", ascending=False)
    fig5 = px.scatter(efficiency, x="Played", y="Wins", size="Win%",
                      color="Team", hover_name="Team",
                      text="Team",
                      color_discrete_map=TCOLORS, size_max=40,
                      labels={"Played":"Matches Played","Wins":"Matches Won"})
    fig5.update_traces(textposition="top center", textfont_size=9)
    st.plotly_chart(base(fig5, 400), use_container_width=True)


# ═══════════════════════ TAB 2 – TOSS & STRATEGY ═════════════════════════════
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="sec">🪙 Toss Decision Trend by Season</div>', unsafe_allow_html=True)
        toss_trend = fdf.groupby(["season","toss_decision"]).size().reset_index(name="count")
        fig = px.bar(toss_trend, x="season", y="count", color="toss_decision",
                     barmode="stack",
                     color_discrete_map={"field": TEAL, "bat": GOLD},
                     labels={"count":"Matches","toss_decision":"Decision"})
        st.plotly_chart(base(fig, 360, xangle=-30), use_container_width=True)

    with col2:
        st.markdown('<div class="sec">🎯 Does Winning Toss Help Win the Match?</div>', unsafe_allow_html=True)
        tw = fdf.dropna(subset=["winner"])
        tw_counts = tw["toss_win_match"].value_counts().reset_index()
        tw_counts.columns = ["Result","Count"]
        tw_counts["Result"] = tw_counts["Result"].map({True:"✅ Toss Winner Won", False:"❌ Toss Winner Lost"})
        fig2 = px.pie(tw_counts, values="Count", names="Result", hole=0.52,
                      color_discrete_map={"✅ Toss Winner Won": TEAL, "❌ Toss Winner Lost": RED})
        fig2.update_traces(textinfo="label+percent+value")
        st.plotly_chart(base(fig2, 360, showlegend=False), use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="sec">🏏 Toss Decision by Team (Field vs Bat)</div>', unsafe_allow_html=True)
        toss_team = (fdf[fdf["toss_winner"].isin(sel_teams)]
                     .groupby(["toss_winner","toss_decision"]).size()
                     .reset_index(name="count"))
        fig3 = px.bar(toss_team, x="toss_winner", y="count", color="toss_decision",
                      barmode="group",
                      color_discrete_map={"field": TEAL, "bat": GOLD},
                      labels={"count":"Times","toss_winner":"Team","toss_decision":"Decision"})
        fig3.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(base(fig3, 370), use_container_width=True)

    with col4:
        st.markdown('<div class="sec">🏆 Toss Win → Match Win Rate by Team</div>', unsafe_allow_html=True)
        toss_eff = (fdf[fdf["toss_winner"].isin(sel_teams)]
                    .groupby("toss_winner")["toss_win_match"]
                    .agg(["sum","count"]).reset_index())
        toss_eff.columns = ["Team","Converted","Total"]
        toss_eff["Rate%"] = (toss_eff["Converted"] / toss_eff["Total"] * 100).round(1)
        toss_eff = toss_eff.sort_values("Rate%", ascending=False)
        colors = [TCOLORS.get(t, GOLD) for t in toss_eff["Team"]]
        fig4 = go.Figure(go.Bar(
            y=toss_eff["Team"], x=toss_eff["Rate%"], orientation="h",
            marker=dict(color=colors),
            text=toss_eff["Rate%"].astype(str) + "%", textposition="outside",
        ))
        fig4.add_vline(x=50, line_dash="dash", line_color="#ffffff55",
                       annotation_text="50%", annotation_font_color="#aaaacc")
        fig4.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(base(fig4, 370), use_container_width=True)


# ═══════════════════════ TAB 3 – WIN PATTERNS ════════════════════════════════
with tab3:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="sec">🏏 Win by Runs — Distribution</div>', unsafe_allow_html=True)
        runs_wins = fdf[fdf["win_by_runs"] > 0]
        fig = px.histogram(runs_wins, x="win_by_runs", nbins=30,
                           color_discrete_sequence=[GOLD],
                           labels={"win_by_runs": "Winning Margin (Runs)"})
        fig.add_vline(x=runs_wins["win_by_runs"].mean(), line_dash="dash",
                      line_color=RED,
                      annotation_text=f"Avg: {runs_wins['win_by_runs'].mean():.1f}",
                      annotation_font_color=RED)
        st.plotly_chart(base(fig, 360), use_container_width=True)

    with col2:
        st.markdown('<div class="sec">🎳 Win by Wickets — Distribution</div>', unsafe_allow_html=True)
        wkt_wins = fdf[fdf["win_by_wickets"] > 0]
        wkt_count = wkt_wins["win_by_wickets"].value_counts().sort_index().reset_index()
        wkt_count.columns = ["Wickets","Matches"]
        fig2 = px.bar(wkt_count, x="Wickets", y="Matches",
                      color="Matches", color_continuous_scale="Teal",
                      text="Matches")
        fig2.update_traces(textposition="outside")
        st.plotly_chart(base(fig2, 360), use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="sec">📦 Win Margin Boxplot by Win Type</div>', unsafe_allow_html=True)
        box_runs = fdf[fdf["win_by_runs"]>0][["win_by_runs"]].assign(Type="By Runs", Margin=fdf[fdf["win_by_runs"]>0]["win_by_runs"])
        box_wkts = fdf[fdf["win_by_wickets"]>0][["win_by_wickets"]].assign(Type="By Wickets", Margin=fdf[fdf["win_by_wickets"]>0]["win_by_wickets"])
        box_data = pd.concat([
            box_runs[["Type","Margin"]],
            box_wkts[["Type","Margin"]]
        ])
        fig3 = px.box(box_data, x="Type", y="Margin", color="Type",
                      color_discrete_map={"By Runs": GOLD, "By Wickets": TEAL},
                      points="all")
        st.plotly_chart(base(fig3, 360), use_container_width=True)

    with col4:
        st.markdown('<div class="sec">🗓️ Matches per Season</div>', unsafe_allow_html=True)
        mps = fdf.groupby("season").size().reset_index(name="Matches")
        fig4 = px.bar(mps, x="season", y="Matches",
                      color="Matches", color_continuous_scale="Blues",
                      text="Matches")
        fig4.update_traces(textposition="outside")
        st.plotly_chart(base(fig4, 360, xangle=-30), use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="sec">🔥 Biggest Wins by Runs — Top 15</div>', unsafe_allow_html=True)
    big_wins = (fdf[fdf["win_by_runs"]>0]
                .nlargest(15, "win_by_runs")
                [["season","winner","win_by_runs","venue"]]
                .reset_index(drop=True))
    colors2 = [TCOLORS.get(t, GOLD) for t in big_wins["winner"]]
    fig5 = go.Figure(go.Bar(
        x=big_wins["win_by_runs"],
        y=big_wins.apply(lambda r: f"{r['winner']} ({r['season']})", axis=1),
        orientation="h",
        marker=dict(color=colors2),
        text=big_wins["win_by_runs"], textposition="outside",
        hovertext=big_wins["venue"], hovertemplate="<b>%{y}</b><br>Margin: %{x} runs<br>Venue: %{hovertext}<extra></extra>"
    ))
    fig5.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(base(fig5, 420), use_container_width=True)


# ═══════════════════════ TAB 4 – VENUES & CITIES ═════════════════════════════
with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="sec">🏟️ Top Venues by Matches Hosted</div>', unsafe_allow_html=True)
        venues = (fdf["venue"].value_counts().head(12)
                  .reset_index().rename(columns={"venue":"Venue","count":"Matches"}))
        venues["Venue"] = venues["Venue"].str[:32]
        fig = px.bar(venues, x="Matches", y="Venue", orientation="h",
                     color="Matches", color_continuous_scale="Oranges",
                     text="Matches")
        fig.update_traces(textposition="outside")
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(base(fig, 420), use_container_width=True)

    with col2:
        st.markdown('<div class="sec">🌆 Matches by City</div>', unsafe_allow_html=True)
        city_m = (fdf["city"].value_counts().head(15)
                  .reset_index().rename(columns={"city":"City","count":"Matches"}))
        fig2 = px.bar(city_m, x="City", y="Matches",
                      color="Matches", color_continuous_scale="Teal",
                      text="Matches")
        fig2.update_traces(textposition="outside")
        fig2.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(base(fig2, 420), use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="sec">🏆 Most Wins at Each Venue</div>', unsafe_allow_html=True)
        venue_wins = (fdf.dropna(subset=["winner"])
                      .groupby(["venue","winner"]).size()
                      .reset_index(name="wins"))
        top_venue_list = venues["Venue"].str.strip().tolist()
        top_vw = (venue_wins.sort_values("wins", ascending=False)
                  .groupby("venue").head(1)
                  .sort_values("wins", ascending=False).head(12))
        top_vw["venue"] = top_vw["venue"].str[:28]
        colors3 = [TCOLORS.get(t, GOLD) for t in top_vw["winner"]]
        fig3 = go.Figure(go.Bar(
            x=top_vw["wins"], y=top_vw["venue"], orientation="h",
            marker=dict(color=colors3),
            text=top_vw["winner"].str.split().str[0],
            textposition="inside",
            hovertemplate="<b>%{y}</b><br>Top team: %{text}<br>Wins: %{x}<extra></extra>"
        ))
        fig3.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(base(fig3, 420), use_container_width=True)

    with col4:
        st.markdown('<div class="sec">📅 Season vs City — Match Heatmap</div>', unsafe_allow_html=True)
        top_cities_list = city_m.head(10)["City"].tolist()
        hmap = (fdf[fdf["city"].isin(top_cities_list)]
                .groupby(["season","city"]).size()
                .reset_index(name="matches"))
        pivot = hmap.pivot(index="city", columns="season", values="matches").fillna(0)
        fig4 = px.imshow(pivot, color_continuous_scale="YlOrRd",
                         labels=dict(x="Season", y="City", color="Matches"),
                         aspect="auto", text_auto=True)
        fig4.update_coloraxes(showscale=False)
        st.plotly_chart(base(fig4, 420), use_container_width=True)


# ════════════════════ TAB 5 – PLAYER OF THE MATCH ════════════════════════════
with tab5:
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown('<div class="sec">🏅 Most Player of the Match Awards</div>', unsafe_allow_html=True)
        top_n = st.slider("Show top N players", 5, 25, 15)
        potm = (fdf["player_of_match"].value_counts()
                .head(top_n).reset_index()
                .rename(columns={"player_of_match":"Player","count":"Awards"}))
        fig = px.bar(potm, x="Awards", y="Player", orientation="h",
                     color="Awards", color_continuous_scale="YlOrRd",
                     text="Awards")
        fig.update_traces(textposition="outside")
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(base(fig, 480), use_container_width=True)

    with col2:
        st.markdown('<div class="sec">📈 POTM Awards by Season</div>', unsafe_allow_html=True)
        top10_players = potm.head(10)["Player"].tolist()
        potm_season = (fdf[fdf["player_of_match"].isin(top10_players)]
                       .groupby(["season","player_of_match"]).size()
                       .reset_index(name="awards"))
        fig2 = px.line(potm_season, x="season", y="awards",
                       color="player_of_match", markers=True,
                       labels={"player_of_match":"Player","awards":"Awards"},
                       color_discrete_sequence=px.colors.qualitative.Bold)
        fig2.update_layout(xaxis_tickangle=-30)
        st.plotly_chart(base(fig2, 480), use_container_width=True)

    st.markdown("---")
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<div class="sec">🌟 POTM Winners per Team</div>', unsafe_allow_html=True)
        # Find team of winner (winner column is the winning team)
        potm_team = (fdf.dropna(subset=["player_of_match","winner"])
                     .groupby("winner")["player_of_match"].count()
                     .reset_index(name="POTM Awards")
                     .sort_values("POTM Awards", ascending=False))
        potm_team = potm_team[potm_team["winner"].isin(sel_teams)]
        colors4 = [TCOLORS.get(t, GOLD) for t in potm_team["winner"]]
        fig3 = go.Figure(go.Bar(
            y=potm_team["winner"], x=potm_team["POTM Awards"],
            orientation="h", marker=dict(color=colors4),
            text=potm_team["POTM Awards"], textposition="outside"
        ))
        fig3.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(base(fig3, 380), use_container_width=True)

    with col4:
        st.markdown('<div class="sec">📊 POTM by Win Type</div>', unsafe_allow_html=True)
        potm_wtype = (fdf.dropna(subset=["player_of_match"])
                      .groupby(["win_type","player_of_match"]).size()
                      .reset_index(name="count")
                      .sort_values("count", ascending=False)
                      .groupby("win_type").head(5))
        fig4 = px.bar(potm_wtype, x="count", y="player_of_match",
                      color="win_type", orientation="h",
                      color_discrete_map={"By Runs": GOLD, "By Wickets": TEAL, "Tie/NR": RED},
                      labels={"count":"Awards","player_of_match":"Player","win_type":"Win Type"},
                      barmode="group")
        fig4.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(base(fig4, 380), use_container_width=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("🏏 IPL Matches Dashboard · Seasons 2008–2016 · Built with Streamlit & Plotly")
