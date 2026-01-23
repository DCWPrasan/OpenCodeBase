from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from AdminApp.models import T72Purchase, T72Status, T72ItemIssuedHistory
from .serializers import (
    T72CreateUpdateSerializer,
    T72ListSerializer,
    SearchUserSerializer,
    T72ItemIssuedHistorySerializer,
)
from AdminApp.pagination import CustomPagination
from AuthApp.models import Users


class T72ListCreateAPIView(APIView, CustomPagination):

    def get(self, request):
        query = request.GET.get("query")
        qs = T72Purchase.objects.prefetch_related("items").all().order_by("-id")

        if query:
            qs = qs.filter(
                Q(party_name__icontains=query)
                | Q(items__item_name__icontains=query)
                | Q(daybook_number__icontains=query)
                | Q(order_number__icontains=query)
                | Q(challan_number__icontains=query)
                | Q(remarks__icontains=query)
                | Q(used_area__icontains=query)
                | Q(authorized_by__name__icontains=query)
            ).distinct()

        status_param = request.GET.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        page = self.paginate_queryset(qs, request, view=self)
        serializer = T72ListSerializer(page, many=True)
        result = self.get_paginated_response(serializer.data)
        data = result.data["results"]  # pagination data
        total = result.data["count"]  # pagination data
        response = {
            "success": True,
            "message": "Products List Get Succesfully",
            "data": data,
            "total": total,
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = T72CreateUpdateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "T-72 Created"}, status=201)
        return Response(serializer.errors, status=400)


