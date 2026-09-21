import streamlit as st
import pandas as pd
import time
from fetchers import fetch_reddit_posts, fetch_serp_posts, PostItem
from utils.exporter import posts_to_dataframe, export_to_csv
from config import PLATFORM_DOMAINS, SERPER_API_KEY

# Page Config
st.set_page_config(
    page_title="NicheRadar - Social Intent & Lead Engine",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="auto"
)

# Custom Responsive CSS for Mobile & Desktop
st.markdown("""
<style>
    /* Dark glassmorphism background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
        overflow-x: hidden;
    }
    
    /* Responsive Header Typography */
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        line-height: 1.2;
    }

    .sub-header {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 1.2rem;
        line-height: 1.4;
    }
    
    /* Responsive Glassmorphism Cards */
    .lead-card {
        background: rgba(30, 41, 59, 0.75);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 1rem;
        margin-bottom: 0.8rem;
        word-wrap: break-word;
        word-break: break-word;
        overflow-wrap: anywhere;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .card-header-row {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
        margin-bottom: 8px;
    }
    
    /* Badges */
    .badge-high {
        background-color: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
    }

    .badge-medium {
        background-color: rgba(245, 158, 11, 0.2);
        color: #fde047;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
    }

    .badge-low {
        background-color: rgba(100, 116, 139, 0.2);
        color: #cbd5e1;
        border: 1px solid rgba(100, 116, 139, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        white-space: nowrap;
    }
    
    .platform-badge {
        background-color: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        white-space: nowrap;
    }

    /* Mobile Breakpoints & Responsive Tweaks */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.65rem !important;
        }
        .sub-header {
            font-size: 0.88rem !important;
            margin-bottom: 1rem !important;
        }
        .lead-card {
            padding: 0.85rem !important;
            border-radius: 10px !important;
        }
        .card-header-row {
            flex-direction: row;
            align-items: flex-start;
        }
        /* Touch target button spacing */
        .stButton button, .stDownloadButton button {
            min-height: 44px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown('<div class="main-header">NicheRadar 🎯</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Discover active social posts, questions, and leads in your target niche & location.</div>', unsafe_allow_html=True)

# Sidebar Controls
with st.sidebar:
    st.header("🔍 Radar Parameters")
    
    niche_input = st.text_input(
        "Niche / Industry", 
        value="Real Estate", 
        placeholder="e.g., Real Estate, Video Editor, Law Firm, Dentist, Tax"
    )
    
    location_input = st.text_input(
        "City / Country Location", 
        value="Miami", 
        placeholder="e.g., Miami, Dubai, London, New York, Toronto"
    )
    
    st.subheader("🌐 Target Platforms")
    selected_platforms = []
    for platform in ["Reddit", "LinkedIn", "Quora", "Twitter / X", "Web Forums"]:
        if st.checkbox(platform, value=(platform in ["Reddit", "LinkedIn", "Quora"])):
            selected_platforms.append(platform)
            
    st.subheader("⚙️ Settings & Lead Focus")
    lead_focus = st.selectbox(
        "🎯 Lead Focus Mode",
        ["❓ Questioning & Recommendations", "💼 Hiring & Job Offers", "🌐 All Discussions"],
        index=0
    )
    custom_keywords = st.text_input(
        "💬 Custom Query Keywords (Optional)",
        value="",
        placeholder="e.g. recommendation, best, looking for, cost"
    )
    time_filter = st.selectbox(
        "📅 Post Recency (How Old?)", 
        ["Past 24 Hours", "Past Week", "Past Month", "Anytime"],
        index=0
    )
    posts_per_platform = st.slider("Max Posts Per Platform", min_value=5, max_value=25, value=10)
    intent_filter = st.selectbox(
        "Intent Signal Filter", 
        ["All Signals", "🔥 High Intent Only", "⚡ Medium & High Intent"]
    )
    
    scan_button = st.button("Scan Radar 📡", type="primary", width="stretch")

    st.divider()
    if SERPER_API_KEY:
        st.caption("✅ **Serper API**: Configured (High Precision)")
    else:
        st.caption("ℹ️ **Engine Mode**: Free Public Endpoints & Fallback Scrapers")

# Session State for Posts
if "scanned_posts" not in st.session_state:
    st.session_state.scanned_posts = []

# Scan Action Trigger
if scan_button:
    if not niche_input.strip() or not location_input.strip():
        st.warning("Please enter both a Niche and a Location!")
    elif not selected_platforms:
        st.warning("Please select at least one platform to scan!")
    else:
        st.session_state.scanned_posts = []
        all_results: list[PostItem] = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_steps = len(selected_platforms)
        for idx, platform in enumerate(selected_platforms):
            status_text.markdown(f"🛰️ **Scanning {platform}** ({lead_focus}) for *{niche_input}* in *{location_input}*...")
            
            if platform == "Reddit":
                reddit_posts = fetch_reddit_posts(
                    niche_input, 
                    location_input, 
                    limit=posts_per_platform, 
                    time_filter=time_filter,
                    lead_focus=lead_focus,
                    custom_keywords=custom_keywords
                )
                all_results.extend(reddit_posts)
            else:
                serp_posts = fetch_serp_posts(
                    platform, 
                    niche_input, 
                    location_input, 
                    limit=posts_per_platform, 
                    time_filter=time_filter,
                    lead_focus=lead_focus,
                    custom_keywords=custom_keywords
                )
                all_results.extend(serp_posts)
                
            progress_bar.progress(int((idx + 1) / total_steps * 100))
            time.sleep(0.3)
            
        status_text.success(f"✅ Scanning Complete! Found {len(all_results)} social posts.")
        st.session_state.scanned_posts = all_results

# Filter Results
filtered_posts = st.session_state.scanned_posts
if intent_filter == "🔥 High Intent Only":
    filtered_posts = [p for p in filtered_posts if "High" in p.intent_score]
elif intent_filter == "⚡ Medium & High Intent":
    filtered_posts = [p for p in filtered_posts if "High" in p.intent_score or "Medium" in p.intent_score]

# Main Area Metrics & Results
if filtered_posts:
    # Responsive Metrics Layout (2x2 on Mobile, 4x1 on Desktop)
    m1, m2 = st.columns(2)
    m3, m4 = st.columns(2)
    
    with m1:
        st.metric("Total Posts", len(filtered_posts))
    with m2:
        high_count = sum(1 for p in filtered_posts if "High" in p.intent_score)
        st.metric("High Intent Leads 🔥", high_count)
    with m3:
        st.metric("Active Niche", niche_input)
    with m4:
        st.metric("Target Location", location_input)
        
    st.divider()
    
    tab1, tab2, tab3 = st.tabs(["📌 Post Feed", "📊 Data Table", "✍️ AI Outreach Helper"])
    
    # Tab 1: Post Cards Feed
    with tab1:
        for p in filtered_posts:
            badge_class = "badge-high" if "High" in p.intent_score else ("badge-medium" if "Medium" in p.intent_score else "badge-low")
            
            with st.container():
                st.markdown(f"""
                <div class="lead-card">
                    <div class="card-header-row">
                        <div>
                            <span class="platform-badge">{p.platform}</span>
                            <span style="color: #94a3b8; font-size: 0.8rem; margin-left: 8px;">📅 {p.published_date}</span>
                        </div>
                        <span class="{badge_class}">{p.intent_score}</span>
                    </div>
                    <h4 style="margin: 6px 0; color: #f8fafc; font-size: 1.05rem; line-height: 1.35;">{p.title}</h4>
                    <p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.45; margin-bottom: 8px;">{p.snippet if p.snippet else "No preview snippet available."}</p>
                    <div style="margin-top: 6px;">
                        <span style="color: #818cf8; font-size: 0.78rem; font-weight: 600;">Keywords: </span>
                        <span style="color: #94a3b8; font-size: 0.78rem;">{", ".join(p.matched_keywords) if p.matched_keywords else "Niche context match"}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mobile-Optimized Action Row
                btn_col, link_col = st.columns([1, 1])
                with btn_col:
                    st.link_button("Open Post Link 🔗", p.url, width="stretch")
                with link_col:
                    st.caption(f"URL: `{p.url}`")
                st.write("")
                
    # Tab 2: Data Table View
    with tab2:
        df = posts_to_dataframe(filtered_posts)
        st.dataframe(df, width="stretch", hide_index=True)
        
        csv_data = export_to_csv(filtered_posts)
        st.download_button(
            label="📥 Export Leads to CSV",
            data=csv_data,
            file_name=f"nicheradar_{niche_input.lower().replace(' ', '_')}_{location_input.lower()}.csv",
            mime="text/csv",
            width="stretch"
        )
        
    # Tab 3: AI Outreach Helper
    with tab3:
        st.subheader("💡 Outreach Response Draft Generator")
        st.caption("Select a lead post below to generate a professional outreach response template.")
        
        post_titles = [f"[{p.platform}] {p.title}" for p in filtered_posts]
        selected_index = st.selectbox("Select Target Post", range(len(post_titles)), format_func=lambda i: post_titles[i])
        
        if selected_index is not None and selected_index < len(filtered_posts):
            target_post = filtered_posts[selected_index]
            
            st.markdown(f"**Target Title**: `{target_post.title}`")
            st.markdown(f"**Platform**: `{target_post.platform}` | **Link**: [{target_post.url}]({target_post.url})")
            
            pitch_template = f"""Hi there! 👋

Saw your post regarding {target_post.niche or niche_input} in {target_post.location or location_input}. 

If you're still looking for help or recommendations, I specialize in {niche_input} services around {location_input}. 

Feel free to check out my profile or DM me directly if you have any questions—happy to share some quick guidance or point you in the right direction!

Best regards,"""
            
            st.text_area("Generated Outreach Pitch Template (Copy & Edit):", value=pitch_template, height=180)
            st.info("💡 **Tip**: Personalize the response based on the post details before replying on the target platform.")

elif not scan_button:
    st.info("👈 Set your target **Niche**, **City/Location**, and click **Scan Radar 📡** to discover active post links.")
