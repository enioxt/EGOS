"""
UI component functions for the EGOS Dashboard.
Contains modular functions for rendering different sections of the Streamlit interface.
"""

import asyncio
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.config import BASE_GITHUB_URL
from src.data_simulation import (
    generate_historical_data,
    get_coruja_metrics,
    get_cronos_metrics,
    get_ethik_metrics,
    get_koios_metrics,
    get_mycelium_metrics,
    get_nexus_metrics,
    get_overall_metrics,
    get_subsystem_health_scores,
    get_subsystem_status,
    style_status,
)
from src.translations import _


def render_page_header():
    """Render the page title and timestamp."""
    st.title(_("title"))
    st.caption(f"{_('last_updated')} {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("---")


def render_sidebar():
    """Render the sidebar with navigation, settings, and info."""
    # Theme toggle is handled in the main app file

    # Language Cycle Button
    language_options = {
        "en": "English",
        "pt": "Português",
        # Add other languages back if needed later
    }
    language_codes = list(language_options.keys())

    def cycle_language():
        current_lang_index = language_codes.index(st.session_state.lang)
        next_lang_index = (current_lang_index + 1) % len(language_codes)
        st.session_state.lang = language_codes[next_lang_index]
        # Reset NATS status text after language change
        st.session_state.nats_connection_status = _("nats_status_disconnected")

    st.sidebar.button(
        f"🌐 {language_options[st.session_state.lang]}",
        on_click=cycle_language,
        help="Cycle through available languages",
    )

    # NATS Status Display
    if hasattr(st.session_state, "nats_connection_status"):
        st.sidebar.caption(f"{_('nats_status_label')} {st.session_state.nats_connection_status}")
    else:
        st.sidebar.caption(f"{_('nats_status_label')} {_('nats_status_disconnected')}")

    # Subsystem Navigation Selectbox
    st.sidebar.header("Navigation")
    selected_subsystem = st.sidebar.selectbox(
        "Select Subsystem:",
        ["Overview", "ETHIK", "KOIOS", "CORUJA", "MYCELIUM", "ATLAS", "NEXUS", "CRONOS", "HARMONY"],
    )

    # Sidebar Info
    st.sidebar.header("ℹ️ About EGOS")
    st.sidebar.info("""
    The **Evolutionary Gnostic Operating System (EGOS)** is a modular and
    conscious AI ecosystem, built on fundamental ethical principles like
    Universal Love and Universal Redemption. This dashboard provides a
    (simulated) real-time view of the system's status and operation.
    """)
    st.sidebar.header("🔗 Useful Links")
    st.sidebar.markdown("- [🌐 Official Website](https://enioxt.github.io/egos)")
    st.sidebar.markdown("- [🐙 Main Repository (GitHub)](https://github.com/enioxt/EGOS)")
    st.sidebar.markdown(
        "- [🗺️ Project Roadmap](https://github.com/enioxt/EGOS/blob/main/ROADMAP.md)"
    )
    st.sidebar.markdown(
        "- [📖 Main Documentation (docs/)](https://github.com/enioxt/EGOS/tree/main/docs)"
    )

    return selected_subsystem


def render_overview_metrics():
    """Render the overall system metrics."""
    st.header(_("overview_header"))
    overall_metrics = get_overall_metrics()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(_("active_tasks"), overall_metrics["active_tasks"], help=_("active_tasks_help"))
    with col2:
        st.metric(
            _("mycelium_messages"),
            f"{overall_metrics['total_messages']:,}",
            help=_("mycelium_messages_help"),
        )
    with col3:
        st.metric(
            _("average_load"), f"{overall_metrics['system_load']:.1%}", help=_("average_load_help")
        )
    with col4:
        st.metric(
            _("active_ai_models"),
            overall_metrics["active_ai_models"],
            help=_("active_ai_models_help"),
        )


def render_subsystem_status_table():
    """Render the subsystem status table."""
    st.subheader(_("subsystem_status_header"))
    status_df = get_subsystem_status()
    st.dataframe(
        status_df.style.map(lambda x: style_status(x), subset=[_("status_col")]),
        use_container_width=True,
    )
    st.markdown("---")


def render_system_health_visualization():
    """Render the system health radar chart and metrics."""
    st.header("🌐 System Health Overview")
    st.markdown("Visual representation of all subsystem health indicators in one view.")

    # Get health scores
    health_scores = get_subsystem_health_scores()
    categories = list(health_scores.keys())
    values = list(health_scores.values())
    values.append(values[0])  # Close the loop
    categories.append(categories[0])  # Close the loop

    # Create radar chart
    fig = go.Figure()

    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill="toself",
            fillcolor="rgba(99, 110, 250, 0.5)",
            line=dict(color="rgb(99, 110, 250)", width=2),
            name="Health Score",
        )
    )

    # Add an "ideal" line at 100% for reference
    ideal_values = [100] * len(categories)
    fig.add_trace(
        go.Scatterpolar(
            r=ideal_values,
            theta=categories,
            line=dict(color="rgba(0, 200, 0, 0.4)", width=1, dash="dot"),
            name="Ideal (100%)",
            fillcolor="rgba(0, 0, 0, 0)",
            fill="none",
        )
    )

    # Add a "warning" line at 70% for reference
    warning_values = [70] * len(categories)
    fig.add_trace(
        go.Scatterpolar(
            r=warning_values,
            theta=categories,
            line=dict(color="rgba(255, 165, 0, 0.4)", width=1, dash="dot"),
            name="Warning (<70%)",
            fillcolor="rgba(0, 0, 0, 0)",
            fill="none",
        )
    )

    fig.update_layout(
        template="plotly_dark" if st.session_state.theme == "dark" else "plotly_white",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]),
            bgcolor="rgba(0,0,0,0)",  # Make polar background transparent
        ),
        paper_bgcolor="rgba(0,0,0,0)",  # Make overall background transparent
        plot_bgcolor="rgba(0,0,0,0)",  # Make plot area background transparent
        showlegend=True,
        height=500,
        margin=dict(l=80, r=80, t=20, b=20),
    )

    # Display the radar chart
    st.plotly_chart(fig, use_container_width=True)

    # Display metric indicators in a row
    health_col1, health_col2 = st.columns(2)

    with health_col1:
        # Calculate overall system health (average of all subsystems)
        overall_health = sum(list(health_scores.values())[:-1]) / (
            len(health_scores) - 1
        )  # Exclude the duplicated first element
        st.metric(
            "🔔 Overall System Health",
            f"{overall_health:.1f}%",
            delta=f"{overall_health - 85:.1f}%" if overall_health != 85 else None,
            help="Average health score across all subsystems",
        )

        # Find the subsystem with minimum health
        min_health_subsystem = min(health_scores.items(), key=lambda x: x[1])
        st.metric(
            "⚠️ Critical Attention Needed",
            f"{min_health_subsystem[0]}: {min_health_subsystem[1]}%",
            delta=f"{min_health_subsystem[1] - 70:.1f}%",
            delta_color="inverse" if min_health_subsystem[1] < 70 else "normal",
            help="Subsystem with the lowest health score that may need attention",
        )

    with health_col2:
        # Count subsystems below warning threshold
        below_warning = sum(
            1 for score in list(health_scores.values())[:-1] if score < 70
        )  # Exclude the duplicated first element
        st.metric(
            "🚨 Subsystems Below Warning",
            below_warning,
            delta=f"-{below_warning}" if below_warning > 0 else f"+{below_warning}",
            delta_color="inverse" if below_warning > 0 else "normal",
            help="Number of subsystems with health score below warning threshold (70%)",
        )

        # Find the subsystem with maximum health
        max_health_subsystem = max(health_scores.items(), key=lambda x: x[1])
        st.metric(
            "✅ Best Performing",
            f"{max_health_subsystem[0]}: {max_health_subsystem[1]}%",
            delta=f"{max_health_subsystem[1] - 90:.1f}%",
            help="Subsystem with the highest health score",
        )

    st.markdown("---")


