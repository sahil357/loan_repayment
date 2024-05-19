from rest_framework import serializers
from loan.models import Loan, LoanRepaymentSchedule

REVERSE_ADMIN_APPROVAL_STATUS = {}
for key, value in dict(Loan.ADMIN_APPROVAL_STATUS).items():
    REVERSE_ADMIN_APPROVAL_STATUS[value] = key

class LoanListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['payment_frequency'] = dict(Loan.PAYMENT_FREQUENCY).get(representation['payment_frequency'], '')
        representation['admin_approval_status'] = dict(Loan.ADMIN_APPROVAL_STATUS
                                                       ).get(representation['admin_approval_status'], '')
        representation['payment_status'] = dict(Loan.PAYMENT_STATUS).get(representation['payment_status'], '')
        return representation


class LoanListingAdminSerializer(LoanListingSerializer):
    customer_username = serializers.SerializerMethodField()

    def get_customer_username(self, obj):
        return obj.customer.username if obj.customer and obj.customer.username else None

    class Meta:
        model = Loan
        fields = ['id', 'amount_required', 'loan_term', 'payment_frequency',
                  'admin_approval_status', 'customer_username', 'payment_status']


class LoanStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(required=True, choices=REVERSE_ADMIN_APPROVAL_STATUS)

    def validate_status(self, value):
        return REVERSE_ADMIN_APPROVAL_STATUS.get(value, None)

    def update(self, instance, validated_data):
        instance.admin_approval_status = validated_data['status']
        instance.save()
        return instance


class LoanRepaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepaymentSchedule
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['status'] = dict(LoanRepaymentSchedule.PAYMENT_STATUS).get(representation['status'], '')
        return representation


class LoanRepaymentSerializer(serializers.Serializer):
    scheduled_id = serializers.IntegerField(required=True)
    repayment_amount = serializers.DecimalField(required=True, max_digits=20, decimal_places=2)

    def validate_scheduled_id(self, value):
        return LoanRepaymentSchedule.objects.filter(id=value).last()

    def update(self, instance, validated_data):
        if instance.status == 2:
            raise ValueError("Repayment for this schedule is already done")

        loan = instance.loan
        value = validated_data['repayment_amount']
        if value < instance.scheduled_repayment_amount:
            total_value = float(value) + float(loan.extra_credit_amount)
            if total_value < instance.scheduled_repayment_amount:
                raise ValueError("Invalid repayment_amount, Please add alteast {} amount "
                                 "more".format(float(instance.scheduled_repayment_amount - total_value)))

        instance.repayment_amount = validated_data['repayment_amount']
        if validated_data['repayment_amount'] < instance.scheduled_repayment_amount:
            loan.extra_credit_amount = float(loan.extra_credit_amount) - (float(instance.scheduled_repayment_amount) -
                                                                          float(validated_data['repayment_amount']))
            loan.save()
        elif validated_data['repayment_amount'] > instance.scheduled_repayment_amount:
            loan.extra_credit_amount = loan.extra_credit_amount + (float(validated_data['repayment_amount']) -
                                                                   float(instance.scheduled_repayment_amount))

            loan.save()
        instance.status = 2
        instance.save()

        loan_schedule = LoanRepaymentSchedule.objects.filter(loan=instance.loan, status__in=[0, 1])
        if not loan_schedule:
            loan = instance.loan
            loan.payment_status = 2
            loan.save()
        return instance