class T72DetailAPIView(APIView):

    def get_object(self, pk):
        return T72Purchase.objects.get(pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        serializer = T72CreateUpdateSerializer(obj)
        return Response(serializer.data)

    def put(self, request, pk):
        obj = self.get_object(pk)

        if obj.status != T72Status.RECEIVED:
            return Response({"error": "Cannot not edit this T72 Order"}, status=400)

        serializer = T72CreateUpdateSerializer(
            obj, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Updated"})
        return Response(serializer.errors, status=400)


class T72RemarkAPIView(APIView):
    def patch(self, request, pk):
        try:
            obj = T72Purchase.objects.get(pk=pk)
            remarks = request.data.get("remarks")
            obj.remarks = remarks
            obj.save()
            return Response({"message": "Remarks updated"})
        except T72Purchase.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)


class T72IssueAPIView(APIView):

    def post(self, request, pk):
        try:
            t72 = T72Purchase.objects.get(pk=pk)
        except T72Purchase.DoesNotExist:
            return Response({"error": "T72 Entry not found"}, status=404)

        items_to_issue = request.data.get("items", [])
        received_by_id = request.data.get("received_by")
        # issued_by is the logged in user

        if not items_to_issue:
            return Response({"error": "No items selected for issuance"}, status=400)

        if not received_by_id:
            return Response({"error": "Received By (Employee) is required"}, status=400)

        # Validate Employee
        from AdminApp.models import Employees, T72PurchaseItem, T72ItemIssuedHistory

        try:
            employee = Employees.objects.get(id=received_by_id)
        except Employees.DoesNotExist:
            return Response({"error": "Invalid Employee ID"}, status=400)

        # Process Issuance
        from django.db import transaction

        try:
            with transaction.atomic():
                for item_data in items_to_issue:
                    item_id = item_data.get("id")
                    issue_qty = float(item_data.get("quantity", 0))

                    if issue_qty <= 0:
                        continue

                    t72_item = T72PurchaseItem.objects.get(pk=item_id, purchase=t72)

                    if issue_qty > t72_item.available_quantity:
                        raise ValueError(
                            f"Insufficient quantity for {t72_item.item_name}"
                        )

                    # Create History
                    T72ItemIssuedHistory.objects.create(
                        purchase=t72,
                        item=t72_item,
                        quantity=issue_qty,
                        issue_by=request.user,
                        received_by=employee,
                    )

                    from decimal import Decimal

                    t72_item.available_quantity -= Decimal(str(issue_qty))
                    t72_item.save()

                # Update T72 Status
                # Check if all items are fully issued (available_quantity == 0)
                all_items = t72.items.all()
                total_available = sum(item.available_quantity for item in all_items)

                if total_available == 0:
                    t72.status = T72Status.ISSUED
                elif total_available < sum(item.quantity for item in all_items):
                    t72.status = T72Status.PARTIALLY_ISSUED
                # Else remains RECEIVED (if nothing happened, but we checked issue_qty > 0)

                t72.save()

            return Response({"message": "Items Issued Successfully"})

        except ValueError as e:
            return Response({"error": str(e)}, status=400)
        except Exception as e:
            print(e)
            return Response({"error": str(e)}, status=500)


class T72DashboardAPIView(APIView):

    def get(self, request):
        total_orders = T72Purchase.objects.count()
        received = T72Purchase.objects.filter(status=T72Status.RECEIVED).count()
        partial_issued = T72Purchase.objects.filter(
            status=T72Status.PARTIALLY_ISSUED
        ).count()
        issued = T72Purchase.objects.filter(status=T72Status.ISSUED).count()

        return Response(
            {
                "total_orders": total_orders,
                "received": received,
                "partial_issued": partial_issued,
                "issued": issued,
            }
        )


class SearchUserAPIView(APIView):
    serializer_class = SearchUserSerializer

    def get(self, request):
        try:
            instance = Users.objects.filter(role="User").order_by("name")
            serializer = self.serializer_class(instance, many=True)
            data = serializer.data
            response = {
                "success": True,
                "message": "User List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


from django.http import HttpResponse
from datetime import datetime
import pandas as pd


class T72IssuedHistoryListAPIView(APIView, CustomPagination):

    def get(self, request):
        queryset = T72ItemIssuedHistory.objects.all().order_by("-issue_at", "-id")

        order_id = request.query_params.get("t72_order_id")
        if order_id:
            queryset = queryset.filter(purchase__id=order_id)

        query = request.query_params.get("query")
        if query:
            queryset = queryset.filter(
                Q(purchase__order_number__icontains=query)
                | Q(item__item_name__icontains=query)
                | Q(received_by__name__icontains=query)
                | Q(issue_by__name__icontains=query)
            )

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            queryset = queryset.filter(issue_at__range=[from_date, to_date])

        result_page = self.paginate_queryset(queryset, request)
        serializer = T72ItemIssuedHistorySerializer(result_page, many=True)
        return self.get_paginated_response(serializer.data)


class T72IssuedHistoryExportAPIView(APIView):

    def get(self, request):
        queryset = T72ItemIssuedHistory.objects.all().order_by("-issue_at", "-id")

        order_id = request.query_params.get("t72_order_id")
        if order_id:
            queryset = queryset.filter(purchase__id=order_id)

        query = request.query_params.get("query")
        if query:
            queryset = queryset.filter(
                Q(purchase__order_number__icontains=query)
                | Q(item__item_name__icontains=query)
                | Q(received_by__name__icontains=query)
                | Q(issue_by__name__icontains=query)
            )

        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        if from_date and to_date:
            queryset = queryset.filter(issue_at__range=[from_date, to_date])

        data = []
        for history in queryset:
            data.append(
                {
                    "Order No": history.purchase.order_number,
                    "Item Name": history.item.item_name,
                    "Quantity": history.quantity,
                    "Unit": history.item.unit,
                    "Issued By": history.issue_by.name if history.issue_by else "",
                    "Received By": (
                        history.received_by.name if history.received_by else ""
                    ),
                    "Issue Date": (
                        history.issue_at.strftime("%Y-%m-%d")
                        if history.issue_at
                        else ""
                    ),
                }
            )

        df = pd.DataFrame(data)
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"T72_Issued_History_{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        df.to_excel(response, index=False)
        return response
