"""
Analysis serializer — single responsibility: Analysis record serialization.
"""

from rest_framework import serializers

from apps.esppa.models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Analysis
        fields = ['id', 'analysis_type', 'chart_type', 'chart_data',
                  'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_by', 'created_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)