def render_ethik_expander():
    """Render the ETHIK subsystem expander with metrics."""
    with st.expander("⚖️ ETHIK - Ethical Guardian", expanded=False):
        st.markdown(
            "**Role:** Validates actions, data, and interactions against "
            "defined ethical principles and security rules."
        )
        st.markdown(
            "**Description:** Monitors actions, data handling, and AI-generated "
            "content against core principles and defined security rules *before* "
            "execution. It ensures privacy, prevents harmful outputs, and "
            "maintains the system's ethical integrity."
        )
        ethik_metrics = get_ethik_metrics()
        e_col1, e_col2, e_col3, e_col4 = st.columns(4)
        with e_col1:
            st.metric(
                "📜 Rules Loaded",
                ethik_metrics["rules_loaded"],
                help="Total number of active validation rules.",
            )
        with e_col2:
            st.metric(
                "✅ Validations Passed",
                f"{ethik_metrics['validations_passed']:,}",
                help="Total successful validations.",
            )
        with e_col3:
            st.metric(
                "❌ Validations Failed",
                f"{ethik_metrics['validations_failed']:,}",
                delta=f"-{ethik_metrics['validations_failed'] % 5}",
                delta_color="inverse",
                help="Total validations that failed or blocked an action.",
            )
        with e_col4:
            st.metric(
                "⏱️ Avg. Latency (ms)",
                f"{ethik_metrics['average_latency_ms']:.1f}",
                help="Average time taken to perform a validation.",
            )

        st.markdown("##### Validation Trend (Last Minute)")
        validation_data = generate_historical_data(
            points=60,
            interval_sec=1,
            base_value=ethik_metrics["validations_passed"] / 60,
            noise_factor=2,
            trend_factor=5,
            sin_factor=3,
        )
        st.line_chart(validation_data)

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/ETHIK)")
        st.markdown(f"- [ETHIK Documentation (Placeholder)]({BASE_GITHUB_URL}/ETHIK/docs)")


