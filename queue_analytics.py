#!/usr/bin/env python3
"""
Call Queue Analytics Report Generator
• Reads Queue Call Summary and Agent Summary CSVs
• Creates Markdown + JSON reports with queue performance metrics
• Optional GPT-4o-mini executive summary focused on call center KPIs
"""

import argparse, os, json, warnings, datetime as dt, re, textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import pytz
import numpy as np

try:
    from openai import OpenAI          # SDK ≥1.0
except ModuleNotFoundError:
    OpenAI = None

warnings.filterwarnings("ignore", message="Could not infer format")

# ───── constants
TZ_IL = pytz.timezone("Asia/Jerusalem")
TODAY = dt.date.today()

# ───── loaders & parsers
def parse_datetime_from_interval(date_str, interval_str):
    """Parse the specific date/interval format from the CSV"""
    try:
        # Parse date from MM.DD.YYYY format
        date_parts = date_str.split('.')
        if len(date_parts) == 3:
            month, day, year = date_parts
            
            # Parse interval start time from "HH:MM - HH:MM" format
            interval_start = interval_str.split(' - ')[0].strip()
            
            # Combine into full datetime string
            datetime_str = f"{year}-{month.zfill(2)}-{day.zfill(2)} {interval_start}"
            return pd.to_datetime(datetime_str)
    except:
        pass
    return pd.NaT

def load_queue_csv(path: str) -> pd.DataFrame:
    """Load and normalize queue call summary CSV"""
    df = pd.read_csv(path)
    # Normalize column names
    df.columns = df.columns.str.upper().str.strip()
    
    # Parse the specific date/interval format
    try:
        if 'DATE' in df.columns and 'INTERVAL' in df.columns:
            df['DATETIME'] = df.apply(lambda row: parse_datetime_from_interval(
                str(row['DATE']), str(row['INTERVAL'])), axis=1)
        else:
            df['DATETIME'] = pd.Timestamp.now()
            
        # Drop rows where datetime parsing failed
        df = df.dropna(subset=['DATETIME'])
        
        if not df.empty:
            df['DATE_ONLY'] = df['DATETIME'].dt.date
            df['HOUR'] = df['DATETIME'].dt.hour
            df['MINUTE'] = df['DATETIME'].dt.minute
        else:
            # If all dates failed to parse, create dummy columns
            df['DATE_ONLY'] = pd.Timestamp.now().date()
            df['HOUR'] = 12
            df['MINUTE'] = 0
            
    except Exception as e:
        print(f"Warning: Date parsing failed: {e}")
        # Create dummy date columns
        df['DATETIME'] = pd.Timestamp.now()
        df['DATE_ONLY'] = pd.Timestamp.now().date()
        df['HOUR'] = 12
        df['MINUTE'] = 0
    
    return df

def load_agent_csv(path: str) -> pd.DataFrame:
    """Load and normalize agent summary CSV"""
    df = pd.read_csv(path)
    # Normalize column names
    df.columns = df.columns.str.upper().str.strip()
    
    # Parse the specific date/interval format
    try:
        if 'DATE' in df.columns and 'INTERVAL' in df.columns:
            df['DATETIME'] = df.apply(lambda row: parse_datetime_from_interval(
                str(row['DATE']), str(row['INTERVAL'])), axis=1)
        else:
            df['DATETIME'] = pd.Timestamp.now()
            
        df = df.dropna(subset=['DATETIME'])
        
        if not df.empty:
            df['DATE_ONLY'] = df['DATETIME'].dt.date
            df['HOUR'] = df['DATETIME'].dt.hour
        else:
            df['DATE_ONLY'] = pd.Timestamp.now().date()
            df['HOUR'] = 12
            
    except Exception as e:
        print(f"Warning: Agent date parsing failed: {e}")
        df['DATETIME'] = pd.Timestamp.now()
        df['DATE_ONLY'] = pd.Timestamp.now().date()
        df['HOUR'] = 12
    
    return df

def parse_time_duration(time_str):
    """Convert time string (HH:MM:SS or MM:SS) to total seconds"""
    if pd.isna(time_str) or str(time_str).strip() == '' or str(time_str).strip().lower() in ['nan', 'null', '0', '00:00']:
        return 0
    try:
        time_str = str(time_str).strip()
        # Handle different time formats
        if ':' in time_str:
            parts = time_str.split(':')
            if len(parts) == 3:  # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2:  # MM:SS (most common in your data)
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 1:
                return int(float(parts[0]))
        else:
            # Just seconds or a number
            return int(float(time_str))
    except (ValueError, AttributeError):
        return 0

