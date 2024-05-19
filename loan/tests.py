from django.urls import reverse
from rest_framework import status
# from rest_framework.tests import APITestCase, APIClient
from user.tests import UserCreateTest
from user.models import CustomerUser
from loan.models import Loan, LoanRepaymentSchedule

class LoanCreateTest(UserCreateTest):

    def login_admin_and_create(self):
        self.test_login_admin()
        self.test_login_customer()

    def test_submit_loan_application(self):
        self.login_admin_and_create()
        url = reverse('loan-submit')
        data = {
            "amount_required": 10000000,
            "loan_term": 5
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.post(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('data', response.data)

    def test_submit_loan_application_custom_admin(self):
        self.login_admin_and_create()
        url = reverse('loan-submit')
        data = {
            "amount_required": 10000000,
            "loan_term": 5,
            "admin_username": "admin"
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.post(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['data']), 12)

    def test_submit_loan_application_failed(self):
        self.login_admin_and_create()
        url = reverse('loan-submit')
        data = {
            "amount_required": 10000000,
            "loan_term": "FIVE"
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.post(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_loan_status(self):
        self.test_submit_loan_application()
        url = reverse('loan-status')
        data = {
            "loan_id": 1,
            "status": "APPROVED"
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=True).token
        }
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Loan status updated")

    def test_update_loan_status_invalid_loan_id(self):
        self.test_submit_loan_application_failed()
        url = reverse('loan-status')
        data = {
            "loan_id": 1,
            "status": "APPROVED"
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=True).token
        }
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_loan_status_invalid_status(self):
        self.test_submit_loan_application()
        url = reverse('loan-status')
        data = {
            "loan_id": 1,
            "status": "RANDOM"
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=True).token
        }
        response = self.client.put(url, data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_loan_listing_admin(self):
        self.test_submit_loan_application()
        url = reverse('loan-admin-list')
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=True).token
        }
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_loan_listing_customer(self):
        self.test_submit_loan_application()
        url = reverse('loan-customer-list')
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)

    def test_loan_repayment_listing(self):
        self.test_update_loan_status()
        url = reverse('loan-repayments')
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.get(url, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 5)

    def test_update_repayment_status_invalid_input(self):
        self.test_update_loan_status()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": "11",
            "repayment_amount": 1000000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Invalid Loan Repayment Id")

    def test_update_repayment_status_invalid_scheduled_id(self):
        self.test_update_loan_status()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 1,
            "repayment_amount": "invalid_input"
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_repayment_status_not_approved(self):
        self.test_submit_loan_application()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 1,
            "repayment_amount": 1000000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "Loan is not approved yet")

    def test_update_repayment_failed_with_less_amount(self):
        self.test_update_loan_status()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 1,
            "repayment_amount": 1000000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_repayment(self):
        self.test_update_loan_status()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 1,
            "repayment_amount": 2000000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Loan Repayment status updated")

    def test_update_repayment_with_more_amount(self):
        self.test_update_repayment()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 2,
            "repayment_amount": 2500000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Loan Repayment status updated")
        self.assertEqual(int(Loan.objects.get().extra_credit_amount), 500000)

    def test_update_repayment_with_less_amount(self):
        self.test_update_repayment_with_more_amount()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 3,
            "repayment_amount": 1500000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Loan Repayment status updated")
        self.assertEqual(int(Loan.objects.get().extra_credit_amount), 0)

    def test_update_repayment_and_not_update_loan_status(self):
        self.test_update_repayment_with_less_amount()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 4,
            "repayment_amount": 2000000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Loan Repayment status updated")
        self.assertEqual(Loan.objects.get().payment_status, 1)

    def test_not_update_repayment_for_already_updated_repayment(self):
        self.test_update_repayment_and_not_update_loan_status()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 4,
            "repayment_amount": 2000000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], "Repayment for this schedule is already done")

    def test_update_repayment_and_update_loan_status(self):
        self.test_update_repayment_and_not_update_loan_status()
        url = reverse('loan-repayment-status')
        data = {
            "scheduled_id": 5,
            "repayment_amount": 2000000
        }
        headers = {
            'Token': CustomerUser.objects.get(is_superuser=False).token
        }
        response = self.client.put(url, data=data, headers=headers, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], "Loan Repayment status updated")
        self.assertEqual(Loan.objects.get().payment_status, 2)


