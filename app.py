import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine

# Page Config
st.set_page_config(layout="wide", page_title="STRATEGIC CONTROLLER DASHBOARD - GRÜNENTAL", initial_sidebar_state="collapsed", page_icon="➕")

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'database': 'grunental_db',
    'user': 'postgres',
    'password': '12345'
}
engine = create_engine(f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")

# Initialize session state for country selection
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None

# --- GRÜNENTAL BRAND PALETTE ---
GRUNENTAL_GREEN = "#2ECC71"
GRUNENTAL_NAVY = "#002C5F"
GRUNENTAL_BLUE = "#009DE0"
GRUNENTAL_LIME = "#A2D149"
GRUNENTAL_TEAL = "#008080"
WHITE = "#FFFFFF"
SOFT_GREY = "#F8F9FA"
DARK_GREY = "#4A5568"

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {WHITE};
        overflow: hidden;
        height: 100vh;
        color: {GRUNENTAL_NAVY};
    }}
    .block-container {{
        padding-top: 0.4rem;
        padding-bottom: 0rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
        max-width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.2rem;
        border-bottom: 2px solid {GRUNENTAL_GREEN};
        padding-bottom: 5px;
    }}
    .logo-text {{ color: {GRUNENTAL_NAVY}; font-size: 26px; font-weight: 800; display: flex; align-items: center; gap: 8px; }}
    .logo-icon {{ color: {GRUNENTAL_GREEN}; font-size: 30px; }}
    .header-subtitle {{ color: {DARK_GREY}; font-size: 12px; margin-top: -4px; font-weight: 600; }}
    .chip {{ padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 700; color: white; background-color: {GRUNENTAL_NAVY}; text-transform: uppercase; }}
    .section-header {{ font-size: 13px; font-weight: 800; color: {GRUNENTAL_NAVY}; margin-bottom: 12px; border-left: 3px solid {GRUNENTAL_GREEN}; padding-left: 8px; }}
    .minimal-footer {{ font-size: 9px; color: {DARK_GREY}; border-top: 1px solid #EEE; padding: 8px 0; margin-top: auto; display: flex; justify-content: space-between; align-items: center; }}
    .footer-author {{ font-weight: 800; color: {GRUNENTAL_BLUE}; }}
    
    /* FILTER LABELS COLOR */
    [data-testid="stWidgetLabel"] p {{
        color: {GRUNENTAL_NAVY} !important;
        font-weight: 700 !important;
        font-size: 13px !important;
    }}
    
    /* OVERRIDE DEFAULT STREAMLIT RED (#ff4b4b) WITH GRÜNENTAL GREEN */
    :root {{
        --primary-color: {GRUNENTAL_GREEN} !important;
    }}
    
    /* RESET BUTTON SPECIAL STYLE (Transparent background, Green text) */
    div.stButton > button {{
        background-color: transparent !important;
        color: {GRUNENTAL_GREEN} !important;
        border: 1px solid {GRUNENTAL_GREEN} !important;
        transition: 0.3s !important;
        font-weight: 700 !important;
    }}
    div.stButton > button:hover {{
        background-color: {GRUNENTAL_GREEN} !important;
        color: white !important;
    }}
    
    /* Multiselect tags and selection */
    span[data-baseweb="tag"] {{
        background-color: {GRUNENTAL_NAVY} !important;
        color: white !important;
        font-size: 11px !important; /* Smaller text for selected items */
        padding: 1px 6px !important;
    }}
    div[data-baseweb="select"] > div {{
        border-color: {GRUNENTAL_NAVY} !important;
        min-height: 32px !important;
    }}
    div[data-baseweb="popover"] ul li {{
        font-size: 11px !important; /* Smaller text in dropdown list */
    }}
    div[data-baseweb="popover"] ul li:hover {{
        background-color: {GRUNENTAL_GREEN} !important;
        color: white !important;
    }}
    
    /* Input and Select focus */
    .stTextInput > div > div > input:focus, .stSelectbox > div > div > div:focus {{
        border-color: {GRUNENTAL_GREEN} !important;
        box-shadow: 0 0 0 2px rgba(46, 204, 113, 0.2) !important;
    }}
    
    /* SLIDER CUSTOMIZATION */
    .stSlider [data-baseweb="slider"] > div {{
        background-color: transparent !important;
    }}
    .stSlider [data-baseweb="slider"] > div > div {{
        background: {GRUNENTAL_NAVY} !important;
    }}
    .stSlider [data-baseweb="slider"] [role="slider"] {{
        background-color: {GRUNENTAL_NAVY} !important;
        border: 2px solid {GRUNENTAL_GREEN} !important;
        box-shadow: none !important;
    }}
    .stSlider [data-testid="stSliderTickBar"] {{
        color: {GRUNENTAL_NAVY} !important;
        font-weight: 700 !important;
    }}
    
    /* Ensure spinners and other elements use corporate green */
    .stSpinner > div {{
        border-top-color: {GRUNENTAL_GREEN} !important;
    }}
    
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
""", unsafe_allow_html=True)

# Animation Helpers
def update_fig_layout(fig, height=180):
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=25, b=10), # Added more top margin for labels
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=GRUNENTAL_NAVY, size=10),
        showlegend=False, # Global legend removal by default
        transition=dict(duration=1500, easing="cubic-in-out")
    )
    return fig

def animated_kpi(label, value, prefix="€", suffix="", color=GRUNENTAL_NAVY):
    fig = go.Figure(go.Indicator(
        mode = "number",
        value = value,
        number = {
            'prefix': prefix, 
            'suffix': suffix, 
            'font': {'size': 24, 'color': color, 'family': "Arial Black"},
            'valueformat': ',.0f'
        },
        title = {'text': label, 'font': {'size': 11, 'color': DARK_GREY, 'family': "Arial"}}
    ))
    fig.update_layout(
        height=80, 
        margin=dict(l=5, r=5, t=5, b=5),
        transition={'duration': 2000, 'easing': 'cubic-in-out'}
    )
    return fig

# Data Fetching
@st.cache_data
def get_master_data():
    return pd.read_sql("SELECT * FROM master_performance", engine)

@st.cache_data
def get_allocation_data():
    return pd.read_sql("SELECT * FROM allocation_summary", engine)

@st.cache_data
def get_highest_expenses():
    return pd.read_sql("SELECT * FROM highest_expenses", engine)

# --- HEADER ---
st.markdown(f"""
    <div class="header-container">
        <div>
            <div class="logo-text"><span class="logo-icon">+</span> Grunental</div>
            <div class="header-subtitle">Strategic Business Partner · Global Sales & Performance Engine</div>
        </div>
        <div style="display: flex; gap: 5px;">
            <div class="chip">FY 2024</div>
            <div class="chip" style="background:{GRUNENTAL_BLUE}">GLOBAL PRESENCE</div>
            <div class="chip" style="background:{GRUNENTAL_GREEN}">CONFIDENTIAL</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- FILTERS ---
df_master = get_master_data()

col_f1, col_f2, col_f3, col_f4 = st.columns([1, 1, 1.5, 0.5])
with col_f1:
    areas_list = sorted(df_master['area'].unique().tolist())
    selected_areas = st.multiselect("BUSINESS UNIT", options=areas_list, default=areas_list)
with col_f2:
    products_list = sorted(df_master['product'].unique().tolist())
    selected_products = st.multiselect("PRODUCT PORTFOLIO", options=products_list, default=products_list)
with col_f3:
    months_list = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    month_range = st.select_slider("PERIOD ANALYSIS", options=months_list, value=("Ene", "Dic"))
with col_f4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 RESET"):
        st.session_state.selected_country = None
        st.rerun()

# --- UNIFIED FILTER LOGIC ---
start_idx = months_list.index(month_range[0]) + 1
end_idx = months_list.index(month_range[1]) + 1

# Filter by period
filtered_df = df_master[(df_master['month_idx'] >= start_idx) & (df_master['month_idx'] <= end_idx)]

# Filter by Country (Session State)
if st.session_state.selected_country:
    filtered_df = filtered_df[filtered_df['country'] == st.session_state.selected_country]
    st.info(f"📍 Country Focus: **{st.session_state.selected_country}** (Click bubble to switch, RESET to clear)")

# Filter by Area and Product (Multiselect)
filtered_df = filtered_df[filtered_df['area'].isin(selected_areas)]
filtered_df = filtered_df[filtered_df['product'].isin(selected_products)]

# --- METRICS ---
if not filtered_df.empty:
    total_sales = filtered_df['sales_volume'].sum()
    total_expenses = filtered_df['actual_expenses'].sum()
    total_budget = filtered_df['budget_expenses'].sum()
    roi = (total_sales / total_expenses) if total_expenses > 0 else 0
else:
    total_sales = total_expenses = total_budget = roi = 0

# --- KPI ROW ---
k1, k2, k3, k4 = st.columns(4)
with k1: st.plotly_chart(animated_kpi("GLOBAL SALES VOLUME", total_sales), use_container_width=True, config={'displayModeBar': False})
with k2: st.plotly_chart(animated_kpi("OPERATIONAL EXPENSES", total_expenses, color=GRUNENTAL_BLUE), use_container_width=True, config={'displayModeBar': False})
with k3: st.plotly_chart(animated_kpi("BUDGET ALLOCATION", total_budget, color=DARK_GREY), use_container_width=True, config={'displayModeBar': False})
with k4: st.plotly_chart(animated_kpi("EFFICIENCY RATIO (S/E)", roi, prefix="x", color=GRUNENTAL_GREEN), use_container_width=True, config={'displayModeBar': False})

# --- MAIN DASHBOARD LAYOUT ---
# ROW 1: STRATEGIC ANALYSIS
row1_col1, row1_col2 = st.columns([1.1, 0.9])

with row1_col1:
    st.markdown(f'<div class="section-header">🌍 Global Sales Distribution by Country (Select Bubble to Filter)</div>', unsafe_allow_html=True)
    bubble_base_df = df_master[(df_master['month_idx'] >= start_idx) & (df_master['month_idx'] <= end_idx)]
    bubble_base_df = bubble_base_df[bubble_base_df['area'].isin(selected_areas)]
    bubble_base_df = bubble_base_df[bubble_base_df['product'].isin(selected_products)]
    
    if not bubble_base_df.empty:
        geo_agg = bubble_base_df.groupby(['country']).agg({'sales_volume': 'sum'}).reset_index().sort_values(by='sales_volume', ascending=True)
        geo_agg['sales_label'] = geo_agg['sales_volume'].apply(lambda x: f"{x/1e6:.1f}M")
        
        if st.session_state.selected_country:
            geo_agg['display_color'] = geo_agg['country'].apply(lambda x: GRUNENTAL_GREEN if x == st.session_state.selected_country else "#D1D5DB")
        else:
            geo_agg['display_color'] = geo_agg['country']

        fig_bubble = px.scatter(geo_agg, x="country", y="sales_volume", size="sales_volume", color="country" if not st.session_state.selected_country else "display_color",
                               hover_name="country", size_max=40,
                               text="sales_label",
                               color_discrete_sequence=[GRUNENTAL_NAVY, GRUNENTAL_BLUE, GRUNENTAL_GREEN, 
                                                     GRUNENTAL_LIME, GRUNENTAL_TEAL, "#D1D5DB", "#888888"])
        
        fig_bubble.update_traces(
            textposition='top center', 
            textfont=dict(size=11, color=GRUNENTAL_NAVY, family="Arial Black"),
            cliponaxis=False
        )
        fig_bubble.update_layout(xaxis_title="", yaxis_title="Total Sales (€)", xaxis={'categoryorder':'total ascending'})
        
        selected_points = st.plotly_chart(update_fig_layout(fig_bubble, height=280), 
                                          use_container_width=True, 
                                          config={'displayModeBar': False},
                                          on_select="rerun",
                                          selection_mode="points")
        
        if selected_points and "selection" in selected_points and selected_points["selection"]["points"]:
            new_selection = selected_points["selection"]["points"][0]["x"]
            if new_selection != st.session_state.selected_country:
                st.session_state.selected_country = new_selection
                st.rerun()
    else:
        st.warning("No data found for selected filters.")

with row1_col2:
    st.markdown(f'<div class="section-header">📈 Performance Trend: Sales vs Expenses</div>', unsafe_allow_html=True)
    if not filtered_df.empty:
        trend_data = filtered_df.groupby(['month', 'month_idx']).agg({'sales_volume': 'sum', 'actual_expenses': 'sum'}).reset_index().sort_values('month_idx')
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=trend_data['month'], y=trend_data['sales_volume'], name='Sales', 
                                       line=dict(color=GRUNENTAL_GREEN, width=3), mode='lines+markers'))
        fig_trend.add_trace(go.Bar(x=trend_data['month'], y=trend_data['actual_expenses'], name='Expenses', 
                                   marker_color=GRUNENTAL_BLUE, opacity=0.4))
        
        if len(trend_data) > 1:
            trend_data['ma'] = trend_data['sales_volume'].rolling(window=3, min_periods=1).mean()
            fig_trend.add_trace(go.Scatter(x=trend_data['month'], y=trend_data['ma'], name='Sales Trend', 
                                           line=dict(color=GRUNENTAL_LIME, width=2, dash='dot')))
        
        st.plotly_chart(update_fig_layout(fig_trend, height=280), use_container_width=True, config={'displayModeBar': False})

