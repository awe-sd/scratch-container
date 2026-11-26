import AWUtil
from AWDecomp import psenShiftSet, portfolio, decomp
import AWSnowflakeUtil as sf
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import importlib
pd.set_option('future.no_silent_downcasting', True)

from ftr_engine_batch import *
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure logging


def benchmark_shifts(
    study_id,
    branch_label,
    ctg_label,
    start_date,
    end_date,
    sign_in_study=-1,
    reference_cpnodeid=12791,
    sim_hour=None,
    psen_threshold=0.0001,
    filter_deadbus=True
):
    """
    Benchmark shift factors between study results and DART shifts.

    Parameters:
    -----------
    study_id : int
        The study ID to filter study_shifts
    branch_label : str
        Branch label to filter (e.g., '6945')
    ctg_label : str
        Contingency label to filter (e.g., 'MCATMG25')
    start_date : str
        Start date for DART shifts (format: 'YYYY-MM-DD')
    end_date : str
        End date for DART shifts (format: 'YYYY-MM-DD')
    sign_in_study : int, optional
        Sign to apply to study psens values (default: -1)
    reference_cpnodeid : int, optional
        Reference bus cpnodeid for normalization (default: 12791)
    sim_hour : int, optional
        Specific hour to filter (default: None for all hours)
    psen_threshold : float, optional
        Minimum absolute difference to include (default: 0.0001)

    Returns:
    --------
    pandas.DataFrame
        Comparison results with study and DART shift factors
    """
        # Build the deadbus filter
    deadbus_filter = "AND cv.deadbus = 0" if filter_deadbus else ""
    # Build the hour filter condition
    hour_filter = f"AND ds.simhour = {sim_hour}" if sim_hour is not None else ""

    query = f"""
WITH study_shifts AS (
    SELECT
        cv.PSENSHIFTID,
        cv.RUNID,
        {sign_in_study}*cv.psens as psens,
        cv.direction,
        cv.name,
        cv.cpnodeid,
        orun.simdate,
        orun.simhour,
        cv.branchlabel,
        cv.ctglabel
    FROM shift_factors.dbo.cpnode_shifts_view cv
    INNER JOIN AWOPF.DBO.OPFRUN AS orun
        ON cv.runid = orun.runid
    WHERE cv.isomarketid = 6
        AND cv.studyid = {study_id}
        AND cv.branchlabel LIKE '%{branch_label}%'
        AND cv.ctglabel = '{ctg_label}'
        {deadbus_filter}
),
DART_shifts AS (
    SELECT
        psd.psenshiftid,
        ps.psen,
        ps.cpnodeid,
        cp.name,
        b.branchName AS branchlabel,
        cdc.congContName AS ctglabel,
        TO_DATE(psd.extractionEnd) AS simdate,
        HOUR(psd.extractionEnd)+1 AS simhour
    FROM AW.dbo.psenShiftDef AS psd
    INNER JOIN AW.DBO.PSENSHIFT AS ps
        ON ps.psenshiftid = psd.psenshiftid
    INNER JOIN AW.DBO.congDefConstraint AS cd
        ON cd.congConstraintID = psd.congConstraintID
    INNER JOIN AW.DBO.congDefMonitor cdm
        ON cdm.congMontID = cd.congMontID
    INNER JOIN AW.DBO.congDefContingency cdc
        ON cdc.congContID = cd.congContID
    INNER JOIN AW.DBO.branchMonitored bm
        ON bm.branchMonitoredID = cdm.branchMonitoredId
    INNER JOIN AW.DBO.branch b
        ON b.branchID = bm.branchID
    INNER JOIN AW.DBO.CPNODE cp
        ON cp.cpnodeid = ps.cpnodeid
    WHERE psd.isoMarketID = 6
        AND psd.psenShiftTypeId = 14
        AND psd.extractionEnd >= '{start_date}'
        AND psd.extractionEnd <= '{end_date}'
        AND b.branchName LIKE '%{branch_label}%'
        AND cdc.congContName = '{ctg_label}'
)
SELECT
    ss.psenshiftid as STUDY_psenshiftid,
    ds.psenshiftid as DART_psenshiftid,
    ss.psens as STUDY_psens,
    ds.psen as DART_psens,
    ref.psen as REFERENCE_psens,
    ref.name as REFERENCE_bus,
    ABS(ss.psens + ref.psen - ds.psen) as PSEN_DIFFERENCE,
    ss.cpnodeid,
    ss.name as STUDY_name,
    ss.branchlabel,
    ss.ctglabel,
    ss.simdate,
    ss.simhour,
    ss.RUNID
FROM study_shifts ss
INNER JOIN DART_shifts ds
    ON ss.branchlabel = ds.branchlabel
    AND ss.cpnodeid = ds.cpnodeid
    AND ss.ctglabel = ds.ctglabel
    AND ss.simdate = ds.simdate
    AND ss.simhour = ds.simhour
INNER JOIN DART_shifts ref
    ON ss.simdate = ref.simdate
    AND ss.simhour = ref.simhour
    AND ref.psenshiftid = ds.psenshiftid
    AND ref.cpnodeid = {reference_cpnodeid}
WHERE 1=1
    {hour_filter}
    AND ABS(ss.psens + ref.psen - ds.psen) > {psen_threshold}
ORDER BY
    ds.psen DESC,
    ss.simdate DESC,
    ss.simhour DESC
"""

    logging.info(f"Benchmarking shifts for study {study_id}, branch '{branch_label}', ctg '{ctg_label}'")
    logging.info(f"Date range: {start_date} to {end_date}")

    # Execute query using Snowflake
    df = sf.performQuery('AW', query)

    logging.info(f"Found {len(df)} shift comparisons with difference > {psen_threshold}")
    logging.info(f"Found {len(df)} shift comparisons with difference > {psen_threshold}")
    return df


