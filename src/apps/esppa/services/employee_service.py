"""
Service encapsulating employee query, metrics, and aggregation logic.
Views call this service instead of directly querying the Employee model.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List

import pandas as pd

from .config import (
    PERFORMANCE_HIGH_THRESHOLD,
    PERFORMANCE_MEDIUM_THRESHOLD,
    SALARY_HIGH_THRESHOLD_USD,
    SALARY_MEDIUM_THRESHOLD_USD,
    USD_TO_INR_RATE,
)

logger = logging.getLogger(__name__)


@dataclass
class DepartmentMetrics:
    """Aggregated metrics for a single department."""
    name: str
    count: int
    performance: float
    performance_width: float
    salary_inr: float


@dataclass
class DashboardMetrics:
    """Top-level dashboard KPIs."""
    total_employees: int = 0
    avg_performance: float = 0.0
    avg_salary_inr: float = 0.0
    resignation_rate: float = 0.0
    department_data: List[DepartmentMetrics] = field(default_factory=list)
    gender_counts: Dict[str, int] = field(default_factory=dict)
    education_counts: Dict[str, int] = field(default_factory=dict)
    high_performers: int = 0
    medium_performers: int = 0
    low_performers: int = 0
    high_salary: int = 0
    medium_salary: int = 0
    low_salary: int = 0


class EmployeeService:
    """Business-logic service over employee / CSV data."""

    @staticmethod
    def build_dashboard_metrics(df: pd.DataFrame) -> DashboardMetrics:
        """Compute all KPIs from the raw CSV DataFrame."""
        total = len(df)
        avg_perf = float(df['Performance_Score'].mean())
        avg_sal = float(df['Monthly_Salary'].mean())
        avg_sal_inr = avg_sal * USD_TO_INR_RATE
        resign_rate = (
            (df['Resigned'].sum() / total * 100) if total > 0 else 0
        )

        # Department breakdown
        dept_counts = df['Department'].value_counts().to_dict()
        dept_perf = df.groupby('Department')['Performance_Score'].mean().to_dict()
        dept_sal = df.groupby('Department')['Monthly_Salary'].mean().to_dict()

        department_data = [
            DepartmentMetrics(
                name=dept,
                count=dept_counts[dept],
                performance=dept_perf.get(dept, 0),
                performance_width=min(100, max(0, dept_perf.get(dept, 0) * 20)),
                salary_inr=dept_sal.get(dept, 0) * USD_TO_INR_RATE,
            )
            for dept in dept_counts
        ]

        # Performance categories
        high_p = int((df['Performance_Score'] >= PERFORMANCE_HIGH_THRESHOLD).sum())
        med_p = int(
            ((df['Performance_Score'] >= PERFORMANCE_MEDIUM_THRESHOLD)
             & (df['Performance_Score'] < PERFORMANCE_HIGH_THRESHOLD)).sum()
        )
        low_p = int((df['Performance_Score'] < PERFORMANCE_MEDIUM_THRESHOLD).sum())

        # Salary ranges (USD)
        high_s = int((df['Monthly_Salary'] >= SALARY_HIGH_THRESHOLD_USD).sum())
        med_s = int(
            ((df['Monthly_Salary'] >= SALARY_MEDIUM_THRESHOLD_USD)
             & (df['Monthly_Salary'] < SALARY_HIGH_THRESHOLD_USD)).sum()
        )
        low_s = int((df['Monthly_Salary'] < SALARY_MEDIUM_THRESHOLD_USD).sum())

        return DashboardMetrics(
            total_employees=total,
            avg_performance=round(avg_perf, 2),
            avg_salary_inr=round(avg_sal_inr, 0),
            resignation_rate=round(resign_rate, 2),
            department_data=department_data,
            gender_counts=df['Gender'].value_counts().to_dict(),
            education_counts=df['Education_Level'].value_counts().to_dict(),
            high_performers=high_p,
            medium_performers=med_p,
            low_performers=low_p,
            high_salary=high_s,
            medium_salary=med_s,
            low_salary=low_s,
        )