def render_koios_expander():
    """Render the KOIOS subsystem expander with metrics."""
    with st.expander("📚 KOIOS - Standards & Knowledge", expanded=False):
        st.markdown(
            "**Role:** Manages coding standards, documentation, centralized "
            "logging, and internal knowledge search."
        )
        st.markdown(
            "**Description:** Enforces coding standards (like this dashboard's "
            "structure), facilitates documentation generation and consistency, "
            "centralizes system-wide logging, and provides internal knowledge "
            "search capabilities."
        )
        koios_metrics = get_koios_metrics()
        k_col1, k_col2, k_col3, k_col4 = st.columns(4)
        with k_col1:
            st.metric(
                "📏 Standards Checked",
                koios_metrics["standards_enforced"],
                help="Number of monitored KOIOS standards (e.g., PEP8, Docstrings).",
            )
        with k_col2:
            st.metric(
                "💾 Log Volume (GB)",
                f"{koios_metrics['log_volume_gb']:.2f}",
                delta=f"+{koios_metrics['log_volume_gb'] % 0.01:.3f}",
                delta_color="off",
                help="Total volume of stored logs.",
            )
        with k_col3:
            st.metric(
                "📖 Docs Coverage (%)",
                f"{koios_metrics['docs_coverage_percent']:.1f}",
                help="Estimated percentage of code with documentation.",
            )
        with k_col4:
            st.metric(
                "🔍 Searches / Hour",
                koios_metrics["search_queries_last_hr"],
                help="Number of searches performed on the knowledge base.",
            )

        st.markdown("##### Recent Log Entries")
        log_entries = [
            f"{pd.Timestamp.now() - pd.Timedelta(seconds=np.random.randint(30, 60))} "
            f"INFO MYCELIUM: Node ETHIK connected.",
            f"{pd.Timestamp.now() - pd.Timedelta(seconds=np.random.randint(15, 29))} "
            f"WARNING KOIOS: Low disk space detected on log volume.",
            f"{pd.Timestamp.now() - pd.Timedelta(seconds=np.random.randint(1, 14))} "
            f"ERROR CORUJA: AI Model API call failed (Timeout).",
            f"{pd.Timestamp.now() - pd.Timedelta(seconds=np.random.randint(0, 5))} "
            f"DEBUG NEXUS: Starting module analysis.",
        ]
        st.code("\\n".join(log_entries), language="log")
        st.markdown("---")

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/KOIOS)")
        koios_standards_url = (
            "https://github.com/enioxt/EGOS/blob/main/subsystems/KOIOS/docs/STANDARDS.md"
        )
        st.markdown(f"- [View KOIOS Standards]({koios_standards_url})")