# ───── queue metrics
def calculate_queue_metrics(df: pd.DataFrame) -> dict:
    """Calculate key queue performance metrics"""
    total_answered = df['ANSWERED CALLS'].sum()
    total_abandoned = df['ABANDONED CALLS'].sum()
    total_overflowed = df['OVERFLOWED CALLS'].sum()
    total_offered = total_answered + total_abandoned + total_overflowed
    
    # Service Level metrics
    abandonment_rate = round((total_abandoned / total_offered * 100), 2) if total_offered > 0 else 0
    answer_rate = round((total_answered / total_offered * 100), 2) if total_offered > 0 else 0
    overflow_rate = round((total_overflowed / total_offered * 100), 2) if total_offered > 0 else 0
    
    # Wait time analysis (convert to seconds)
    df['AVG_WAIT_SEC'] = df['AVERAGE WAIT TIME'].apply(parse_time_duration)
    df['MAX_WAIT_SEC'] = df['MAXIMUM WAIT TIME'].apply(parse_time_duration)
    df['MIN_WAIT_SEC'] = df['MINIMUM WAIT TIME'].apply(parse_time_duration)
    df['AVG_HANDLE_SEC'] = df['AVERAGE HANDLE TIME'].apply(parse_time_duration)
    
    # Handle NaN values properly
    avg_wait_time = df['AVG_WAIT_SEC'].mean() if not df['AVG_WAIT_SEC'].isna().all() else 0
    max_wait_time = df['MAX_WAIT_SEC'].max() if not df['MAX_WAIT_SEC'].isna().all() else 0
    avg_handle_time = df['AVG_HANDLE_SEC'].mean() if not df['AVG_HANDLE_SEC'].isna().all() else 0
    
    # Peak analysis
    peak_interval = df.loc[df['ANSWERED CALLS'].idxmax()] if len(df) > 0 else None
    worst_abandon_interval = df.loc[df['ABANDONED CALLS'].idxmax()] if len(df) > 0 else None
    
    return {
        'total_offered': total_offered,
        'total_answered': total_answered,
        'total_abandoned': total_abandoned,
        'total_overflowed': total_overflowed,
        'abandonment_rate': abandonment_rate,
        'answer_rate': answer_rate,
        'overflow_rate': overflow_rate,
        'avg_wait_time_sec': round(avg_wait_time, 1) if not pd.isna(avg_wait_time) else 0,
        'max_wait_time_sec': int(max_wait_time) if not pd.isna(max_wait_time) else 0,
        'avg_handle_time_sec': round(avg_handle_time, 1) if not pd.isna(avg_handle_time) else 0,
        'peak_interval': {
            'datetime': str(peak_interval['DATETIME']),
            'answered_calls': peak_interval['ANSWERED CALLS'],
            'abandoned_calls': peak_interval['ABANDONED CALLS']
        } if peak_interval is not None else None,
        'worst_abandon_interval': {
            'datetime': str(worst_abandon_interval['DATETIME']),
            'abandoned_calls': worst_abandon_interval['ABANDONED CALLS'],
            'answered_calls': worst_abandon_interval['ANSWERED CALLS']
        } if worst_abandon_interval is not None else None
    }

