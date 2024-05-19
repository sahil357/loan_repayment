from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class CommonDetails(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

class Loan(CommonDetails):
    PAYMENT_FREQUENCY = (
        (1, 'Weekly'),
        (2, 'Monthly'),
        (3, 'Yearly'),
    )

    ADMIN_APPROVAL_STATUS = (
        (1, 'PENDING'),
        (2, 'APPROVED'),
        (0, 'FAILED'),
    )
    PAYMENT_STATUS = (
        (0, 'FAILED'),
        (2, 'PAID'),
        (1, 'PENDING')
    )

    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_loans')
    customer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='customer_loans')
    amount_required = models.PositiveIntegerField()
    loan_term = models.SmallIntegerField(default=1)
    payment_frequency = models.SmallIntegerField(choices=PAYMENT_FREQUENCY, default=1)
    admin_approval_status = models.SmallIntegerField(choices=ADMIN_APPROVAL_STATUS, default=1)
    payment_status = models.SmallIntegerField(choices=PAYMENT_STATUS, default=1)
    extra_credit_amount = models.FloatField(default=0)

    def __str__(self):
        return '{} - {}({})'.format(self.customer.username, self.amount_required, self.loan_term)

    def save(self, *args, **kwargs):
        create_loan_repayment = False
        if not self.id:
            create_loan_repayment = True
        super(Loan, self).save(*args, **kwargs)
        if create_loan_repayment:
            self.create_loan_repayment()

    def create_loan_repayment(self):
        loan_date = self.created_at
        for term in range(1, self.loan_term + 1):
            scheduled_repayment_date = loan_date + timedelta(days=(7*term))
            scheduled_repayment_amount = round((self.amount_required/self.loan_term), 2)
            LoanRepaymentSchedule.objects.create(loan=self,
                                                 scheduled_repayment_amount=scheduled_repayment_amount,
                                                 scheduled_repayment_date=scheduled_repayment_date)


class LoanRepaymentSchedule(CommonDetails):
    PAYMENT_STATUS = (
        (0, 'FAILED'),
        (2, 'PAID'),
        (1, 'PENDING')
    )
    loan = models.ForeignKey(Loan, on_delete=models.PROTECT, related_name='loan_repayment_schedules')
    scheduled_repayment_amount = models.FloatField(default=0)
    scheduled_repayment_date = models.DateField()
    status = models.SmallIntegerField(choices=PAYMENT_STATUS, default=1)
    repayment_amount = models.FloatField(default=None, null=True, blank=True)

    def __str__(self):
        return "{} - {}({})".format(str(self.loan.id), str(self.scheduled_repayment_amount),
                                    self.scheduled_repayment_date.strftime('%d/%b/%Y'))