def benchmark_interface_shifts(
    study_id,
    interface_name,
    ctg_label,
    start_date,
    end_date,
    sign_in_study=-1,
    reference_cpnodeid=12791,
    sim_hour=None,
    psen_threshold=0.0001,
    filter_deadbus=True
):
    """
    Benchmark shift factors for interfaces/GTCs between study results and DART shifts.

    Parameters:
    -----------
    study_id : int
        The study ID to filter study_shifts
    interface_name : str
        Interface name to filter (e.g., 'WESTEX')
    ctg_label : str
        Contingency label to filter (e.g., 'BASE CASE' or specific contingency)
    start_date : str
        Start date for DART shifts (format: 'YYYY-MM-DD')
    end_date : str
        End date for DART shifts (format: 'YYYY-MM-DD')
    sign_in_study : int, optional
        Sign to apply to study psens values (default: -1)
    reference_cpnodeid : int, optional
        Reference bus cpnodeid for normalization (default: 12791)
    sim_hour : int, optional
        Specific hour to filter (default: None for all hours)
    psen_threshold : float, optional
        Minimum absolute difference to include (default: 0.0001)
    filter_deadbus : bool, optional
        Whether to filter out dead buses in study shifts (default: True)

    Returns:
    --------
    pandas.DataFrame
        Comparison results with study and DART interface shift factors
    """

    # Build the hour filter condition
    hour_filter = f"AND ds.simhour = {sim_hour}" if sim_hour is not None else ""

    # Build the deadbus filter
    deadbus_filter = "AND cv.deadbus = 0" if filter_deadbus else ""

    # Build the ctg filter
    ctg_filter = f"AND cv.ctglabel = '{ctg_label}'" if ctg_label else ""
    ctg_filter_dart = f"AND cdc.congContName = '{ctg_label}'" if ctg_label else ""

    query = f"""
WITH study_shifts AS (
    SELECT
        cv.PSENSHIFTID,
        cv.RUNID,
        {sign_in_study}*cv.psens as psens,
        cv.name,
        cv.cpnodeid,
        orun.simdate,
        orun.simhour,
        cv.interfacename,
        cv.ctglabel
    FROM shift_factors.dbo.cpnode_shifts_view cv
    INNER JOIN AWOPF.DBO.OPFRUN AS orun
        ON cv.runid = orun.runid
    WHERE cv.isomarketid = 6
        AND cv.studyid = {study_id}
        AND cv.interfacename LIKE '%{interface_name}%'
        {ctg_filter}
        {deadbus_filter}
),
DART_shifts AS (
    SELECT
        psd.psenshiftid,
        ps.psen,
        ps.cpnodeid,
        cp.name,
        bm.branchmonitoredname AS interfacename,
        cdc.congContName AS ctglabel,
        TO_DATE(psd.extractionEnd) AS simdate,
        HOUR(psd.extractionEnd)+1 AS simhour
    FROM AW.dbo.psenShiftDef AS psd
    INNER JOIN AW.DBO.PSENSHIFT AS ps
        ON ps.psenshiftid = psd.psenshiftid
    INNER JOIN AW.DBO.congDefConstraint AS cd
        ON cd.congConstraintID = psd.congConstraintID
    INNER JOIN AW.DBO.congDefMonitor cdm
        ON cdm.congMontID = cd.congMontID
    INNER JOIN AW.DBO.congDefContingency cdc
        ON cdc.congContID = cd.congContID
    INNER JOIN AW.DBO.branchMonitored bm
        ON bm.branchMonitoredID = cdm.branchMonitoredId
    INNER JOIN AW.DBO.CPNODE cp
        ON cp.cpnodeid = ps.cpnodeid
    WHERE psd.isoMarketID = 6
        AND psd.psenShiftTypeId = 14
        AND psd.extractionEnd >= '{start_date}'
        AND psd.extractionEnd <= '{end_date}'
        AND bm.branchmonitoredname LIKE '%{interface_name}%'
        {ctg_filter_dart}
)
SELECT
    ss.psenshiftid as STUDY_psenshiftid,
    ds.psenshiftid as DART_psenshiftid,
    ss.psens as STUDY_psens,
    ds.psen as DART_psens,
    ref.psen as REFERENCE_psens,
    ref.name as REFERENCE_bus,
    ABS(ss.psens + ref.psen - ds.psen) as PSEN_DIFFERENCE,
    ss.cpnodeid,
    ss.name as STUDY_name,
    ss.interfacename,
    ss.ctglabel,
    ss.simdate,
    ss.simhour,
    ss.RUNID
FROM study_shifts ss
INNER JOIN DART_shifts ds
    ON ss.interfacename = ds.interfacename
    AND ss.cpnodeid = ds.cpnodeid
    AND ss.simdate = ds.simdate
    AND ss.simhour = ds.simhour
INNER JOIN DART_shifts ref
    ON ss.simdate = ref.simdate
    AND ss.simhour = ref.simhour
    AND ref.psenshiftid = ds.psenshiftid
    AND ref.cpnodeid = {reference_cpnodeid}
WHERE 1=1
    {hour_filter}
    AND ABS(ss.psens + ref.psen - ds.psen) > {psen_threshold}
ORDER BY
    ABS(ss.psens + ref.psen - ds.psen) DESC,
    ss.simdate DESC,
    ss.simhour DESC
"""

    logging.info(f"Benchmarking interface shifts for study {study_id}, interface '{interface_name}', ctg '{ctg_label}'")
    logging.info(f"Date range: {start_date} to {end_date}")

    # Execute query using Snowflake
    df = sf.performQuery('AW', query)
    logging.info(f"Found {len(df)} interface shift comparisons with difference > {psen_threshold}")

    return df