# ROW 2: OPERATIONAL ANALYSIS
row2_col1, row2_col2, row2_col3 = st.columns([1, 1, 1])

with row2_col1:
    st.markdown(f'<div class="section-header">🍩 OpEx Allocation</div>', unsafe_allow_html=True)
    if not filtered_df.empty:
        df_alloc_dynamic = filtered_df.groupby('area')['actual_expenses'].sum().reset_index()
        fig_pie = px.pie(df_alloc_dynamic, values='actual_expenses', names='area', hole=0.5, 
                         color_discrete_sequence=[GRUNENTAL_NAVY, GRUNENTAL_BLUE, GRUNENTAL_GREEN, GRUNENTAL_TEAL, GRUNENTAL_LIME])
        fig_pie.update_traces(
            textinfo='label+percent',
            textfont=dict(color=WHITE, size=11),
            textposition='inside',
            insidetextorientation='horizontal',
            hoverinfo='label+percent+value'
        )
        st.plotly_chart(update_fig_layout(fig_pie, height=200), use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("Select filters")

with row2_col2:
    st.markdown(f'<div class="section-header">📊 BU Execution (Sorted Desc)</div>', unsafe_allow_html=True)
    if not filtered_df.empty:
        bu_perf = filtered_df.groupby('area').agg({'actual_expenses': 'sum'}).reset_index()
        bu_perf = bu_perf.sort_values(by='actual_expenses', ascending=False)
        bu_perf['expense_label'] = bu_perf['actual_expenses'].apply(lambda x: f"{x/1e6:.1f}M")
        
        fig_bu = px.bar(bu_perf, x='area', y='actual_expenses', color='area', text='expense_label',
                        color_discrete_sequence=[GRUNENTAL_NAVY, GRUNENTAL_BLUE, GRUNENTAL_GREEN, 
                                                 GRUNENTAL_LIME, GRUNENTAL_TEAL, "#D1D5DB"])
        fig_bu.update_traces(textposition='outside', textfont=dict(size=11, color=GRUNENTAL_NAVY, family="Arial Black"),
                             cliponaxis=False, width=0.6)
        fig_bu.update_layout(xaxis_title="", yaxis_title="", bargap=0.1)
        st.plotly_chart(update_fig_layout(fig_bu, height=200), use_container_width=True, config={'displayModeBar': False})
    else:
        st.info("No data")

with row2_col3:
    st.markdown(f'<div class="section-header">📑 Top Cost Centers</div>', unsafe_allow_html=True)
    st.dataframe(get_highest_expenses(), hide_index=True, use_container_width=True, height=195)

# --- FOOTER ---
st.markdown(f"""
    <div class="minimal-footer">
        <div>GRUNENTAL GLOBAL CONTROLLING · ENGINE: POSTGRESQL + STREAMLIT + PLOTLY</div>
        <div>STRATEGIC INSIGHTS BY <span class="footer-author">DIEGO VALLEJO</span></div>
        <div>© 2024 · CORPORATE PERFORMANCE SYSTEM</div>
    </div>
""", unsafe_allow_html=True)
