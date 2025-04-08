"""
Data simulation functions for the EGOS Dashboard.
These functions generate placeholder data to simulate metrics and status data
from the various EGOS subsystems when actual data via NATS is not available.
"""

import time

import numpy as np
import pandas as pd

from src.translations import _  # Import translation function


def get_subsystem_status():
    """
    Simulates fetching subsystem status (e.g., from Mycelium heartbeats).

    Returns:
        DataFrame with subsystem status information
    """
    subsystems = ["ETHIK", "KOIOS", "CORUJA", "MYCELIUM", "ATLAS", "NEXUS", "CRONOS", "HARMONY"]
    # Simulate dynamic statuses
    statuses = []
    base_time = time.time()
    for i, sub in enumerate(subsystems):
        mod_value = (base_time + i * 5) % 60  # Offset phase for each subsystem
        if sub == "CORUJA" and mod_value < 10:
            statuses.append("Starting")
        elif sub == "CRONOS" and mod_value > 45:
            statuses.append("Maintenance")
        elif (base_time % (70 + i * 3)) < 5:  # Less frequent errors/warnings
            statuses.append(np.random.choice(["Error", "Warning"], p=[0.6, 0.4]))
        else:
            statuses.append("Operational")

    data = {
        _("subsystem_col"): subsystems,
        _("status_col"): statuses,
        _("last_heartbeat_col"): pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return pd.DataFrame(data).set_index(_("subsystem_col"))  # Use subsystem as index


def get_overall_metrics():
    """
    Simulates fetching high-level system metrics.

    Returns:
        Dictionary with overall system metrics
    """
    # Add slight variations
    return {
        "active_tasks": 15 + int(time.time() % 7),
        "total_messages": 12548 + int(time.time() * 1.8),
        "system_load": max(0.1, min(0.9, 0.5 + np.sin(time.time() / 20) * 0.4)),
        "active_ai_models": 2,  # Assume constant for now
    }


def get_ethik_metrics():
    """
    Simulates fetching ETHIK specific metrics.

    Returns:
        Dictionary with ETHIK metrics
    """
    return {
        "rules_loaded": 42,
        "validations_passed": 10567 + int(time.time()),
        "validations_failed": 83 + int(time.time() % 6),
        "average_latency_ms": 15.5 + np.sin(time.time() / 5) * 2.0,
    }


def get_koios_metrics():
    """
    Simulates fetching KOIOS specific metrics.

    Returns:
        Dictionary with KOIOS metrics
    """
    return {
        "standards_enforced": 15,
        "log_volume_gb": 1.2 + (time.time() / 3600) * 0.05,  # Slower growth
        "docs_coverage_percent": max(
            75.0, min(95.0, 85.2 + np.sin(time.time() / 100) * 3)
        ),  # Bounded
        "search_queries_last_hr": 55 + int(np.sin(time.time() / 60) * 10),
    }


def get_coruja_metrics():
    """
    Simulates fetching CORUJA specific metrics.

    Returns:
        Dictionary with CORUJA metrics
    """
    return {
        "models_loaded": 2,
        "api_calls_hr": 150 + int(np.sin(time.time() / 30) * 30),
        "tokens_processed_m": 1.2 + (time.time() % 600) / 100.0,
        "avg_response_ms": 1150 + int(np.sin(time.time() / 15) * 80),
    }


def get_mycelium_metrics():
    """
    Simulates fetching MYCELIUM specific metrics.

    Returns:
        Dictionary with MYCELIUM metrics
    """
    return {
        "nodes_connected": 8,
        "active_topics": 25 + int(np.sin(time.time() / 10) * 5),
        "msg_rate_sec": 50 + int(np.sin(time.time() / 8) * 20),
        "queue_depth": max(0, int(5 + np.sin(time.time() / 3) * 4)),  # Ensure non-negative
    }


def get_cronos_metrics():
    """
    Simulates fetching CRONOS specific metrics.

    Returns:
        Dictionary with CRONOS metrics
    """
    last_backup_time = time.time() - (time.time() % 1800)  # Last half-hour mark
    status = "Success" if (last_backup_time % 3600) > 100 else "Failed"  # Fail sometimes
    return {
        "checkpoints_saved": 152 + int(time.time() // 3600),
        "history_size_gb": 5.8 + (time.time() // 86400) * 0.1,  # Daily growth
        "last_backup_status": status,
    }


def get_nexus_metrics():
    """
    Simulates fetching NEXUS specific metrics.

    Returns:
        Dictionary with NEXUS metrics
    """
    return {
        "modules_analyzed": 35,
        "avg_coupling": max(0.1, min(1.0, 0.65 + np.sin(time.time() / 25) * 0.05)),
        "avg_cohesion": max(0.1, min(1.0, 0.40 + np.cos(time.time() / 18) * 0.08)),
        "critical_dependencies": 3 + int(time.time() % 4),
    }


def get_subsystem_health_scores():
    """
    Generate simulated health scores for radar chart visualization.

    Returns:
        Dictionary with health scores for each subsystem
    """
    # subsystems = ["ETHIK", "KOIOS", "CORUJA", "MYCELIUM", "ATLAS", "NEXUS", "CRONOS", "HARMONY"]

    # Generate scores between 60-100 with some randomness
    subsystem_scores = {
        s: max(0, min(100, int(np.random.normal(85, 10))))
        for s in ["ETHIK", "KOIOS", "CORUJA", "MYCELIUM", "ATLAS", "NEXUS", "CRONOS", "HARMONY"]
    }
    return subsystem_scores


def generate_historical_data(
    points=60, interval_sec=1, base_value=50, noise_factor=5, trend_factor=10, sin_factor=10
):
    """
    Generates simple time-series data for charts with configurable factors.

    Args:
        points: Number of data points to generate
        interval_sec: Time interval between points in seconds
        base_value: Base value for the data
        noise_factor: Amount of random noise to add
        trend_factor: Strength of upward trend
        sin_factor: Amplitude of sine wave pattern

    Returns:
        DataFrame with timestamp index and value column
    """
    now = pd.Timestamp.now()
    timestamps = [now - pd.Timedelta(seconds=x * interval_sec) for x in range(points)][::-1]
    noise = np.random.randn(points) * noise_factor
    trend = np.linspace(0, trend_factor, points)
    sin_wave = np.sin(np.linspace(0, 10, points)) * sin_factor
    values = base_value + trend + noise + sin_wave
    df = pd.DataFrame(
        {"Timestamp": timestamps, "Value": np.maximum(0, values)}
    )  # Ensure non-negative
    df = df.set_index("Timestamp")
    return df


def style_status(status):
    """
    Returns CSS style string based on subsystem status.

    Args:
        status: Status string (e.g., 'Operational', 'Error')

    Returns:
        CSS style string
    """
    if status == "Operational":
        return "color: green; font-weight: bold;"
    elif status == "Starting":
        return "color: orange;"
    elif status == "Maintenance":
        return "color: grey;"
    elif status == "Error":
        return "color: red; font-weight: bold;"
    elif status == "Warning":
        return "color: #D4AC0D;"  # Amber/Yellow
    else:
        return ""  # Default style
