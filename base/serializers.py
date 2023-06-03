from rest_framework import serializers
from .models import ExecutiveMember, Practitioner, Activity, FinancialStatement, Transfer, Semso

class ExecutiveMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExecutiveMember
        fields = '__all__'


class PractitionerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practitioner
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = '__all__'


class FinancialStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialStatement
        fields = '__all__'


class TransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transfer
        fields = '__all__'


class SemsoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semso
        fields = '__all__'
