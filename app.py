import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="Tea Sales Analysis",
    page_icon="🍵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CUSTOM CSS FOR A CLEANER LOOK
# --------------------------------------------------
st.markdown("""
    <style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E7D32;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .section-box {
        background-color: #F1F8E9;
        padding: 1.2rem 1.5rem;
        border-radius: 12px;
        border-left: 6px solid #66BB6A;
        margin-bottom: 1.2rem;
    }
    .section-box h3 {
        color: #2E7D32;
        margin-top: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# DEFAULT DATASET
# --------------------------------------------------
DEFAULT_DATA = {
    "Tea Type": [
        "Green Tea", "Black Tea", "Milk Tea",
        "Oolong Tea", "Chamomile Tea", "Matcha Tea"
    ],
    "Sales": [450, 600, 750, 350, 250, 550]
}

if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(DEFAULT_DATA)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown('<div class="main-title">🍵 Tea Shop Sales Analysis</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Enter your own sales figures below, '
    'then explore the interactive charts.</div>',
    unsafe_allow_html=True
)

# ==================================================
# 1. DATA INPUT SECTION (COMES FIRST!)
# ==================================================
st.markdown("## ✏️ Enter Your Tea Sales Data")

# Styled box using a native Streamlit container
with st.container(border=True):
    st.markdown(
        "<p style='color:#2E7D32; font-weight:600; margin-top:0;'>"
        "Type in the sales figure for each tea type. "
        "The charts below will update automatically."
        "</p>",
        unsafe_allow_html=True
    )

    tea_types = st.session_state.df["Tea Type"].tolist()
    cols = st.columns(3)

    new_sales = {}
    for i, tea in enumerate(tea_types):
        with cols[i % 3]:
            new_sales[tea] = st.number_input(
                f"**{tea}** sales",
                min_value=0,
                max_value=100000,
                value=int(st.session_state.df.loc[
                    st.session_state.df["Tea Type"] == tea, "Sales"
                ].values[0]),
                step=10,
                key=f"input_{tea}"
            )

# Update dataframe from inputs
st.session_state.df["Sales"] = st.session_state.df["Tea Type"].map(new_sales)
df = st.session_state.df.copy()

# --------------------------------------------------
# 2. SIDEBAR FILTERS
# --------------------------------------------------
st.sidebar.header("🔍 Filters")
st.sidebar.caption("Refine the charts below.")

selected_teas = st.sidebar.multiselect(
    "Select Tea Types",
    options=df["Tea Type"].tolist(),
    default=df["Tea Type"].tolist()
)

sales_filter = st.sidebar.slider(
    "Minimum Sales",
    min_value=0,
    max_value=int(max(df["Sales"].max(), 1)),
    value=0,
    step=10
)

# Apply filters
filtered_df = df[
    (df["Tea Type"].isin(selected_teas)) &
    (df["Sales"] >= sales_filter)
]

# Reset button
if st.sidebar.button("🔄 Reset to Default Data"):
    st.session_state.df = pd.DataFrame(DEFAULT_DATA)
    st.rerun()

# --------------------------------------------------
# 3. DATA TABLE
# --------------------------------------------------
st.markdown("## 📋 Your Tea Sales Data")

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Sales": st.column_config.ProgressColumn(
            "Sales",
            help="Sales volume",
            format="%d",
            min_value=0,
            max_value=int(max(df["Sales"].max(), 1))
        )
    }
)

# --------------------------------------------------
# 4. KPI METRICS
# --------------------------------------------------
st.markdown("## 📈 Sales Summary")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Tea Types Shown", len(filtered_df))

with col2:
    st.metric("Total Sales", f"{int(filtered_df['Sales'].sum()):,}")

with col3:
    if not filtered_df.empty:
        avg = filtered_df["Sales"].mean()
        st.metric("Average Sales", f"{avg:,.0f}")
    else:
        st.metric("Average Sales", "—")

with col4:
    if not filtered_df.empty:
        best = filtered_df.loc[filtered_df["Sales"].idxmax(), "Tea Type"]
        st.metric("Best Seller", best)
    else:
        st.metric("Best Seller", "—")

# --------------------------------------------------
# 5. CHARTS
# --------------------------------------------------
if filtered_df.empty:
    st.warning("⚠️ No data matches your filters. Please adjust them.")
else:
    # ----- BAR CHART -----
    st.markdown("## 📊 Bar Chart of Tea Sales")

    fig, ax = plt.subplots(figsize=(11, 5))

    # Color-code: best = green, worst = red, others = skyblue
    colors = []
    max_val = filtered_df["Sales"].max()
    min_val = filtered_df["Sales"].min()

    for val in filtered_df["Sales"]:
        if val == max_val and len(filtered_df) > 1:
            colors.append("#4CAF50")   # best -> green
        elif val == min_val and len(filtered_df) > 1:
            colors.append("#E53935")   # worst -> red
        else:
            colors.append("#64B5F6")   # normal -> blue

    bars = ax.bar(
        filtered_df["Tea Type"],
        filtered_df["Sales"],
        color=colors,
        edgecolor="white",
        linewidth=1.5
    )

    ax.set_xlabel("Tea Type", fontsize=12)
    ax.set_ylabel("Sales", fontsize=12)
    ax.set_title("Tea Sales Comparison", fontsize=14, fontweight="bold")
    ax.tick_params(axis="x", rotation=20)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    # Value labels
    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + max_val * 0.01,
            f"{int(h):,}",
            ha="center", va="bottom", fontsize=10, fontweight="bold"
        )

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#4CAF50", label="Best Seller"),
        Patch(facecolor="#E53935", label="Lowest Seller"),
        Patch(facecolor="#64B5F6", label="Other Teas"),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    plt.tight_layout()
    st.pyplot(fig)

    # ----- PIE CHART -----
    st.markdown("## 🥧 Pie Chart of Tea Sales Distribution")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        fig2, ax2 = plt.subplots(figsize=(7, 6))

        pie_colors = ["#FFB74D", "#4DB6AC", "#BA68C8",
                      "#F06292", "#81C784", "#64B5F6",
                      "#FFD54F", "#A1887F"]

        wedges, texts, autotexts = ax2.pie(
            filtered_df["Sales"],
            labels=filtered_df["Tea Type"],
            autopct="%1.1f%%",
            startangle=90,
            colors=pie_colors[:len(filtered_df)],
            wedgeprops={"edgecolor": "white", "linewidth": 2}
        )

        for t in autotexts:
            t.set_fontsize(10)
            t.set_fontweight("bold")

        ax2.set_title("Tea Sales Distribution",
                      fontsize=14, fontweight="bold")
        ax2.axis("equal")

        st.pyplot(fig2)

    with col_b:
        st.markdown("### 🏆 Best & Lowest Sellers")

        best_sale = filtered_df.loc[filtered_df["Sales"].idxmax()]
        worst_sale = filtered_df.loc[filtered_df["Sales"].idxmin()]

        st.success(
            f"**Best Seller:** {best_sale['Tea Type']} "
            f"— **{best_sale['Sales']:,}** units"
        )
        st.error(
            f"**Lowest Seller:** {worst_sale['Tea Type']} "
            f"— **{worst_sale['Sales']:,}** units"
        )

        st.info(
            f"**Total Sales:** {int(filtered_df['Sales'].sum()):,} units  \n"
            f"**Average per Tea:** "
            f"{filtered_df['Sales'].mean():,.0f} units"
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("Data Visualization — Dyah Alyana Sulaksono | 🍵 Tea Sales Analysis Dashboard")