def visualize_errors_over_time(results_df, viz_type='all', width=1200, height=800, save_dir=None, save_format='html'):
    """
    Visualize shift factor errors over time using plotly (interactive plots).

    Best practices for scientific visualization:
    1. Time series with quartile bands - shows central tendency and spread
    2. Box plots by time period - shows distribution and outliers clearly
    3. Heatmap - reveals patterns across time and categories
    4. CDF (Cumulative Distribution Function) - shows error distribution

    Parameters:
    -----------
    results_df : pandas.DataFrame
        Output from benchmark_shifts() or benchmark_interface_shifts()
    viz_type : str
        Type of visualization: 'timeseries', 'boxplot', 'heatmap', 'cdf', 'all'
    width : int
        Figure width in pixels (default: 1200)
    height : int
        Figure height in pixels (default: 800)
    save_dir : str, optional
        Directory path to save plots. If None, plots are not saved (default: None)
    save_format : str, optional
        Format to save plots: 'html', 'png', 'svg', 'pdf' (default: 'html')
        Note: Static formats (png, svg, pdf) require kaleido package

    Returns:
    --------
    plotly.graph_objects.Figure or dict of Figures
    """
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    # Create datetime column
    results_df = results_df.copy()
    results_df['datetime'] = pd.to_datetime(results_df['simdate']) + pd.to_timedelta(results_df['simhour'], unit='h')

    figures = {}

    # 1. TIME SERIES WITH PERCENTILE BANDS (Best for journals - shows trends and uncertainty)
    if viz_type in ['timeseries', 'all']:
        # Aggregate by datetime
        time_stats = results_df.groupby('datetime')['PSEN_DIFFERENCE'].agg([
            ('mean', 'mean'),
            ('median', 'median'),
            ('p25', lambda x: x.quantile(0.25)),
            ('p75', lambda x: x.quantile(0.75)),
            ('p95', lambda x: x.quantile(0.95)),
            ('max', 'max'),
            ('count', 'count')
        ]).reset_index()

        # Create subplots
        fig1 = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=('Error Distribution Over Time', 'Sample Count'),
            vertical_spacing=0.12
        )

        # Upper plot: Error metrics over time
        # 25th-75th percentile band
        fig1.add_trace(go.Scatter(
            x=time_stats['datetime'], y=time_stats['p75'],
            mode='lines', line=dict(width=0), showlegend=False,
            hovertemplate='75th: %{y:.6f}<extra></extra>'
        ), row=1, col=1)

        fig1.add_trace(go.Scatter(
            x=time_stats['datetime'], y=time_stats['p25'],
            mode='lines', line=dict(width=0),
            fill='tonexty', fillcolor='rgba(0,100,250,0.2)',
            name='25th-75th Percentile',
            hovertemplate='25th: %{y:.6f}<extra></extra>'
        ), row=1, col=1)

        # Mean line
        fig1.add_trace(go.Scatter(
            x=time_stats['datetime'], y=time_stats['mean'],
            mode='lines+markers', name='Mean Error',
            line=dict(color='rgb(255,65,54)', width=2),
            marker=dict(size=6),
            hovertemplate='Mean: %{y:.6f}<extra></extra>'
        ), row=1, col=1)

        # Median line
        fig1.add_trace(go.Scatter(
            x=time_stats['datetime'], y=time_stats['median'],
            mode='lines+markers', name='Median Error',
            line=dict(color='rgb(133,20,75)', width=2, dash='dot'),
            marker=dict(size=5, symbol='square'),
            hovertemplate='Median: %{y:.6f}<extra></extra>'
        ), row=1, col=1)

        # 95th percentile line
        fig1.add_trace(go.Scatter(
            x=time_stats['datetime'], y=time_stats['p95'],
            mode='lines', name='95th Percentile',
            line=dict(color='rgb(0,147,146)', width=2, dash='dash'),
            hovertemplate='95th: %{y:.6f}<extra></extra>'
        ), row=1, col=1)

        # Lower plot: Sample count
        fig1.add_trace(go.Bar(
            x=time_stats['datetime'], y=time_stats['count'],
            name='Sample Count', marker=dict(color='steelblue'),
            hovertemplate='Count: %{y}<extra></extra>',
            showlegend=False
        ), row=2, col=1)

        # Update layout
        fig1.update_xaxes(title_text='Date-Time', row=2, col=1, title_font=dict(size=14))
        fig1.update_yaxes(title_text='|PSEN Difference|', row=1, col=1, title_font=dict(size=14))
        fig1.update_yaxes(title_text='Sample Count', row=2, col=1, title_font=dict(size=14))

        fig1.update_layout(
            title=dict(text='Shift Factor Error Distribution Over Time', font=dict(size=18)),
            height=height,
            width=width,
            hovermode='x unified',
            template='plotly_white',
            legend=dict(x=1.02, y=1, xanchor='left', yanchor='top')
        )

        figures['timeseries'] = fig1

    # 2. BOX PLOTS BY HOUR (Shows distribution - excellent for comparing time periods)
    if viz_type in ['boxplot', 'all']:
        results_df['simhour_str'] = results_df['simhour'].astype(str)

        fig2 = go.Figure()

        # Create box plot for each hour with custom hover data
        for hour in sorted(results_df['simhour'].unique()):
            hour_df = results_df[results_df['simhour'] == hour]

            # Prepare custom data for hover: date and node name
            customdata = np.column_stack((
                hour_df['simdate'].astype(str),
                hour_df['STUDY_NAME']
            ))

            fig2.add_trace(go.Box(
                y=hour_df['PSEN_DIFFERENCE'],
                name=str(hour),
                boxmean=True,
                marker_color='lightseagreen',
                customdata=customdata,
                hovertemplate='<b>Hour %{x}</b><br>' +
                              'Error: %{y:.6f}<br>' +
                              'Date: %{customdata[0]}<br>' +
                              'Node: %{customdata[1]}<extra></extra>'
            ))

        fig2.update_layout(
            title=dict(text='Error Distribution by Hour', font=dict(size=18)),
            xaxis=dict(title='Hour of Day', title_font=dict(size=14)),
            yaxis=dict(title='|PSEN Difference|', title_font=dict(size=14)),
            height=int(height*0.7),
            width=width,
            showlegend=False,
            template='plotly_white',
            hovermode='closest'
        )

        figures['boxplot'] = fig2

    # 3. HEATMAP (Reveals temporal patterns)
    if viz_type in ['heatmap', 'all']:
        # Create pivot table for heatmap
        results_df['date_only'] = results_df['simdate'].astype(str)
        pivot_data = results_df.pivot_table(
            values='PSEN_DIFFERENCE',
            index='simhour',
            columns='date_only',
            aggfunc='mean'
        )

        fig3 = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='YlOrRd',
            colorbar=dict(title='Mean |PSEN<br>Difference|'),
            hovertemplate='Date: %{x}<br>Hour: %{y}<br>Mean Error: %{z:.6f}<extra></extra>'
        ))

        fig3.update_layout(
            title=dict(text='Error Heatmap: Hour vs Date', font=dict(size=18)),
            xaxis=dict(title='Date', title_font=dict(size=14)),
            yaxis=dict(title='Hour of Day', title_font=dict(size=14)),
            height=height,
            width=width,
            template='plotly_white'
        )

        figures['heatmap'] = fig3

    # 4. CUMULATIVE DISTRIBUTION FUNCTION (Shows error distribution - key for journals)
    if viz_type in ['cdf', 'all']:
        sorted_errors = np.sort(results_df['PSEN_DIFFERENCE'])
        cdf = np.arange(1, len(sorted_errors) + 1) / len(sorted_errors) * 100

        p95_val = np.percentile(sorted_errors, 95)
        p99_val = np.percentile(sorted_errors, 99)

        fig4 = go.Figure()

        # CDF line
        fig4.add_trace(go.Scatter(
            x=sorted_errors, y=cdf,
            mode='lines', name='CDF',
            line=dict(color='darkblue', width=3),
            hovertemplate='Error: %{x:.6f}<br>Percentile: %{y:.2f}%<extra></extra>'
        ))

        # 95th percentile line
        fig4.add_hline(
            y=95, line_dash='dash', line_color='red',
            annotation_text=f'95th: {p95_val:.6f}',
            annotation_position='right'
        )

        # 99th percentile line
        fig4.add_hline(
            y=99, line_dash='dash', line_color='orange',
            annotation_text=f'99th: {p99_val:.6f}',
            annotation_position='right'
        )

        fig4.update_layout(
            title=dict(text='Cumulative Distribution of Errors', font=dict(size=18)),
            xaxis=dict(title='|PSEN Difference|', title_font=dict(size=14), rangemode='tozero'),
            yaxis=dict(title='Cumulative Percentage (%)', title_font=dict(size=14)),
            height=int(height*0.7),
            width=int(width*0.8),
            template='plotly_white',
            hovermode='x'
        )

        figures['cdf'] = fig4

    # Save plots if save_dir is provided
    if save_dir is not None:
        import os
        os.makedirs(save_dir, exist_ok=True)

        # Determine the naming convention based on data type
        if 'interfacename' in results_df.columns:
            # Interface/GTC data
            interface_name = results_df['interfacename'].iloc[0]
            ctg_label = results_df['ctglabel'].iloc[0] if results_df['ctglabel'].iloc[0] else 'ALL_CTG'
            name_prefix = f"{interface_name}_{ctg_label}"
        elif 'branchlabel' in results_df.columns:
            # Branch data
            branch_label = results_df['branchlabel'].iloc[0]
            ctg_label = results_df['ctglabel'].iloc[0]
            name_prefix = f"{branch_label}_{ctg_label}"
        else:
            name_prefix = "shift_errors"

        # Clean up name_prefix (remove invalid filename characters)
        name_prefix = name_prefix.replace('/', '_').replace('\\', '_').replace(':', '_').replace(' ', '_')

        for plot_name, fig in figures.items():
            filename = f"{name_prefix}_{plot_name}.{save_format}"
            filepath = os.path.join(save_dir, filename)

            try:
                if save_format == 'html':
                    fig.write_html(filepath)
                else:
                    # Requires kaleido: pip install kaleido
                    fig.write_image(filepath)
                logging.info(f"Saved {plot_name} plot to: {filepath}")
            except Exception as e:
                logging.error(f"Failed to save {plot_name} plot: {e}")
                if save_format != 'html':
                    logging.error("For static image formats (png, svg, pdf), install kaleido: pip install kaleido")

    if viz_type == 'all':
        return figures
    else:
        return figures[viz_type]