def analyze_service_level_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze abandonment rate trends by time period"""
    df['TOTAL_OFFERED'] = df['ANSWERED CALLS'] + df['ABANDONED CALLS'] + df['OVERFLOWED CALLS']
    df['ABANDONMENT_RATE'] = (df['ABANDONED CALLS'] / df['TOTAL_OFFERED'] * 100).fillna(0).round(2)
    
    # Group by hour to show trends
    hourly_trends = df.groupby('HOUR').agg({
        'ANSWERED CALLS': 'sum',
        'ABANDONED CALLS': 'sum',
        'OVERFLOWED CALLS': 'sum',
        'TOTAL_OFFERED': 'sum'
    }).reset_index()
    
    hourly_trends['ABANDONMENT_RATE'] = (
        hourly_trends['ABANDONED CALLS'] / hourly_trends['TOTAL_OFFERED'] * 100
    ).fillna(0).round(2)
    
    return hourly_trends[hourly_trends['TOTAL_OFFERED'] > 0].sort_values('ABANDONMENT_RATE', ascending=False)

def analyze_agent_performance(df: pd.DataFrame) -> dict:
    """Analyze individual agent performance"""
    if df.empty:
        return {}
    
    # Convert handle times to seconds
    df['TOTAL_HANDLE_SEC'] = df['TOTAL HANDLE TIME'].apply(parse_time_duration)
    df['AVG_HANDLE_SEC'] = df['AVERAGE HANDLE TIME'].apply(parse_time_duration)
    df['MAX_HANDLE_SEC'] = df['MAXIMUM HANDLE TIME'].apply(parse_time_duration)
    df['MIN_HANDLE_SEC'] = df['MINIMUM HANDLE TIME'].apply(parse_time_duration)
    
    # Agent summary stats
    agent_stats = df.groupby('AGENT').agg({
        'ANSWERED CALLS': 'sum',
        'TOTAL_HANDLE_SEC': 'sum',
        'AVG_HANDLE_SEC': 'mean',
        'MAX_HANDLE_SEC': 'max'
    }).reset_index()
    
    agent_stats['AVG_HANDLE_TIME'] = agent_stats['AVG_HANDLE_SEC'].round(1)
    agent_stats = agent_stats.sort_values('ANSWERED CALLS', ascending=False)
    
    # Top and bottom performers
    top_volume = agent_stats.head(5)[['AGENT', 'ANSWERED CALLS', 'AVG_HANDLE_TIME']]
    
    # Efficiency analysis (calls per minute of handle time)
    agent_stats['EFFICIENCY'] = (
        agent_stats['ANSWERED CALLS'] / (agent_stats['TOTAL_HANDLE_SEC'] / 60)
    ).round(3)
    most_efficient = agent_stats.nlargest(5, 'EFFICIENCY')[['AGENT', 'ANSWERED CALLS', 'EFFICIENCY', 'AVG_HANDLE_TIME']]
    
    return {
        'all_agents': agent_stats,
        'top_volume': top_volume,
        'most_efficient': most_efficient
    }

# ───── charts
def chart_abandonment_trend(df: pd.DataFrame, path: Path):
    """Create abandonment rate trend chart"""
    if df.empty:
        return
    
    df['TOTAL_OFFERED'] = df['ANSWERED CALLS'] + df['ABANDONED CALLS'] + df['OVERFLOWED CALLS']
    df['ABANDONMENT_RATE'] = (df['ABANDONED CALLS'] / df['TOTAL_OFFERED'] * 100).fillna(0)
    
    # Filter out rows with no calls
    df_filtered = df[df['TOTAL_OFFERED'] > 0]
    if df_filtered.empty:
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Call volume over time
    ax1.plot(df_filtered['DATETIME'], df_filtered['ANSWERED CALLS'], label='Answered', color='green', marker='o')
    ax1.plot(df_filtered['DATETIME'], df_filtered['ABANDONED CALLS'], label='Abandoned', color='red', marker='s')
    ax1.plot(df_filtered['DATETIME'], df_filtered['OVERFLOWED CALLS'], label='Overflowed', color='orange', marker='^')
    ax1.set_ylabel('Call Count')
    ax1.set_title('Call Volume by Type Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Abandonment rate
    ax2.plot(df_filtered['DATETIME'], df_filtered['ABANDONMENT_RATE'], color='red', marker='o', linewidth=2)
    ax2.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='5% Target')
    ax2.axhline(y=10, color='red', linestyle='--', alpha=0.7, label='10% Warning')
    ax2.set_ylabel('Abandonment Rate (%)')
    ax2.set_xlabel('Time')
    ax2.set_title('Abandonment Rate Trend')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches='tight')
    plt.close()

def chart_agent_performance(agent_data: dict, path: Path):
    """Create agent performance comparison chart"""
    if not agent_data or agent_data['top_volume'].empty:
        return
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Top agents by call volume
    top_vol = agent_data['top_volume']
    ax1.barh(top_vol['AGENT'], top_vol['ANSWERED CALLS'], color='steelblue')
    ax1.set_xlabel('Calls Answered')
    ax1.set_title('Top Agents by Call Volume')
    ax1.grid(True, alpha=0.3)
    
    # Agent efficiency
    if not agent_data['most_efficient'].empty:
        eff_data = agent_data['most_efficient']
        ax2.barh(eff_data['AGENT'], eff_data['EFFICIENCY'], color='forestgreen')
        ax2.set_xlabel('Calls per Minute (Handle Time)')
        ax2.set_title('Most Efficient Agents')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches='tight')
    plt.close()

def chart_hourly_patterns(df: pd.DataFrame, path: Path):
    """Create hourly call patterns chart"""
    if df.empty:
        return
        
    hourly = df.groupby('HOUR').agg({
        'ANSWERED CALLS': 'sum',
        'ABANDONED CALLS': 'sum',
        'OVERFLOWED CALLS': 'sum'
    }).reset_index()
    
    if hourly.empty:
        return
    
    hourly['TOTAL'] = hourly['ANSWERED CALLS'] + hourly['ABANDONED CALLS'] + hourly['OVERFLOWED CALLS']
    hourly['ABANDONMENT_RATE'] = (hourly['ABANDONED CALLS'] / hourly['TOTAL'] * 100).fillna(0)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Hourly volume
    ax1.bar(hourly['HOUR'], hourly['ANSWERED CALLS'], label='Answered', color='green', alpha=0.7)
    ax1.bar(hourly['HOUR'], hourly['ABANDONED CALLS'], bottom=hourly['ANSWERED CALLS'], 
            label='Abandoned', color='red', alpha=0.7)
    ax1.bar(hourly['HOUR'], hourly['OVERFLOWED CALLS'], 
            bottom=hourly['ANSWERED CALLS'] + hourly['ABANDONED CALLS'],
            label='Overflowed', color='orange', alpha=0.7)
    ax1.set_ylabel('Call Count')
    ax1.set_title('Hourly Call Volume Distribution')
    ax1.legend()
    ax1.set_xticks(range(24))
    ax1.grid(True, alpha=0.3)
    
    # Hourly abandonment rate
    ax2.bar(hourly['HOUR'], hourly['ABANDONMENT_RATE'], color='red', alpha=0.7)
    ax2.axhline(y=5, color='orange', linestyle='--', alpha=0.7, label='5% Target')
    ax2.set_ylabel('Abandonment Rate (%)')
    ax2.set_xlabel('Hour of Day')
    ax2.set_title('Hourly Abandonment Rate')
    ax2.legend()
    ax2.set_xticks(range(24))
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches='tight')
    plt.close()

# ───── GPT summary
def gpt_summary(metrics_text: str, key: str) -> str:
    """Generate executive summary using GPT"""
    if not key or OpenAI is None: 
        return "⚠️ OpenAI key missing – summary not generated.\n"
    
    client = OpenAI(api_key=key)
    chat = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": (
            "You are a Call Center Analytics Expert. "
            "Write a six-bullet executive summary for call center management "
            "focusing on service level, abandonment rates, agent performance, and actionable recommendations.\n\n"
            f"Queue Performance Data:\n{metrics_text}"
        )}],
        temperature=0.3,
    )
    return chat.choices[0].message.content.strip()

# ───── markdown helpers
def md_table(df: pd.DataFrame, index: bool = False) -> str:
    """Convert DataFrame to markdown table"""
    if df.empty:
        return "\n_— no data —_\n"
    return "\n" + df.to_markdown(index=index, tablefmt="github") + "\n"

def format_seconds_to_time(seconds: float) -> str:
    """Convert seconds to MM:SS format"""
    if pd.isna(seconds) or seconds == 0:
        return "00:00"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

def build_kpi_table(metrics: dict) -> str:
    """Build the main KPI table"""
    peak_info = "N/A"
    if metrics.get('peak_interval'):
        peak = metrics['peak_interval']
        peak_info = f"{peak['answered_calls']} calls at {peak['datetime']}"
    
    abandon_info = "N/A"
    if metrics.get('worst_abandon_interval'):
        abandon = metrics['worst_abandon_interval']
        abandon_info = f"{abandon['abandoned_calls']} calls at {abandon['datetime']}"
    
    kpi_data = pd.DataFrame({
        "Metric": [
            "Total Calls Offered",
            "Calls Answered", 
            "Calls Abandoned",
            "Calls Overflowed",
            "Answer Rate",
            "Abandonment Rate",
            "Overflow Rate", 
            "Average Wait Time",
            "Maximum Wait Time",
            "Average Handle Time",
            "Peak Call Period",
            "Worst Abandonment Period"
        ],
        "Value": [
            f"{metrics['total_offered']:,}",
            f"{metrics['total_answered']:,} ({metrics['answer_rate']}%)",
            f"{metrics['total_abandoned']:,} ({metrics['abandonment_rate']}%)",
            f"{metrics['total_overflowed']:,} ({metrics['overflow_rate']}%)",
            f"{metrics['answer_rate']}%",
            f"{metrics['abandonment_rate']}%",
            f"{metrics['overflow_rate']}%",
            format_seconds_to_time(metrics['avg_wait_time_sec']),
            format_seconds_to_time(metrics['max_wait_time_sec']),
            format_seconds_to_time(metrics['avg_handle_time_sec']),
            peak_info,
            abandon_info
        ]
    })
    
    return md_table(kpi_data)

def build_markdown_report(summary: str, kpi_table: str, trends_df: pd.DataFrame, 
                         agent_data: dict, chart_paths: dict) -> str:
    """Build the complete markdown report"""
    
    sections = [
        "## Executive Summary\n" + summary,
        "## Key Performance Indicators\n" + kpi_table,
        "## Service Level Trends\n" + f"![Abandonment Trends]({chart_paths['abandonment']})",
        "## Hourly Call Patterns\n" + f"![Hourly Patterns]({chart_paths['hourly']})",
        "## Service Level by Hour\n" + md_table(trends_df.head(10)),
    ]
    
    if agent_data and not agent_data['top_volume'].empty:
        sections.extend([
            "## Agent Performance\n" + f"![Agent Performance]({chart_paths['agents']})",
            "## Top Agents by Call Volume\n" + md_table(agent_data['top_volume']),
            "## Most Efficient Agents\n" + md_table(agent_data['most_efficient'])
        ])
    
    return "\n\n".join(sections) + "\n"

# ───── main
def main():
    parser = argparse.ArgumentParser(description="Generate Call Queue Analytics Report")
    parser.add_argument("--queue-csv", required=True, help="Queue Call Summary CSV file")
    parser.add_argument("--agent-csv", help="Agent Summary CSV file (optional)")
    parser.add_argument("--output", default="queue_report.md", help="Output markdown file")
    parser.add_argument("--openai-key", help="OpenAI API key for summary generation")
    
    args = parser.parse_args()
    key = args.openai_key or os.getenv("OPENAI_API_KEY")
    
    # Load data
    print("Loading queue data...")
    queue_df = load_queue_csv(args.queue_csv)
    print(f"Loaded {len(queue_df)} queue records")
    if not queue_df.empty:
        print(f"Date range: {queue_df['DATETIME'].min()} to {queue_df['DATETIME'].max()}")
    
    agent_df = pd.DataFrame()
    if args.agent_csv and Path(args.agent_csv).exists():
        print("Loading agent data...")
        agent_df = load_agent_csv(args.agent_csv)
        print(f"Loaded {len(agent_df)} agent records")
    
    # Calculate metrics
    print("Analyzing queue performance...")
    if queue_df.empty:
        print("Warning: No queue data to analyze")
        return
        
    queue_metrics = calculate_queue_metrics(queue_df)
    service_trends = analyze_service_level_trends(queue_df)
    agent_performance = analyze_agent_performance(agent_df)
    
    # Generate charts
    print("Creating charts...")
    chart_paths = {
        'abandonment': Path("abandonment_trends.png"),
        'hourly': Path("hourly_patterns.png"),
        'agents': Path("agent_performance.png")
    }
    
    chart_abandonment_trend(queue_df, chart_paths['abandonment'])
    chart_hourly_patterns(queue_df, chart_paths['hourly'])
    if agent_performance:
        chart_agent_performance(agent_performance, chart_paths['agents'])
    
    # Build report
    print("Generating report...")
    kpi_table = build_kpi_table(queue_metrics)
    summary = gpt_summary(kpi_table, key)
    
    markdown_report = build_markdown_report(
        summary, kpi_table, service_trends, agent_performance, chart_paths
    )
    
    # Save files
    output_path = Path(args.output)
    output_path.write_text(markdown_report, encoding="utf-8")
    print(f"✅ Markdown report saved → {output_path}")
    
    # Save JSON data
    json_data = {
        "queue_metrics": queue_metrics,
        "service_trends": service_trends.to_dict(orient="records"),
        "agent_performance": {
            k: v.to_dict(orient="records") if hasattr(v, 'to_dict') else v
            for k, v in agent_performance.items()
        } if agent_performance else {},
        "charts": {k: str(v) for k, v in chart_paths.items()},
        "summary": summary.strip()
    }
    
    json_path = output_path.with_suffix(".json")
    json_path.write_text(json.dumps(json_data, default=str, indent=2), encoding="utf-8")
    print(f"✅ JSON data saved → {json_path}")

if __name__ == "__main__":
    main()