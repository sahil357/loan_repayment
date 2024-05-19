from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from loan.serializers import LoanListingAdminSerializer, LoanListingSerializer, \
     LoanStatusSerializer, LoanRepaymentScheduleSerializer, LoanRepaymentSerializer
from user.models import CustomerUser
from loan.models import Loan, LoanRepaymentSchedule

class LoanViewSet(viewsets.ViewSet):

    def get_default_admin(self, data):
        admin_username = data.get('admin_username', None)
        if not admin_username or not CustomerUser.objects.filter(username=admin_username, is_superuser=True):
            return CustomerUser.objects.filter(is_superuser=True).last()
        return CustomerUser.objects.filter(username=admin_username, is_superuser=True).last()

    @action(detail=False, methods=['post'], url_path='submit', url_name='submit')
    def submit_loan(self, request):
        request.data['customer'] = request.user.id
        request.data['admin'] = self.get_default_admin(request.data).id
        serializer = LoanListingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='admin/list', url_name='admin-list')
    def get_loan_listing_for_admin(self, request):
        data = Loan.objects.filter(admin=request.user)
        serializer = LoanListingAdminSerializer(data, many=True)
        # serializer.is_valid(raise_exception=True)
        return Response({'data':serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='customer/list', url_name='customer-list')
    def get_loan_listing_for_customer(self, request):
        data = Loan.objects.filter(customer=request.user)
        serializer = LoanListingSerializer(data, many=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], url_path='status',  url_name='status')
    def update_status(self, request):
        instance = Loan.objects.filter(id=request.data.get('loan_id'), admin=request.user).last()
        if not instance:
            return Response({"message": "Invalid Loan Id"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoanStatusSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Loan status updated"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='repayments',  url_name='repayments')
    def list_repayments(self, request):
        data = LoanRepaymentSchedule.objects.filter(loan__customer=request.user,
                                                    loan__admin_approval_status=2).order_by('scheduled_repayment_date')
        serializer = LoanRepaymentScheduleSerializer(data, many=True)
        # serializer.is_valid(raise_exception=True)
        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put'], url_path='repayment-status', url_name='repayment-status')
    def update_repayments(self, request):
        try:
            instance = LoanRepaymentSchedule.objects.filter(id=request.data.get('scheduled_id')).last()
            if not instance:
                return Response({"error": "Invalid Loan Repayment Id"}, status=status.HTTP_400_BAD_REQUEST)

            if instance.loan.admin_approval_status != 2:
                return Response({"error": "Loan is not approved yet"}, status=status.HTTP_400_BAD_REQUEST)

            serializer = LoanRepaymentSerializer(instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Loan Repayment status updated"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


