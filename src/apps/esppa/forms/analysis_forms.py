"""
Analysis form — single responsibility: analysis type and chart type selection.
"""

from django import forms


class AnalysisForm(forms.Form):
    """Form for selecting analysis type and chart type."""
    analysis_type = forms.ChoiceField(
        choices=[('department', 'Department Analysis'), ('performance', 'Performance Analysis'),
                 ('salary', 'Salary Analysis'), ('overtime', 'Overtime Analysis'),
                 ('satisfaction', 'Satisfaction Analysis'), ('overall', 'Overall Analysis')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    chart_type = forms.ChoiceField(
        choices=[('bar', 'Bar Chart'), ('histogram', 'Histogram'), ('pie', 'Pie Chart'),
                 ('box', 'Box Plot'), ('heatmap', 'Heatmap'), ('scatter', 'Scatter Plot'),
                 ('line', 'Line Chart')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