def analyze_shift_errors(results_df):
    """
    Provide statistical summary of shift comparison errors.

    Parameters:
    -----------
    results_df : pandas.DataFrame
        Output from benchmark_shifts() or benchmark_interface_shifts()

    Returns:
    --------
    dict
        Dictionary containing statistical summary metrics
    """

    if results_df.empty:
        logging.warning("Empty results DataFrame provided")
        return {}

    # Create datetime column for easier analysis
    results_df['datetime'] = pd.to_datetime(results_df['simdate']) + pd.to_timedelta(results_df['simhour'], unit='h')

    # Calculate statistics
    stats = {
        'total_comparisons': len(results_df),
        'unique_datetimes': results_df['datetime'].nunique(),
        'unique_dates': results_df['simdate'].nunique(),
        'unique_hours': results_df['simhour'].nunique(),
        'date_range': f"{results_df['simdate'].min()} to {results_df['simdate'].max()}",

        # Absolute highest error
        'max_error': results_df['PSEN_DIFFERENCE'].max(),
        'max_error_row': results_df.loc[results_df['PSEN_DIFFERENCE'].idxmax()].to_dict(),

        # Date-hour pair with most aggregate error
        'datetime_errors': results_df.groupby('datetime')['PSEN_DIFFERENCE'].agg(['sum', 'mean', 'count', 'max']).sort_values('sum', ascending=False),

        # Node with most aggregate error
        'node_errors': results_df.groupby('STUDY_NAME')['PSEN_DIFFERENCE'].agg(['sum', 'mean', 'count', 'max']).sort_values('sum', ascending=False),

        # Overall error statistics
        'error_mean': results_df['PSEN_DIFFERENCE'].mean(),
        'error_median': results_df['PSEN_DIFFERENCE'].median(),
        'error_std': results_df['PSEN_DIFFERENCE'].std(),
        'error_95th_percentile': results_df['PSEN_DIFFERENCE'].quantile(0.95),
        'error_99th_percentile': results_df['PSEN_DIFFERENCE'].quantile(0.99),
    }

    # Print summary
    print("=" * 80)
    print("SHIFT FACTOR BENCHMARK ERROR ANALYSIS")
    print("=" * 80)
    print(f"\nTotal Comparisons: {stats['total_comparisons']:,}")
    print(f"Unique Date-Time Pairs: {stats['unique_datetimes']}")
    print(f"Date Range: {stats['date_range']}")
    print(f"Hours Analyzed: {sorted(results_df['simhour'].unique())}")

    print("\n" + "-" * 80)
    print("ERROR STATISTICS")
    print("-" * 80)
    print(f"Maximum Error: {stats['max_error']:.6f}")
    print(f"Mean Error: {stats['error_mean']:.6f}")
    print(f"Median Error: {stats['error_median']:.6f}")
    print(f"Std Dev: {stats['error_std']:.6f}")
    print(f"95th Percentile: {stats['error_95th_percentile']:.6f}")
    print(f"99th Percentile: {stats['error_99th_percentile']:.6f}")

    print("\n" + "-" * 80)
    print("MAXIMUM ERROR OCCURRENCE")
    print("-" * 80)
    max_err_row = stats['max_error_row']
    print(f"Error: {max_err_row['PSEN_DIFFERENCE']:.6f}")
    print(f"Node: {max_err_row['STUDY_NAME']}")
    print(f"Date-Time: {max_err_row['datetime']}")
    if 'branchlabel' in max_err_row:
        print(f"Branch: {max_err_row.get('branchlabel', 'N/A')}")
    if 'interfacename' in max_err_row:
        print(f"Interface: {max_err_row.get('interfacename', 'N/A')}")
    print(f"Contingency: {max_err_row['ctglabel']}")

    print("\n" + "-" * 80)
    print("TOP 5 DATE-HOURS BY TOTAL ERROR")
    print("-" * 80)
    top_datetimes = stats['datetime_errors'].head()
    for dt, row in top_datetimes.iterrows():
        print(f"{dt}: Sum={row['sum']:.4f}, Mean={row['mean']:.6f}, Count={int(row['count'])}, Max={row['max']:.6f}")

    print("\n" + "-" * 80)
    print("TOP 10 NODES BY TOTAL ERROR")
    print("-" * 80)
    top_nodes = stats['node_errors'].head(10)
    for node, row in top_nodes.iterrows():
        print(f"{node}: Sum={row['sum']:.4f}, Mean={row['mean']:.6f}, Count={int(row['count'])}, Max={row['max']:.6f}")

    print("\n" + "=" * 80)

    return stats