def render_coruja_expander():
    """Render the CORUJA subsystem expander with metrics."""
    with st.expander("🦉 CORUJA - AI Orchestration", expanded=False):
        st.markdown(
            "**Role:** Orchestrates external and internal AI models, manages "
            "prompts, and adapts responses for other subsystems."
        )
        st.markdown(
            "**Description:** Acts as the interface to external LLMs (like Gemini, "
            "Claude) and potentially internal AI models. It crafts prompts based "
            "on requests from other subsystems, interprets AI responses, and "
            "adapts them for use within EGOS."
        )
        coruja_metrics = get_coruja_metrics()
        c_col1, c_col2, c_col3, c_col4 = st.columns(4)
        with c_col1:
            st.metric(
                "🤖 Models Loaded",
                coruja_metrics["models_loaded"],
                help="Number of AI models ready for use.",
            )
        with c_col2:
            st.metric(
                "📞 API Calls / Hour",
                coruja_metrics["api_calls_hr"],
                help="Number of calls to external/internal AI APIs.",
            )
        with c_col3:
            st.metric(
                "🧩 Tokens Processed (M)",
                f"{coruja_metrics['tokens_processed_m']:.1f}",
                help="Total tokens processed by models (in millions).",
            )
        with c_col4:
            st.metric(
                "⏱️ Avg. Response (ms)",
                f"{coruja_metrics['avg_response_ms']:.0f}",
                help="Average response time for AI calls.",
            )

        st.markdown("##### API Call Latency Trend (Last Minute)")
        latency_data = generate_historical_data(
            points=60,
            interval_sec=1,
            base_value=coruja_metrics["avg_response_ms"],
            noise_factor=50,
            trend_factor=0,
            sin_factor=80,
        )
        st.line_chart(latency_data)

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/CORUJA)")
        st.markdown(f"- [CORUJA Documentation (Placeholder)]({BASE_GITHUB_URL}/CORUJA/docs)")


def render_mycelium_expander():
    """Render the MYCELIUM subsystem expander with metrics."""
    with st.expander("🍄 MYCELIUM - Communication Network", expanded=False):
        st.markdown(
            "**Role:** Enables asynchronous, decoupled communication between all "
            "subsystems using a message broker (NATS)."
        )
        st.markdown(
            "**Description:** The central nervous system. It utilizes NATS "
            "messaging to enable reliable, asynchronous, and decoupled "
            "communication between all subsystems."
        )
        mycelium_metrics = get_mycelium_metrics()
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric(
                "🔌 Connected Nodes",
                mycelium_metrics["nodes_connected"],
                help="Number of subsystems connected to the network.",
            )
        with m_col2:
            st.metric(
                "🏷️ Active Topics",
                mycelium_metrics["active_topics"],
                help="Number of message topics currently in use.",
            )
        with m_col3:
            st.metric(
                "📨 Messages / Sec",
                mycelium_metrics["msg_rate_sec"],
                help="Average rate of messages flowing through the network.",
            )
        with m_col4:
            st.metric(
                "⏳ Queue Depth",
                mycelium_metrics["queue_depth"],
                help="Estimated number of messages awaiting processing.",
            )

        st.markdown("##### Message Rate Trend (Last Minute)")
        message_rate_data = generate_historical_data(
            points=60,
            interval_sec=1,
            base_value=mycelium_metrics["msg_rate_sec"],
            noise_factor=10,
            trend_factor=5,
            sin_factor=20,
        )
        st.line_chart(message_rate_data)

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/MYCELIUM)")
        st.markdown(f"- [MYCELIUM Documentation (Placeholder)]({BASE_GITHUB_URL}/MYCELIUM/docs)")


