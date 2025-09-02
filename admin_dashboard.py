# admin_dashboard.py - SUPER OPTIMIZED VERSION WITH PASSWORD PROTECTION
"""
AI Survey Admin Dashboard - LIGHTNING FAST VERSION WITH SECURITY
Run this separately from your main app with password protection
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime, timedelta
import json
from database import create_database, AdminUtils
import plotly.express as px
import plotly.graph_objects as go
import math
import time
import hashlib

# Page configuration
st.set_page_config(
    page_title="Survey Admin Dashboard", 
    layout="wide",
    page_icon="📊"
)

# ==========================================
# PASSWORD AUTHENTICATION
# ==========================================

# Admin password (in production, use environment variables or secure config)
ADMIN_PASSWORD_HASH = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"  # "password" hashed
# To generate a new hash: hashlib.sha256("your_password".encode()).hexdigest()

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password():
    """Check if the user has entered the correct password"""
    
    # Initialize session state for authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.password_attempts = 0
        st.session_state.last_attempt_time = None
    
    # If already authenticated, return True
    if st.session_state.authenticated:
        return True
    
    # Check for rate limiting (max 5 attempts per 10 minutes)
    if (st.session_state.password_attempts >= 5 and 
        st.session_state.last_attempt_time and
        datetime.now() - st.session_state.last_attempt_time < timedelta(minutes=10)):
        
        remaining_time = timedelta(minutes=10) - (datetime.now() - st.session_state.last_attempt_time)
        st.error(f"🔒 Too many failed attempts. Try again in {remaining_time.seconds // 60} minutes.")
        return False
    
    # Show login form
    st.markdown("""
        <div style="max-width: 400px; margin: 0 auto; padding: 2rem; background: #f8f9fa; border-radius: 10px; margin-top: 2rem;">
            <h2 style="text-align: center; color: #1f77b4;">🔐 Admin Access</h2>
            <p style="text-align: center; color: #666;">Enter the admin password to access the dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create centered columns for the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Password input
        password = st.text_input(
            "Password:",
            type="password",
            placeholder="Enter admin password",
            key="password_input"
        )
        
        # Login button
        if st.button("🔓 Login", type="primary", use_container_width=True):
            if password:
                if hash_password(password) == ADMIN_PASSWORD_HASH:
                    st.session_state.authenticated = True
                    st.session_state.password_attempts = 0
                    st.success("✅ Access granted! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.password_attempts += 1
                    st.session_state.last_attempt_time = datetime.now()
                    st.error(f"❌ Invalid password. Attempt {st.session_state.password_attempts}/5")
            else:
                st.warning("⚠️ Please enter a password")
        
        # Show attempt counter if there have been failed attempts
        if st.session_state.password_attempts > 0:
            st.caption(f"Failed attempts: {st.session_state.password_attempts}/5")
    
    # Instructions for first-time users
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: #666; font-size: 14px;">
            <p><strong>Admin Password:</strong> plasticsurgeryadmin</p>
            <p><em>Change this in the code by updating ADMIN_PASSWORD_HASH</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    return False

# Authentication check - stop here if not authenticated
if not check_password():
    st.stop()

# Add logout option in sidebar after authentication
with st.sidebar:
    st.markdown("---")
    if st.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.password_attempts = 0
        st.rerun()
    
    # Show authenticated user info
    st.success("🔓 Authenticated")
    st.caption(f"Session: {datetime.now().strftime('%H:%M:%S')}")

# ==========================================
# SUPER AGGRESSIVE CACHING
# ==========================================

# Initialize session state for data persistence
if 'cached_data' not in st.session_state:
    st.session_state.cached_data = {}
    st.session_state.cache_timestamps = {}

def get_cache_key(func_name):
    """Generate cache key"""
    return f"{func_name}_{datetime.now().minute // 2}"  # Cache for 2-minute windows

def is_cache_valid(func_name, ttl_seconds=60):
    """Check if cache is still valid"""
    cache_key = f"{func_name}_timestamp"
    if cache_key not in st.session_state.cache_timestamps:
        return False
    
    age = time.time() - st.session_state.cache_timestamps[cache_key]
    return age < ttl_seconds

def get_cached_data(func_name, fetch_function, ttl_seconds=60):
    """Generic caching function"""
    if is_cache_valid(func_name, ttl_seconds):
        if func_name in st.session_state.cached_data:
            return st.session_state.cached_data[func_name]
    
    # Fetch fresh data
    data = fetch_function()
    st.session_state.cached_data[func_name] = data
    st.session_state.cache_timestamps[f"{func_name}_timestamp"] = time.time()
    return data

def clear_cache():
    """Clear all cached data"""
    st.session_state.cached_data = {}
    st.session_state.cache_timestamps = {}

# Cache database connection
@st.cache_resource
def get_db():
    """Get cached database connection"""
    return create_database()

# Super fast stats function
def fetch_stats():
    """Fetch stats - optimized"""
    db = get_db()
    return db.get_assignment_stats()

def fetch_progress():
    """Fetch progress - optimized"""
    db = get_db()
    return db.get_study_progress()

def fetch_export_data():
    """Fetch export data - optimized"""
    db = get_db()
    return db.export_data()

# ==========================================
# MINIMAL CSS
# ==========================================
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stMetric { padding: 0.5rem; }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>📊 AI Survey Admin Dashboard</h1>
        <p>Lightning Fast Performance - Secure Access</p>
    </div>
    """, unsafe_allow_html=True)

# Check database
if not os.path.exists('survey_data.db'):
    st.error("❌ Database not found!")
    st.stop()

# Initialize
try:
    db = get_db()
except Exception as e:
    st.error(f"❌ Database error: {e}")
    st.stop()

# Sidebar
st.sidebar.title("🧭 Navigation")

# Performance controls
if st.sidebar.button("🔄 Force Refresh"):
    clear_cache()
    st.rerun()

# Show cache status
cache_count = len(st.session_state.cached_data)
st.sidebar.caption(f"📦 Cached items: {cache_count}")

page = st.sidebar.selectbox("Choose a page:", [
    "📈 Dashboard",
    "⚙️ Management", 
    "👥 Participants",
    "💬 Responses",
    "📊 Analytics",
    "📤 Export",
    "🗑️ Danger Zone"
])

# ==========================================
# PAGE 1: DASHBOARD (SUPER FAST)
# ==========================================

if page == "📈 Dashboard":
    # Use aggressive caching
    with st.spinner("Loading dashboard..."):
        stats = get_cached_data("stats", fetch_stats, 30)  # 30-second cache
        progress = get_cached_data("progress", fetch_progress, 30)
    
    # Status
    if stats['study_active']:
        st.success("🟢 ACTIVE")
    else:
        st.warning("🟡 PAUSED")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total", stats['total_participants'], f"/{stats['target_participants']}")
    
    with col2:
        st.metric("Control", stats['control_count'])
    
    with col3:
        st.metric("Warning", stats['warning_count'])
    
    with col4:
        st.metric("Balance", f"±{stats['balance_difference']}")
    
    # Progress
    progress_pct = min(progress['progress_percentage'], 100) / 100
    st.progress(progress_pct)
    st.write(f"**{progress['current_total']} / {progress['target_total']} participants** ({progress['progress_percentage']:.1f}%)")
    
    # Quick actions
    if st.button("📤 Export"):
        with st.spinner("Exporting..."):
            participants_df, responses_df = fetch_export_data()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            p_file = f"participants_{timestamp}.csv"
            r_file = f"responses_{timestamp}.csv"
            
            participants_df.to_csv(p_file, index=False)
            responses_df.to_csv(r_file, index=False)
            
            st.success(f"✅ Exported: {p_file}, {r_file}")

# ==========================================
# PAGE 2: MANAGEMENT (FAST)
# ==========================================

elif page == "⚙️ Management":
    st.markdown("## ⚙️ Study Management")
    
    # Get fresh data for management operations
    stats = get_cached_data("stats", fetch_stats, 10)  # 10-second cache for management
    current_target = db.get_target_participants()
    current_active = db.is_study_active()
    current_participants = stats['total_participants']
    
    # Status control
    st.markdown("### 🔘 Study Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_active = st.toggle("Study Active", value=current_active)
        
        if new_active != current_active:
            if st.button("💾 Update Status"):
                db.set_study_active(new_active)
                clear_cache()
                st.success(f"✅ Status: {'ACTIVE' if new_active else 'PAUSED'}")
                st.rerun()
    
    with col2:
        if current_active:
            st.success("🟢 ACTIVE")
        else:
            st.warning("🟡 PAUSED")
    
    # Target management
    st.markdown("### 🎯 Target Management")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_target = st.number_input(
            "Participant Target:",
            min_value=2,
            max_value=1000,
            value=current_target,
            step=2
        )
        
        if new_target != current_target:
            control_target = math.ceil(new_target / 2)
            warning_target = new_target // 2
            
            st.info(f"New split: Control={control_target}, Warning={warning_target}")
    
    with col2:
        if new_target != current_target:
            if st.button("🎯 Update", type="primary"):
                db.set_target_participants(new_target)
                clear_cache()
                st.success(f"✅ Target: {new_target}")
                st.rerun()
    
    # Current allocation
    st.markdown("### 📊 Current Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Control", stats['control_count'])
        control_target = math.ceil(current_target / 2)
        control_progress = (stats['control_count'] / control_target) if control_target > 0 else 0
        st.progress(min(control_progress, 1.0))
    
    with col2:
        st.metric("Warning", stats['warning_count'])
        warning_target = current_target // 2
        warning_progress = (stats['warning_count'] / warning_target) if warning_target > 0 else 0
        st.progress(min(warning_progress, 1.0))
    
    with col3:
        balance = stats['balance_difference']
        st.metric("Balance", f"±{balance}")
        if balance <= 1:
            st.success("✅ Balanced")
        else:
            st.warning("⚠️ Imbalanced")

# ==========================================
# PAGE 3: PARTICIPANTS (ENHANCED)
# ==========================================

elif page == "👥 Participants":
    st.markdown("## 👥 Participants Management")
    
    # Get cached data
    participants_df, _ = get_cached_data("export_data", fetch_export_data, 60)
    
    if participants_df.empty:
        st.info("No participants yet.")
    else:
        # Enhanced filtering
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            condition_filter = st.selectbox(
                "Filter by condition:",
                ["All", "Control", "Group A - Warning Label"]
            )
        
        with filter_col2:
            status_filter = st.selectbox(
                "Filter by status:",
                ["All", "Completed", "In Progress"]
            )
        
        with filter_col3:
            show_all = st.toggle("Show All Records", value=False, help="Show all records instead of recent 50")
        
        # Apply filters efficiently
        filtered_df = participants_df.copy()
        
        if condition_filter != "All":
            filtered_df = filtered_df[filtered_df['condition'] == condition_filter]
        
        if status_filter == "Completed":
            filtered_df = filtered_df[filtered_df['completed'] == True]
        elif status_filter == "In Progress":
            filtered_df = filtered_df[filtered_df['completed'] == False]
        
        # Display summary metrics
        st.markdown("### 📊 Summary")
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("Total Shown", len(filtered_df))
        
        with summary_col2:
            completed_count = len(filtered_df[filtered_df['completed'] == True])
            st.metric("Completed", completed_count)
        
        with summary_col3:
            if len(filtered_df) > 0:
                completion_rate = (completed_count / len(filtered_df) * 100)
                st.metric("Completion Rate", f"{completion_rate:.1f}%")
        
        with summary_col4:
            if len(filtered_df) > 0:
                avg_age = filtered_df['age'].mean()
                st.metric("Avg Age", f"{avg_age:.1f}" if not pd.isna(avg_age) else "N/A")
        
        # Display data with performance optimization
        st.markdown(f"### Showing {len(filtered_df)} participants")
        
        # Limit display for performance unless "Show All" is enabled
        display_df = filtered_df.copy()
        if not show_all and len(display_df) > 50:
            display_df = display_df.tail(50)  # Show most recent 50
            st.info(f"Showing most recent 50 of {len(filtered_df)} participants. Toggle 'Show All Records' to see everything.")
        
        # Format the dataframe for better display
        display_df['completed'] = display_df['completed'].map({True: "✅ Yes", False: "⏳ No"})
        display_df['assigned_at'] = pd.to_datetime(display_df['assigned_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "id": "ID",
                "condition": "Condition", 
                "age": "Age",
                "profession": "Profession",
                "completed": "Status",
                "assigned_at": "Joined"
            }
        )
        
        # Additional insights
        if len(filtered_df) > 0:
            st.markdown("### 🔍 Additional Insights")
            
            insights_col1, insights_col2 = st.columns(2)
            
            with insights_col1:
                # Profession breakdown
                if 'profession' in filtered_df.columns:
                    profession_counts = filtered_df['profession'].value_counts().head(5)
                    if not profession_counts.empty:
                        st.markdown("**Top Professions:**")
                        for prof, count in profession_counts.items():
                            if pd.notna(prof):
                                st.write(f"- {prof}: {count}")
            
            with insights_col2:
                # Recent activity
                if 'assigned_at' in filtered_df.columns:
                    recent_24h = filtered_df[
                        pd.to_datetime(filtered_df['assigned_at']) > 
                        (datetime.now() - timedelta(hours=24))
                    ]
                    st.metric("Joined Last 24h", len(recent_24h))
                    
                    recent_week = filtered_df[
                        pd.to_datetime(filtered_df['assigned_at']) > 
                        (datetime.now() - timedelta(days=7))
                    ]
                    st.metric("Joined Last Week", len(recent_week))

# ==========================================
# PAGE 4: RESPONSES (ENHANCED)
# ==========================================

elif page == "💬 Responses":
    st.markdown("## 💬 Responses Analysis")
    
    # Get cached data
    participants_df, responses_df = get_cached_data("export_data", fetch_export_data, 60)
    
    if responses_df.empty:
        st.info("No responses yet.")
    else:
        # Response overview
        st.markdown(f"### 📊 Total Responses: {len(responses_df)}")
        
        # Enhanced filters
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            condition_filter = st.selectbox(
                "Filter by condition:",
                ["All"] + list(responses_df['group_condition'].unique())
            )
        
        with filter_col2:
            rating_filter = st.selectbox(
                "Filter by agreement:",
                ["All"] + sorted(list(responses_df['agree_rating'].unique()))
            )
        
        with filter_col3:
            trust_filter = st.selectbox(
                "Filter by trust:",
                ["All", "Would Trust", "Would Not Trust"]
            )
        
        with filter_col4:
            show_all_responses = st.toggle("Show All Responses", value=False)
        
        # Apply filters
        filtered_responses = responses_df.copy()
        
        if condition_filter != "All":
            filtered_responses = filtered_responses[filtered_responses['group_condition'] == condition_filter]
        
        if rating_filter != "All":
            filtered_responses = filtered_responses[filtered_responses['agree_rating'] == rating_filter]
        
        if trust_filter == "Would Trust":
            filtered_responses = filtered_responses[filtered_responses['trust_rating'] == 'Yes']
        elif trust_filter == "Would Not Trust":
            filtered_responses = filtered_responses[filtered_responses['trust_rating'] == 'No']
        
        # Display summary metrics
        st.markdown("### 📊 Filtered Summary")
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            st.metric("Shown", len(filtered_responses))
        
        with summary_col2:
            trust_yes = len(filtered_responses[filtered_responses['trust_rating'] == 'Yes'])
            st.metric("Would Trust", trust_yes)
        
        with summary_col3:
            trust_no = len(filtered_responses[filtered_responses['trust_rating'] == 'No'])
            st.metric("Would Not Trust", trust_no)
        
        with summary_col4:
            if len(filtered_responses) > 0:
                trust_rate = (trust_yes / len(filtered_responses) * 100)
                st.metric("Trust Rate", f"{trust_rate:.1f}%")
        
        # Display responses with performance optimization
        st.markdown(f"### Showing {len(filtered_responses)} responses")
        
        # Limit display for performance
        display_responses = filtered_responses.copy()
        if not show_all_responses and len(display_responses) > 100:
            display_responses = display_responses.tail(100)  # Show most recent 100
            st.info(f"Showing most recent 100 of {len(filtered_responses)} responses. Toggle 'Show All Responses' to see everything.")
        
        # Format for display
        display_responses['trust_rating'] = display_responses['trust_rating'].map({
            'Yes': "✅ Yes", 
            'No': "❌ No",
            True: "✅ Yes",
            False: "❌ No"
        })
        display_responses['submitted_at'] = pd.to_datetime(display_responses['submitted_at']).dt.strftime('%Y-%m-%d %H:%M')
        
        # Sort by most recent first
        display_responses = display_responses.sort_values('submitted_at', ascending=False)
        
        st.dataframe(
            display_responses[['participant_id', 'case_id', 'group_condition', 'agree_rating', 'trust_rating', 'comment', 'submitted_at']],
            use_container_width=True,
            column_config={
                "participant_id": "P.ID",
                "case_id": "Case",
                "group_condition": "Condition",
                "agree_rating": "Agreement",
                "trust_rating": "Trust",
                "comment": "Comment",
                "submitted_at": "Submitted"
            }
        )
        
        # Response insights
        if len(filtered_responses) > 0:
            st.markdown("### 📈 Response Insights")
            
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                # Agreement distribution
                agreement_dist = filtered_responses['agree_rating'].value_counts()
                st.markdown("**Agreement Distribution:**")
                for rating, count in agreement_dist.items():
                    percentage = (count / len(filtered_responses) * 100)
                    st.write(f"- {rating}: {count} ({percentage:.1f}%)")
            
            with insight_col2:
                # Trust by condition
                if len(filtered_responses['group_condition'].unique()) > 1:
                    trust_by_condition = filtered_responses.groupby(['group_condition', 'trust_rating']).size().unstack(fill_value=0)
                    
                    st.markdown("**Trust by Condition:**")
                    for condition in trust_by_condition.index:
                        yes_count = trust_by_condition.loc[condition, 'Yes'] if 'Yes' in trust_by_condition.columns else 0
                        total = trust_by_condition.loc[condition].sum()
                        trust_pct = (yes_count / total * 100) if total > 0 else 0
                        st.write(f"- {condition}: {trust_pct:.1f}% trust")
            
            # Recent activity chart
            if len(filtered_responses) > 5:
                st.markdown("### 📊 Response Timeline")
                
                # Create timeline chart
                timeline_df = filtered_responses.copy()
                timeline_df['submitted_date'] = pd.to_datetime(timeline_df['submitted_at']).dt.date
                timeline_counts = timeline_df.groupby(['submitted_date', 'group_condition']).size().reset_index(name='count')
                
                if not timeline_counts.empty:
                    fig_timeline = px.bar(
                        timeline_counts,
                        x='submitted_date',
                        y='count',
                        color='group_condition',
                        title="Daily Response Count by Condition",
                        barmode='group'
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)

# ==========================================
# PAGE 5: ANALYTICS (FULL FEATURED)
# ==========================================

elif page == "📊 Analytics":
    st.markdown("## 📊 Data Analytics")
    
    # Get cached data
    participants_df, responses_df = get_cached_data("export_data", fetch_export_data, 120)  # 2-minute cache
    
    if participants_df.empty:
        st.info("No data to analyze yet.")
    else:
        # Condition distribution chart
        st.markdown("### 📈 Participant Distribution")
        condition_counts = participants_df['condition'].value_counts()
        
        fig_conditions = px.pie(
            values=condition_counts.values,
            names=condition_counts.index,
            title="Participants by Condition"
        )
        st.plotly_chart(fig_conditions, use_container_width=True)
        
        if not responses_df.empty:
            # Convert Likert scale ratings to numerical values for analysis
            likert_mapping = {
                "1 Strongly Disagree": 1,
                "2 Disagree": 2, 
                "3 Neutral": 3,
                "4 Agree": 4,
                "5 Strongly Agree": 5
            }
            
            # Add numerical agreement scores
            responses_df['agree_numeric'] = responses_df['agree_rating'].map(likert_mapping)
            
            # Remove any unmapped values
            analysis_df = responses_df.dropna(subset=['agree_numeric'])
            
            if not analysis_df.empty:
                # ========================
                # LIKERT SCALE ANALYSIS
                # ========================
                
                st.markdown("### 📊 Likert Scale Analysis")
                
                # Calculate descriptive statistics by condition
                stats_by_condition = analysis_df.groupby('group_condition')['agree_numeric'].agg([
                    'mean', 'median', 'count'
                ]).round(2)
                
                # Calculate mode separately (since it can return multiple values)
                def get_mode(series):
                    mode_result = series.mode()
                    if len(mode_result) > 0:
                        return mode_result.iloc[0]
                    return None
                
                mode_by_condition = analysis_df.groupby('group_condition')['agree_numeric'].apply(get_mode)
                stats_by_condition['mode'] = mode_by_condition
                
                # Display statistics table
                st.markdown("#### 📋 Descriptive Statistics by Condition")
                
                # Format the statistics table for better display
                display_stats = stats_by_condition.copy()
                display_stats.columns = ['Mean', 'Median', 'Count', 'Mode']
                display_stats = display_stats.round(2)
                
                st.dataframe(
                    display_stats,
                    use_container_width=True,
                    column_config={
                        "Mean": st.column_config.NumberColumn("Mean", format="%.2f"),
                        "Median": st.column_config.NumberColumn("Median", format="%.1f"),
                        "Count": st.column_config.NumberColumn("Count", format="%d"),
                        "Mode": st.column_config.NumberColumn("Mode", format="%.0f")
                    }
                )
                
                # ========================
                # AVERAGE LIKERT SCALE GRAPH
                # ========================
                
                st.markdown("#### 📈 Average Likert Scale by Condition")
                
                # Create bar chart of means
                mean_data = stats_by_condition['mean'].reset_index()
                mean_data.columns = ['Condition', 'Mean_Agreement']
                
                fig_means = px.bar(
                    mean_data,
                    x='Condition',
                    y='Mean_Agreement',
                    title="Average Agreement Rating by Condition",
                    color='Condition',
                    text='Mean_Agreement'
                )
                
                fig_means.update_traces(
                    texttemplate='%{text:.2f}', 
                    textposition='outside'
                )
                
                fig_means.update_layout(
                    yaxis=dict(range=[1, 5], title="Average Agreement (1-5 Scale)"),
                    xaxis_title="Condition",
                    showlegend=False
                )
                
                # Add reference lines for scale interpretation
                fig_means.add_hline(y=3, line_dash="dash", line_color="gray", 
                                   annotation_text="Neutral (3.0)")
                
                st.plotly_chart(fig_means, use_container_width=True)
                
                # ========================
                # DISTRIBUTION COMPARISON
                # ========================
                
                st.markdown("#### 📊 Distribution Comparison")
                
                # Create box plot for distribution comparison
                fig_box = px.box(
                    analysis_df,
                    x='group_condition',
                    y='agree_numeric',
                    title="Agreement Rating Distribution by Condition",
                    points="all"
                )
                
                fig_box.update_layout(
                    yaxis=dict(range=[0.5, 5.5], title="Agreement Rating (1-5 Scale)"),
                    xaxis_title="Condition"
                )
                
                st.plotly_chart(fig_box, use_container_width=True)
                
                # ========================
                # STATISTICAL TESTS
                # ========================
                
                # Check if scipy is available
                try:
                    from scipy import stats as scipy_stats
                    SCIPY_AVAILABLE = True
                except ImportError:
                    SCIPY_AVAILABLE = False
                
                if SCIPY_AVAILABLE:
                    st.markdown("### 🧮 Statistical Tests")
                    
                    # Get unique conditions
                    conditions = analysis_df['group_condition'].unique()
                    
                    if len(conditions) >= 2:
                        # Prepare data for Mann-Whitney U test
                        condition1 = conditions[0]
                        condition2 = conditions[1]
                        
                        group1_data = analysis_df[analysis_df['group_condition'] == condition1]['agree_numeric']
                        group2_data = analysis_df[analysis_df['group_condition'] == condition2]['agree_numeric']
                        
                        # Display sample sizes
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric(f"{condition1} Sample Size", len(group1_data))
                        with col2:
                            st.metric(f"{condition2} Sample Size", len(group2_data))
                        
                        # Mann-Whitney U Test
                        st.markdown("#### 🔍 Mann-Whitney U Test")
                        
                        try:
                            # Perform the test
                            statistic, p_value = scipy_stats.mannwhitneyu(
                                group1_data, group2_data, 
                                alternative='two-sided'
                            )
                            
                            # Effect size (rank-biserial correlation)
                            n1, n2 = len(group1_data), len(group2_data)
                            effect_size = 1 - (2 * statistic) / (n1 * n2)
                            
                            # Display results
                            test_col1, test_col2, test_col3 = st.columns(3)
                            
                            with test_col1:
                                st.metric("U Statistic", f"{statistic:.2f}")
                            
                            with test_col2:
                                st.metric("P-value", f"{p_value:.4f}")
                            
                            with test_col3:
                                st.metric("Effect Size (r)", f"{effect_size:.3f}")
                            
                            # Interpretation
                            st.markdown("#### 📝 Test Interpretation")
                            
                            # Significance interpretation
                            if p_value < 0.001:
                                significance = "highly significant (p < 0.001)"
                            elif p_value < 0.01:
                                significance = "very significant (p < 0.01)"
                            elif p_value < 0.05:
                                significance = "significant (p < 0.05)"
                            else:
                                significance = "not significant (p ≥ 0.05)"
                            
                            # Effect size interpretation
                            abs_effect = abs(effect_size)
                            if abs_effect < 0.1:
                                effect_interpretation = "negligible"
                            elif abs_effect < 0.3:
                                effect_interpretation = "small"
                            elif abs_effect < 0.5:
                                effect_interpretation = "medium"
                            else:
                                effect_interpretation = "large"
                            
                            st.markdown(f"""
                            **Results Summary:**
                            - The difference between conditions is **{significance}**
                            - Effect size is **{effect_interpretation}** (r = {effect_size:.3f})
                            - {condition1} median: {group1_data.median():.1f}
                            - {condition2} median: {group2_data.median():.1f}
                            """)
                            
                            # Additional context
                            if p_value < 0.05:
                                st.success("✅ There is a statistically significant difference between conditions")
                            else:
                                st.info("ℹ️ No statistically significant difference detected between conditions")
                            
                        except Exception as e:
                            st.error(f"Statistical test error: {e}")
                    
                    else:
                        st.warning("⚠️ Need at least 2 conditions for statistical comparison")
                
                else:
                    st.warning("📦 Install scipy for statistical tests: pip install scipy")
                
                # ========================
                # ADDITIONAL ANALYSIS CHARTS
                # ========================
                
                st.markdown("---")
                st.markdown("### 📊 Additional Analysis")
                
                # Agreement ratings by condition (original)
                st.markdown("#### 🎯 Agreement Ratings Distribution")
                
                agreement_data = responses_df.groupby(['group_condition', 'agree_rating']).size().reset_index(name='count')
                
                fig_agreement = px.bar(
                    agreement_data,
                    x='agree_rating',
                    y='count',
                    color='group_condition',
                    title="Agreement Ratings Distribution by Condition",
                    barmode='group'
                )
                st.plotly_chart(fig_agreement, use_container_width=True)
                
                # Trust ratings by condition
                st.markdown("#### 🤝 Trust by Condition")
                
                # Count Yes/No responses by condition
                trust_counts = responses_df.groupby(['group_condition', 'trust_rating']).size().reset_index(name='count')
                
                # Calculate percentages
                trust_totals = responses_df.groupby('group_condition').size().reset_index(name='total')
                trust_counts = trust_counts.merge(trust_totals, on='group_condition')
                trust_counts['percentage'] = (trust_counts['count'] / trust_counts['total']) * 100
                
                # Create the trust visualization
                fig_trust = px.bar(
                    trust_counts,
                    x='group_condition',
                    y='count',
                    color='trust_rating',
                    title="Trust Responses by Condition (Count)",
                    text='count',
                    barmode='group'
                )
                fig_trust.update_traces(texttemplate='%{text}', textposition='outside')
                fig_trust.update_layout(
                    xaxis_title="Condition",
                    yaxis_title="Number of Responses",
                    legend_title="Would Follow Recommendation"
                )
                st.plotly_chart(fig_trust, use_container_width=True)
                
                # Also show percentage breakdown
                st.markdown("#### 📊 Trust Percentage Breakdown")
                
                # Calculate just the "Yes" percentages for summary
                yes_percentages = trust_counts[trust_counts['trust_rating'] == 'Yes'].copy()
                
                if not yes_percentages.empty:
                    fig_trust_pct = px.bar(
                        yes_percentages,
                        x='group_condition',
                        y='percentage',
                        title="Percentage Who Would Follow Recommendation",
                        text='percentage',
                        color='group_condition'
                    )
                    fig_trust_pct.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                    fig_trust_pct.update_layout(
                        xaxis_title="Condition",
                        yaxis_title="Percentage (%)",
                        showlegend=False,
                        yaxis=dict(range=[0, 100])
                    )
                    st.plotly_chart(fig_trust_pct, use_container_width=True)
                    
                    # Display summary table
                    trust_summary = responses_df.groupby('group_condition')['trust_rating'].agg(['count', lambda x: (x == 'Yes').sum()]).reset_index()
                    trust_summary.columns = ['Condition', 'Total_Responses', 'Would_Trust']
                    trust_summary['Would_Not_Trust'] = trust_summary['Total_Responses'] - trust_summary['Would_Trust']
                    trust_summary['Trust_Percentage'] = (trust_summary['Would_Trust'] / trust_summary['Total_Responses'] * 100).round(1)
                    
                    st.markdown("**Trust Summary Table:**")
                    st.dataframe(
                        trust_summary,
                        use_container_width=True,
                        column_config={
                            "Condition": "Condition",
                            "Total_Responses": "Total Responses",
                            "Would_Trust": "Would Trust (Yes)",
                            "Would_Not_Trust": "Would Not Trust (No)", 
                            "Trust_Percentage": st.column_config.NumberColumn("Trust %", format="%.1f%%")
                        }
                    )
                
                else:
                    st.info("No 'Yes' responses found in trust data")

# ==========================================
# PAGE 6: EXPORT (MINIMAL)
# ==========================================

elif page == "📤 Export":
    st.markdown("## 📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📁 Export All Data", type="primary"):
            with st.spinner("Exporting..."):
                try:
                    participants_df, responses_df = fetch_export_data()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    p_file = f"survey_participants_{timestamp}.csv"
                    r_file = f"survey_responses_{timestamp}.csv"
                    
                    participants_df.to_csv(p_file, index=False)
                    responses_df.to_csv(r_file, index=False)
                    
                    st.success(f"✅ Exported:")
                    st.write(f"- {p_file}")
                    st.write(f"- {r_file}")
                except Exception as e:
                    st.error(f"Export failed: {e}")
    
    with col2:
        try:
            participants_df, responses_df = get_cached_data("export_data", fetch_export_data, 60)
            
            st.markdown("### Summary")
            st.write(f"**Participants:** {len(participants_df)}")
            st.write(f"**Responses:** {len(responses_df)}")
            
            if not participants_df.empty:
                conditions = participants_df['condition'].value_counts()
                st.write("**By condition:**")
                for condition, count in conditions.items():
                    st.write(f"- {condition}: {count}")
        except Exception as e:
            st.error(f"Summary error: {e}")

# ==========================================
# PAGE 7: DANGER ZONE (MINIMAL)
# ==========================================

elif page == "🗑️ Danger Zone":
    st.markdown("## ⚠️ Danger Zone")
    
    st.markdown("""
        <div style="background-color:#fff5f5;border:2px solid #e53e3e;border-radius:8px;padding:1rem;">
            <h3>🚨 Warning</h3>
            <p>These actions permanently delete data!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick backup
    if st.button("📦 Create Backup"):
        with st.spinner("Creating backup..."):
            try:
                participants_df, responses_df = fetch_export_data()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                p_backup = f"backup_participants_{timestamp}.csv"
                r_backup = f"backup_responses_{timestamp}.csv"
                
                participants_df.to_csv(p_backup, index=False)
                responses_df.to_csv(r_backup, index=False)
                
                st.success(f"✅ Backup: {p_backup}, {r_backup}")
            except Exception as e:
                st.error(f"Backup failed: {e}")
    
    st.markdown("---")
    
    # Nuclear option
    st.markdown("### 💣 Clear ALL Data")
    
    confirm1 = st.checkbox("⚠️ I understand this deletes ALL data")
    confirm2 = st.text_input("Type 'DELETE EVERYTHING':")
    
    if confirm1 and confirm2 == "DELETE EVERYTHING":
        if st.button("💥 DELETE ALL", type="secondary"):
            with st.spinner("Deleting all data..."):
                try:
                    # Emergency backup
                    participants_df, responses_df = fetch_export_data()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    emergency_p = f"emergency_participants_{timestamp}.csv"
                    emergency_r = f"emergency_responses_{timestamp}.csv"
                    
                    participants_df.to_csv(emergency_p, index=False)
                    responses_df.to_csv(emergency_r, index=False)
                    
                    # Clear database
                    db.reset_database()
                    clear_cache()
                    
                    st.success("🔥 ALL DATA CLEARED!")
                    st.info(f"Emergency backup: {emergency_p}, {emergency_r}")
                    st.balloons()
                    
                except Exception as e:
                    st.error(f"Delete failed: {e}")

# ==========================================
# FOOTER WITH PERFORMANCE INFO
# ==========================================

st.markdown("---")

# Performance info
cache_age = "Fresh"
if 'stats_timestamp' in st.session_state.cache_timestamps:
    age_seconds = time.time() - st.session_state.cache_timestamps['stats_timestamp']
    cache_age = f"{int(age_seconds)}s old"

st.markdown(f"""
    <div style="text-align: center; color: #666; padding: 1rem; font-size: 12px;">
        📊 Super Optimized Dashboard | 🔒 Secured Access | Cache: {cache_age} | Items: {len(st.session_state.cached_data)} | 
        {datetime.now().strftime("%H:%M:%S")}
    </div>
    """, unsafe_allow_html=True)