def main():
    # Machine-specific path (original notebook host)
    teid_map = pd.read_csv(r'c:\CimInsight_v1.25.0_win10-x64\Storage\CIM_Jan_ML1_MarketModel_01132026_Redacted\CIM_Jan_ML1_MarketModel_01132026_Redacted_20260101-0700_TeidMap.csv')
    teid_map = teid_map.loc[(teid_map['PsseType'] == 'Branch'), ['Substation1', 'Substation2', 'CircuitIdentifier', 'TransmissionElementId']]

    sql = """SELECT DISTINCT
        cd.isoconstraintname,
        stations.from_station,
        stations.to_station,
        b.branchid,
        b.branchname,
        b.teid,
        CASE
            -- WHEN (ied.fromStationName = stations.from_station) AND (ied.toStationName <> stations.to_station) THEN 1
            WHEN (ied.fromStationName = stations.from_station) AND (ied.toStationName = stations.to_station) THEN 1
            WHEN (ied.toStationName = stations.from_station) AND (ied.fromStationName = stations.to_station) THEN -1
            -- WHEN (ied.toStationName = stations.from_station) AND (ied.fromStationName <> stations.to_station) THEN -1
            ELSE 0
        END as direction,
        CASE
            WHEN cdc.congContName = 'BASE CASE' THEN 'Base Case'
            ELSE cdc.congContName
        END as ctgLabel,
        b.ckt,
        bm.branchMonitoredID as outBranchID,
        cdc.congContID as outCtgID,
    FROM AW.dbo.psenShiftDef AS psd
    INNER JOIN AW.DBO.congDefConstraint as cd
        ON cd.congConstraintID = psd.congConstraintID
    INNER JOIN AW.DBO.congDefMonitor cdm
        ON cdm.congMontID = cd.congMontID
    INNER JOIN AW.DBO.congDefContingency cdc
        ON cdc.congContID = cd.congContID
    INNER JOIN AW.DBO.branchMonitored bm
        ON bm.branchMonitoredID = cdm.branchMonitoredId
    INNER JOIN aw.dbo.branchContingency bc
        ON bc.branchContingencyID = cdc.branchContingencyId
    INNER JOIN AW.DBO.branch b
        ON b.branchID = bm.branchID
    INNER JOIN aw.dbo.isoErcotSeBranchDevice ied
        ON ied.branchID = b.branchID
    INNER JOIN AW.DBO.congHrPrice chp
        ON chp.congConstraintID = psd.congConstraintID
    INNER JOIN AW.DBO.awDate ad
        ON ad.awDateID = chp.awDateID
    , LATERAL (
        SELECT
            TRIM(SPLIT_PART(SPLIT_PART(cd.isoconstraintname, '[', 2), ':', 1)) AS from_station,
            TRIM(SPLIT_PART(SPLIT_PART(SPLIT_PART(cd.isoconstraintname, '-', 2), ':', 1), ' KV', 1)) AS to_station
    ) AS stations
    WHERE psd.isoMarketID = 6
        AND psd.psenShiftTypeId = 14
        AND psd.extractionBegin >= '2026-06-01'
        AND psd.extractionEnd <= '2026-06-20'
    """
    constraint_list = sf.performQuery('AW', sql)

    print(constraint_list)

    constraint_list_from_to = constraint_list.merge(teid_map, left_on=['from_station', 'to_station', 'ckt'], right_on=['Substation1', 'Substation2', 'CircuitIdentifier'], how='inner')
    constraint_list_to_from = constraint_list.merge(teid_map, left_on=['to_station', 'from_station',  'ckt'], right_on=['Substation1', 'Substation2', 'CircuitIdentifier'], how='inner')

    constraint_list = pd.concat([constraint_list_from_to, constraint_list_to_from], ignore_index=True)

    constraint_list['cim_direction'] = constraint_list.apply(lambda x: 1 if ((x['from_station'] == x['Substation1']) & (x['to_station'] == x['Substation2'])) else 0, axis=1)
    constraint_list['cim_direction'] = constraint_list.apply(lambda x: -1 if ((x['from_station'] == x['Substation2']) & (x['to_station'] == x['Substation1'])) else x['cim_direction'], axis=1)
    constraint_list['flip_direcion'] = constraint_list.apply(lambda x: 1 if (x['cim_direction'] == x['direction']) else -1, axis=1)

    print(constraint_list[(constraint_list['direction'] != 0) & (constraint_list['flip_direcion'] == -1)].head(10))

    # Run benchmark with the same parameters as the original query
    results_df = benchmark_shifts(
        study_id=12712,
        branch_label='BI_WAP50',
        ctg_label='SBISMI5',
        start_date='2026-01-01',
        end_date='2026-01-20',
        sign_in_study=1,
        reference_cpnodeid=12791,
        sim_hour=None,
        psen_threshold=0.0,
        filter_deadbus=True
    )

    # Display results
    print(f"\nTotal comparisons found: {len(results_df)}")
    print(f"\nTop 10 largest differences:")
    print(results_df.head(10))

    figs = visualize_errors_over_time(results_df, viz_type='all',)
    figs['boxplot'].show()

    # Example usage for interface benchmarking:
    interface_results = benchmark_interface_shifts(
        study_id=12712,
        interface_name='E_PASP',
        ctg_label=None,  # or specific contingency, or None for all
        start_date='2026-01-01',
        end_date='2026-01-20',
        sign_in_study=1,
        reference_cpnodeid=12791,
        sim_hour=None,  # or None for all hours
        psen_threshold=0.00,
        filter_deadbus=True
    )

    # Example usage of analysis and visualization functions:

    # Run analysis
    stats = analyze_shift_errors(interface_results)

    # Access specific statistics
    print(f"\nWorst datetime: {stats['datetime_errors'].index[0]}")
    print(f"Worst node: {stats['node_errors'].index[0]}")

    # Create all visualizations (plotly - interactive!)
    # Machine-specific path (original notebook host)
    visualize_errors_over_time(interface_results, viz_type='timeseries', save_dir=r'G:\ERCOT\Research\FTR Auctions\2025_12_JAN2026 Monthly Auction\BackTest', save_format='html')
    # Machine-specific path (original notebook host)
    visualize_errors_over_time(interface_results, viz_type='boxplot', save_dir=r'G:\ERCOT\Research\FTR Auctions\2025_12_JAN2026 Monthly Auction\BackTest', save_format='html')

    figs = visualize_errors_over_time(interface_results, viz_type='all',)

    # Display individual plots
    figs['timeseries'].show()
    figs['boxplot'].show()
    # figs['heatmap'].show()
    # figs['cdf'].show()

    # Example: Save plots to directory
    # save_directory = r"C:\Users\sdalvi\Code\appianwaycode3\ISO\Ercot\misc\plots"
    #
    # # Save as interactive HTML (default)
    # figs_saved = visualize_errors_over_time(
    #     interface_results,
    #     viz_type='all',
    #     save_dir=save_directory,
    #     save_format='html'  # Creates interactive HTML files
    # )
    #
    # # Or save as static images (requires kaleido: pip install kaleido)
    # # figs_saved = visualize_errors_over_time(
    # #     interface_results,
    # #     viz_type='all',
    # #     save_dir=save_directory,
    # #     save_format='png'  # Options: 'png', 'svg', 'pdf'
    # # )


if __name__ == "__main__":
    main()