def render_atlas_expander():
    """Render the ATLAS subsystem expander with metrics."""
    with st.expander("🗺️ ATLAS - System Cartographer", expanded=False):
        st.markdown(
            "**Role:** Visualizes the system's structure, module dependencies, "
            "and complex information flows."
        )
        st.markdown(
            "**Description:** Responsible for generating dynamic maps and "
            "visualizations of the system's architecture, component "
            "relationships, data flows, and dependencies."
        )
        st.info(
            "Interactive ATLAS visualizations (dependency maps, component graphs, "
            "etc.) will be integrated here in the future."
        )
        # Placeholder for ATLAS metrics or visualization
        st.markdown("---")

        st.markdown("##### " + _("key_metrics"))
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            st.metric(
                "🗺️ Maps Generated",
                5 + int(time.time() // 1800),
                help="Number of static system maps generated.",
            )
        with a_col2:
            st.metric(
                "🔗 Monitored Components",
                45 + int(np.sin(time.time() / 300) * 2),
                help="Number of components tracked by ATLAS.",
            )

        st.markdown("##### Example Visualization")
        st.image(
            "https://dummyimage.com/600x200/eee/aaa&text=ATLAS+System+Map+(Placeholder)",
            caption="Placeholder for a system map generated by ATLAS",
        )

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/ATLAS)")
        st.markdown(f"- [ATLAS Documentation (Placeholder)]({BASE_GITHUB_URL}/ATLAS/docs)")


def render_nexus_expander():
    """Render the NEXUS subsystem expander with metrics."""
    with st.expander("⚙️ NEXUS - Modular Analysis", expanded=False):
        st.markdown(
            "**Role:** Analyzes module cohesion and coupling, optimizes "
            "architecture, and manages internal dependencies."
        )
        st.markdown(
            "**Description:** Focuses on the health and optimization of the "
            "internal system structure. It analyzes code for coupling, "
            "cohesion, complexity, and adherence to architectural patterns."
        )
        st.info(
            "NEXUS analysis reports (coupling scores, complexity metrics, etc.) "
            "will be integrated here."
        )
        nexus_metrics = get_nexus_metrics()
        n_col1, n_col2, n_col3, n_col4 = st.columns(4)
        with n_col1:
            st.metric(
                "📊 Modules Analyzed",
                nexus_metrics["modules_analyzed"],
                help="Number of code modules analyzed by NEXUS.",
            )
        with n_col2:
            st.metric(
                "🔗 Avg. Coupling",
                f"{nexus_metrics['avg_coupling']:.2f}",
                delta=f"{(nexus_metrics['avg_coupling'] - 0.5) * -100:.1f}%",
                delta_color="inverse",
                help="Average coupling between modules (lower is better).",
            )
        with n_col3:
            st.metric(
                "📦 Avg. Cohesion",
                f"{nexus_metrics['avg_cohesion']:.2f}",
                delta=f"{(nexus_metrics['avg_cohesion'] - 0.5) * 100:.1f}%",
                help="Average cohesion within modules (higher is better).",
            )
        with n_col4:
            st.metric(
                "⚠️ Critical Dependencies",
                nexus_metrics["critical_dependencies"],
                help="Number of high-risk dependencies identified.",
            )

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/NEXUS)")
        st.markdown(f"- [NEXUS Documentation (Placeholder)]({BASE_GITHUB_URL}/NEXUS/docs)")


