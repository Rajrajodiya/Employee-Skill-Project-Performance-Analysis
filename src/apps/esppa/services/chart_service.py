"""
Service for generating matplotlib charts rendered as base64-encoded PNG images.
All charting logic is isolated here so views never touch matplotlib directly.
"""

import base64
import logging
from io import BytesIO
from typing import Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

CHART_DPI = 200
BAR_COLOR = 'skyblue'
BAR_EDGE = 'navy'
HIST_COLOR = 'lightgreen'
HIST_EDGE = 'darkgreen'
SALARY_COLOR = 'gold'
SALARY_EDGE = 'orange'
PIE_CMAP = 'Set3'


class ChartService:
    """Generates analytical charts as base64-encoded PNG strings."""

    @staticmethod
    def department_bar_chart(df: pd.DataFrame) -> Optional[str]:
        """Bar chart of employee count per department."""
        try:
            counts = df['Department'].value_counts()
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(counts.index, counts.values,
                   color=BAR_COLOR, edgecolor=BAR_EDGE)
            ax.set_title('Employee Count by Department',
                         fontsize=16, fontweight='bold')
            ax.set_xlabel('Department', fontsize=12)
            ax.set_ylabel('Number of Employees', fontsize=12)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', alpha=0.3)
            for i, v in enumerate(counts.values):
                ax.text(i, v + 0.5, str(v), ha='center',
                        va='bottom', fontweight='bold')
            plt.tight_layout()
            return ChartService._fig_to_base64(fig)
        except Exception as exc:
            logger.error("Department bar chart failed: %s", exc)
            return None

    @staticmethod
    def department_pie_chart(df: pd.DataFrame) -> Optional[str]:
        """Pie chart of employee distribution by department."""
        try:
            counts = df['Department'].value_counts()
            fig, ax = plt.subplots(figsize=(10, 8))
            cmap = plt.colormaps[PIE_CMAP]
            colors = cmap(np.linspace(0, 1, len(counts)))
            ax.pie(counts.values, labels=counts.index,
                   autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('Employee Distribution by Department',
                         fontsize=16, fontweight='bold')
            plt.tight_layout()
            return ChartService._fig_to_base64(fig)
        except Exception as exc:
            logger.error("Department pie chart failed: %s", exc)
            return None

    @staticmethod
    def performance_histogram(df: pd.DataFrame) -> Optional[str]:
        """Histogram of performance scores with mean overlay."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df['Performance_Score'], bins=20,
                    color=HIST_COLOR, edgecolor=HIST_EDGE, alpha=0.7)
            ax.set_title('Performance Score Distribution',
                         fontsize=16, fontweight='bold')
            ax.set_xlabel('Performance Score', fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            ax.grid(axis='y', alpha=0.3)
            mean_val = df['Performance_Score'].mean()
            ax.axvline(mean_val, color='red', linestyle='--',
                       linewidth=2, label=f'Mean: {mean_val:.2f}')
            ax.legend()
            plt.tight_layout()
            return ChartService._fig_to_base64(fig)
        except Exception as exc:
            logger.error("Performance histogram failed: %s", exc)
            return None

    @staticmethod
    def salary_histogram(df: pd.DataFrame) -> Optional[str]:
        """Histogram of monthly salary with mean overlay."""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df['Monthly_Salary'], bins=25,
                    color=SALARY_COLOR, edgecolor=SALARY_EDGE, alpha=0.7)
            ax.set_title('Monthly Salary Distribution',
                         fontsize=16, fontweight='bold')
            ax.set_xlabel('Monthly Salary ($)', fontsize=12)
            ax.set_ylabel('Frequency', fontsize=12)
            ax.grid(axis='y', alpha=0.3)
            mean_val = df['Monthly_Salary'].mean()
            ax.axvline(mean_val, color='red', linestyle='--',
                       linewidth=2, label=f'Mean: ${mean_val:,.0f}')
            ax.legend()
            plt.tight_layout()
            return ChartService._fig_to_base64(fig)
        except Exception as exc:
            logger.error("Salary histogram failed: %s", exc)
            return None

    @staticmethod
    def _fig_to_base64(fig: plt.Figure) -> str:
        """Render a matplotlib Figure to a base64-encoded PNG string."""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=CHART_DPI,
                    bbox_inches='tight')
        buffer.seek(0)
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close(fig)
        return encoded