def render_cronos_expander():
    """Render the CRONOS subsystem expander with metrics."""
    with st.expander("⏱️ CRONOS - Time & History", expanded=False):
        st.markdown(
            "**Role:** Manages system time, schedules recurring tasks, and "
            "maintains system state history."
        )
        st.markdown(
            "**Description:** Acts as the system's internal clock and memory. "
            "It handles time-based events, schedules recurring tasks, maintains "
            "checkpoints of system state, and preserves historical records for "
            "diagnostics and learning."
        )
        cronos_metrics = get_cronos_metrics()
        c_col1, c_col2, c_col3 = st.columns(3)
        with c_col1:
            st.metric(
                "📊 Checkpoints",
                cronos_metrics["checkpoints_saved"],
                help="Number of system state checkpoints saved.",
            )
        with c_col2:
            st.metric(
                "💾 History Size (GB)",
                f"{cronos_metrics['history_size_gb']:.1f}",
                help="Size of historical data storage.",
            )
        with c_col3:
            status_color = (
                "normal" if cronos_metrics["last_backup_status"] == "Success" else "inverse"
            )
            st.metric(
                "🔄 Last Backup",
                cronos_metrics["last_backup_status"],
                delta="OK" if cronos_metrics["last_backup_status"] == "Success" else "Failed",
                delta_color=status_color,
                help="Status of the most recent backup.",
            )

        st.markdown("##### Recent Backup History (Simulated)")
        backup_df = pd.DataFrame(
            {
                "Timestamp": [pd.Timestamp.now() - pd.Timedelta(hours=x) for x in range(1, 5)],
                "Type": ["Incremental", "Full", "Incremental", "Incremental"],
                "Status": ["Success", "Success", "Success", "Failed"],
                "Size (MB)": [25, 480, 18, 0],
            }
        )
        st.dataframe(backup_df, use_container_width=True, hide_index=True)

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/CRONOS)")
        st.markdown(f"- [CRONOS Documentation (Placeholder)]({BASE_GITHUB_URL}/CRONOS/docs)")


def render_harmony_expander():
    """Render the HARMONY subsystem expander with metrics."""
    with st.expander("🤝 HARMONY - Integration & Testing", expanded=False):
        st.markdown(
            "**Role:** Ensures compatibility, consistency, and quality across "
            "the entire EGOS ecosystem through testing and health checks."
        )
        st.markdown(
            "**Description:** Focuses on system-wide integration, automated "
            "testing, continuous integration, compatibility checks, and "
            "system-wide health monitoring."
        )
        st.markdown("##### Latest Test Run Summary")
        # Simulate some test results
        test_summary = f"""
        **Run Timestamp:** {pd.Timestamp.now() - pd.Timedelta(minutes=np.random.randint(5, 60))}
        **Overall Status:** {"PASS" if np.random.random() > 0.2 else np.random.choice(["FAIL", "WARN"])}
        **Unit Tests:** 150/150 Passed
        **Integration Tests:** 45/50 Passed (5 Skipped)
        **Coverage:** 88.5%
        """
        st.text_area("Test Summary", test_summary, height=150)

        st.markdown("**Resources:**")
        st.markdown(f"- [View Source Code (GitHub)]({BASE_GITHUB_URL}/HARMONY)")
        st.markdown(f"- [HARMONY Documentation (Placeholder)]({BASE_GITHUB_URL}/HARMONY/docs)")


def render_nats_connect_button():
    """Renders the NATS connection button and handles connection logic."""
    if not hasattr(st.session_state, "nats_connected") or not st.session_state.nats_connected:
        if st.sidebar.button(_("connect_live_data")):
            with st.spinner("Connecting to NATS..."):
                if "nats_client" not in st.session_state or st.session_state.nats_client is None:
                    try:
                        from src.nats_client import NATSClient  # Local import for optional NATS

                        # Assuming NATS runs on localhost:4222
                        st.session_state.nats_client = NATSClient()
                        asyncio.run(st.session_state.nats_client.connect())
                    except ImportError:
                        st.error("NATS libraries not installed. Cannot connect.")
                        st.session_state.nats_client = None
                    except Exception as e:
                        st.error(f"NATS connection failed: {e}")
                        st.session_state.nats_client = None  # Ensure client is reset on failure

                if st.session_state.nats_client and st.session_state.nats_client.is_connected:
                    st.session_state.nats_connected = True
                    st.session_state.nats_connection_status = _("nats_status_connected")
                    st.success("Connected to NATS!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.nats_connected = False
                    st.session_state.nats_connection_status = _("nats_status_error")
                    st.warning("Could not establish NATS connection.")
    else:
        st.sidebar.caption(f"{_('nats_status_label')} {_('nats_status_connected')}")


import numpy as np
