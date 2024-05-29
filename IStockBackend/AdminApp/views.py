from django.db import transaction
from .serializers import (
    ProductsSerializer,
    ProductsDetailsSerializer,
    RacksSerializer,
    SearchRacksSerializer,
    StocksSerializer,
    StocksHistorySerializer,
    BarcodeSerializer,
    RacksProductDetailsSerializer,
    EmployeeSerializer,
    UserSerializer,
    DesignationSerializer,
    UnitSerializer,
    ProductCategorySerializer,
    SearchEmployeeSerializer,
    ReportMaterialSerializer,
    ReportMaterialTransacrionSerializer,
    SearchMaterialSerializer,
    ReportFastReceiveMovingItemSerializer,
    CrirticalReorderItemSerializer,
    ReportEmployeeSerializer,
    ReportMaterialUsageSerializer,
    ReportDeadStockItemSerializer,

)
from rest_framework.views import APIView
from rest_framework.response import Response
from .pagination import CustomPagination
from .models import (
    Products,
    Racks,
    Stocks,
    StocksHistory,
    Barcodes,
    ProductCategory,
    Employees,
    Unit
)
from AuthApp.models import Users, Designation
from django.db.models import (
    Q,
    Sum,
    Count,
    F,
    ExpressionWrapper,
    FloatField,
    Max,
    CharField,
    Window,
)
from django.db.models.functions import Coalesce, Rank
from AdminApp.utils import Syserror
from datetime import datetime, timedelta, date
import calendar
import re
#import pandas as pd


def get_number_of_days(year, month):
    _, num_days = calendar.monthrange(year, month)
    return num_days


class DashboardView(APIView):
    def get(self, request):
        try:
            today_date = datetime.now().date()
            stock_history = (
                StocksHistory.objects.select_related("stock")
                .filter(created_at__date=today_date)
                .aggregate(
                    stock_in=Sum("quantity", filter=Q(is_stock_out=False)),
                    stock_out=Sum("quantity", filter=Q(is_stock_out=True)),
                )
            )

            prod = Products.objects.filter(net_quantity__gt=0).aggregate(
                under_stock=Count("id", filter=Q(net_quantity__lt=F("min_threshold"))),
                over_stock=Count("id", filter=Q(net_quantity__gt=F("max_threshold"))),
                in_stock=Count(
                    "id",
                    filter=Q(
                        net_quantity__lt=F("max_threshold"),
                        net_quantity__gt=F("min_threshold"),
                    ),
                ),
            )

            data = {
                "today_stock_in": stock_history["stock_in"] or 0,
                "today_stock_out": stock_history["stock_out"] or 0,
                "total_product": Products.objects.count(),
                "under_stock": prod["under_stock"] or 0,
                "over_stock": prod["over_stock"] or 0,
                "in_stock": prod["in_stock"] or 0,
            }
            response = {
                "success": True,
                "message": "Dashboard Count",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DashboardProductUsesView(APIView):
    def get(self, request):
        try:
            view_type = request.GET.get("view_type", "weekly")
            stock_type = request.GET.get("stock_type", "stockout")
            if view_type == "weekly":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=8)
                if stock_type in ["stockin", "stockout"]:
                    data = (
                        Products.objects.annotate(
                            quantity=Coalesce(
                                Sum(
                                    "stocks__stockshistory__quantity",
                                    filter=Q(
                                        stocks__stockshistory__is_stock_out=stock_type
                                        == "stockout",
                                        stocks__stockshistory__created_at__date__gte=to_date,
                                        stocks__stockshistory__created_at__date__lte=from_date,
                                    ),
                                ),
                                0,
                            )
                        )
                        .order_by("-quantity")
                        .values("name", "id", "quantity")[:10]
                    )
                else:
                    data = (
                        Products.objects.annotate(
                            quantity=Coalesce(
                                Sum(
                                    "stocks__stockshistory__quantity",
                                    filter=Q(
                                        stocks__stockshistory__created_at__date__gte=to_date,
                                        stocks__stockshistory__created_at__date__lte=from_date,
                                    ),
                                ),
                                0,
                            )
                        )
                        .filter(quantity=0)
                        .values("name", "id", "quantity")[:10]
                    )

            elif view_type == "monthly":
                this_month = datetime.now().month
                this_year = datetime.now().year
                if stock_type in ["stockin", "stockout"]:
                    data = (
                        Products.objects.annotate(
                            quantity=Coalesce(
                                Sum(
                                    "stocks__stockshistory__quantity",
                                    filter=Q(
                                        stocks__stockshistory__is_stock_out=stock_type
                                        == "stockout",
                                        stocks__stockshistory__created_at__month=this_month,
                                        stocks__stockshistory__created_at__year=this_year,
                                    ),
                                ),
                                0,
                            )
                        )
                        .order_by("-quantity")
                        .values("name", "id", "quantity")[:10]
                    )
                else:
                    data = (
                        Products.objects.annotate(
                            quantity=Coalesce(
                                Sum(
                                    "stocks__stockshistory__quantity",
                                    filter=Q(
                                        stocks__stockshistory__created_at__month=this_month,
                                        stocks__stockshistory__created_at__year=this_year,
                                    ),
                                ),
                                0,
                            )
                        )
                        .filter(quantity=0)
                        .values("name", "id", "quantity")[:10]
                    )
            else:
                this_year = datetime.now().year
                if stock_type in ["stockin", "stockout"]:
                    data = (
                        Products.objects.annotate(
                            quantity=Coalesce(
                                Sum(
                                    "stocks__stockshistory__quantity",
                                    filter=Q(
                                        stocks__stockshistory__is_stock_out=stock_type
                                        == "stockout",
                                        stocks__stockshistory__created_at__year=this_year,
                                    ),
                                ),
                                0,
                            )
                        )
                        .order_by("-quantity")
                        .values("name", "id", "quantity")[:10]
                    )
                else:
                    data = (
                        Products.objects.annotate(
                            quantity=Coalesce(
                                Sum(
                                    "stocks__stockshistory__quantity",
                                    filter=Q(
                                        stocks__stockshistory__created_at__year=this_year
                                    ),
                                ),
                                0,
                            )
                        )
                        .filter(quantity=0)
                        .values("name", "id", "quantity")[:10]
                    )

            response = {
                "success": True,
                "message": "Dashboard Count",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DashboardProductOverStockView(APIView):
    def get(self, request):
        try:
            stock_type = request.GET.get("stock_type", "stockunder")
            if stock_type == "stockunder":
                data = (
                    Products.objects.filter(net_quantity__lt=F("min_threshold"))
                    .annotate(quantity=F("min_threshold") - F("net_quantity"))
                    .order_by("-quantity")
                    .values("name", "id", "quantity")[:10]
                )
            else:
                data = (
                    Products.objects.filter(net_quantity__gt=F("max_threshold"))
                    .annotate(quantity=(F("max_threshold") - F("net_quantity")))
                    .order_by("-quantity")
                    .values("name", "id", "quantity")[:10]
                )

            response = {
                "success": True,
                "message": "Dashboard Overstock under Stock",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DashboardStockOverViewView(APIView):
    def get(self, request, id=None):
        try:
            view_type = request.GET.get("view_type", "weekly")

            cumulative_stock = 0
            stock_in_list = []
            stock_out_list = []
            carry_forward_list = []
            labels = []

            if view_type == "weekly":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=6)
                prev_date = from_date - timedelta(days=7)

                prev_f = Q(created_at__date__lte=prev_date)
                if id:
                    prev_f &= Q(stock__product__id=id)

                if (
                    prev_stock := StocksHistory.objects.select_related("stock")
                    .filter(prev_f)
                    .aggregate(
                        total=Coalesce(
                            Sum("quantity", filter=Q(is_stock_out=False))
                            - Sum("quantity", filter=Q(is_stock_out=True)),
                            0,
                        )
                    )
                ):
                    cumulative_stock = prev_stock["total"]

                date_list = [
                    to_date + timedelta(days=x)
                    for x in range((from_date - to_date).days + 1)
                ]
                for i in date_list:
                    f = Q(created_at__date=i)
                    if id:
                        f &= Q(stock__product__id=id)
                    stock_item = (
                        StocksHistory.objects.select_related("stock")
                        .filter(f)
                        .values("created_at__date")
                        .aggregate(
                            stock_in=Coalesce(
                                Sum("quantity", filter=Q(is_stock_out=False)), 0
                            ),
                            stock_out=Coalesce(
                                Sum("quantity", filter=Q(is_stock_out=True)), 0
                            ),
                        )
                    )
                    stock_in = stock_item["stock_in"]
                    stock_out = stock_item["stock_out"]
                    cumulative_stock = cumulative_stock + stock_in - stock_out

                    stock_in_list.append(stock_in)
                    stock_out_list.append(stock_out)
                    carry_forward_list.append(cumulative_stock)
                    labels.append(i.strftime("%d-%b"))

            elif view_type == "monthly":
                m = datetime.now().strftime("%m")
                y = datetime.now().strftime("%Y")
                this_year_date = datetime(int(y) - 1, int(m), 1)
                prev_year_date = this_year_date - timedelta(days=1)
                prev_f = Q(created_at__lte=prev_year_date)
                if id:
                    prev_f &= Q(stock__product__id=id)
                if (
                    prev_stock := StocksHistory.objects.select_related("stock")
                    .filter(prev_f)
                    .aggregate(
                        total=Coalesce(
                            Sum("quantity", filter=Q(is_stock_out=False))
                            - Sum("quantity", filter=Q(is_stock_out=True)),
                            0,
                        )
                    )
                ):
                    cumulative_stock = prev_stock["total"]

                for i in range(13):
                    if i != 0:
                        this_year_date = this_year_date + timedelta(
                            days=get_number_of_days(
                                this_year_date.year, this_year_date.month
                            )
                        )
                    this_year = this_year_date.strftime("%Y")
                    this_month = this_year_date.strftime("%m")

                    lbl_mon = date(int(this_year), int(this_month), 1).strftime("%b")
                    lbl_year = date(int(this_year), int(this_month), 1).strftime("%Y")

                    labels.append(f"{lbl_mon}-{lbl_year}")
                    f = Q(created_at__month=this_month, created_at__year=this_year)
                    if id:
                        f &= Q(stock__product__id=id)

                    stock_history = (
                        StocksHistory.objects.select_related("stock")
                        .filter(f)
                        .aggregate(
                            stock_in=Coalesce(
                                Sum("quantity", filter=Q(is_stock_out=False)), 0
                            ),
                            stock_out=Coalesce(
                                Sum("quantity", filter=Q(is_stock_out=True)), 0
                            ),
                        )
                    )

                    stock_in = stock_history["stock_in"]
                    stock_out = stock_history["stock_out"]
                    cumulative_stock = cumulative_stock + stock_in - stock_out

                    stock_in_list.append(stock_in)
                    stock_out_list.append(stock_out)
                    carry_forward_list.append(cumulative_stock)
            else:
                from_year = datetime.now().strftime("%Y")
                to_year = f"{int(from_year)-10}"
                prev_year = f"{int(from_year)-11}"

                f = Q(created_at__year__gte=to_year)
                if id:
                    f &= Q(stock__product__id=id)
                stock_history = (
                    StocksHistory.objects.select_related("stock")
                    .filter(f)
                    .values("created_at__year")
                    .annotate(
                        stock_in=Coalesce(
                            Sum("quantity", filter=Q(is_stock_out=False)), 0
                        ),
                        stock_out=Coalesce(
                            Sum("quantity", filter=Q(is_stock_out=True)), 0
                        ),
                    )
                    .order_by("created_at__year")
                )

                prev_f = Q(created_at__year__lte=prev_year)
                if id:
                    prev_f &= Q(stock__product__id=id)

                if (
                    prev_stock := StocksHistory.objects.select_related("stock")
                    .filter(prev_f)
                    .aggregate(
                        total=Coalesce(
                            Sum("quantity", filter=Q(is_stock_out=False))
                            - Sum("quantity", filter=Q(is_stock_out=True)),
                            0,
                        )
                    )
                ):
                    cumulative_stock = prev_stock["total"]

                for stock_item in stock_history:
                    stock_in = stock_item["stock_in"]
                    stock_out = stock_item["stock_out"]
                    cumulative_stock = cumulative_stock + stock_in - stock_out

                    stock_in_list.append(stock_in)
                    stock_out_list.append(stock_out)
                    carry_forward_list.append(cumulative_stock)
                    labels.append(stock_item["created_at__year"])

            data = {
                "labels": labels,
                "total_stock_in": sum(stock_in_list),
                "total_stock_out": sum(stock_out_list),
                "total_product_quantity": cumulative_stock,
                "quantity": sum(stock_out_list),
                "series": [
                    {
                        "name": "Total Stock",
                        "data": carry_forward_list,
                        "type": "column",
                    },
                    {"name": "Stock IN", "data": stock_in_list, "type": "area"},
                    {"name": "Stock OUT", "data": stock_out_list, "type": "line"},
                ],
            }
            response = {
                "success": True,
                "message": "Dashboard Count",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class RacksView(APIView, CustomPagination):
    serializer_class = RacksSerializer

    def get(self, request, id=None):
        try:
            if id:
                if rack := Racks.objects.filter(id=id).first():
                    products = Products.objects.filter(stocks__rack=rack).distinct()
                    product_data = RacksProductDetailsSerializer(
                        products, many=True, context={"rack_id": id}
                    ).data
                    response = {
                        "success": True,
                        "message": "Rack get successfully",
                        "data": {
                            "rack": {
                                "rack_no": rack.rack_no,
                                "barcode": rack.barcode.barcode_no,
                            },
                            "products": product_data,
                        },
                    }
                    return Response(response, status=200)
                else:
                    response = {"success": False, "message": "Rack Not found"}
                    return Response(response, status=400)

            if query := request.GET.get("query"):
                instance = Racks.objects.select_related().filter(
                    Q(rack_no__icontains=query)
                    | Q(barcode__barcode_no__icontains=query)
                )
            else:
                instance = Racks.objects.select_related()
            instance = instance.annotate(
                product=Count("stocks__product", distinct=True),
                most_product_qunatity=Max("stocks__product__net_quantity"),
                # most_product_name="None",
                # most_product_name=Max(
                #     "stocks__product__name",
                #     filter=Q(stocks__product__net_quantity=F("stocks__product__net_quantity")),
                # ),
            ).order_by("rack_no")
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "Rack List Get Succesfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                rack_no = data.get("rack_no", None)
                barcode_no = data.get("barcode_no", None)
                if not all([rack_no, barcode_no]):
                    response = {
                        "success": False,
                        "message": "Required All Field",
                    }
                    return Response(response, status=400)
                barcode = Barcodes.objects.filter(
                    barcode_no=barcode_no, is_product_type=False
                ).first()
                if not barcode:
                    response = {
                        "success": False,
                        "message": "Invalid barcode",
                    }
                    return Response(response, status=400)
                if Racks.objects.filter(
                    Q(rack_no=rack_no) | Q(barcode=barcode)
                ).exists():
                    response = {
                        "success": False,
                        "message": "Rack no or barcode no already exists",
                    }
                    return Response(response, status=400)
                instance = Racks.objects.create(rack_no=rack_no, barcode=barcode)
                barcode.status = "Used"
                barcode.save()
                response = {
                    "success": True,
                    "message": "Rack Created  Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                rack_id = data.get("rack_id", None)
                rack_no = data.get("rack_no", None)
                barcode_no = data.get("barcode_no", None)
                if not all([rack_no, barcode_no, rack_id]):
                    response = {
                        "success": False,
                        "message": "Required All Field",
                    }
                    return Response(response, status=400)
                instance = Racks.objects.get(id=rack_id)
                if (
                    Racks.objects.filter(rack_no=rack_no)
                    .exclude(rack_no=instance.rack_no)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Rack No already exists",
                    }
                    return Response(response, status=400)
                barcode = Barcodes.objects.filter(
                    barcode_no=barcode_no, is_product_type=False
                ).first()
                if not barcode:
                    response = {
                        "success": False,
                        "message": "Invalid barcode",
                    }
                    return Response(response, status=400)

                if (
                    Racks.objects.filter(barcode=barcode)
                    .exclude(barcode=instance.barcode)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Barcode already exists",
                    }
                    return Response(response, status=400)
                instance.barcode = barcode
                instance.rack_no = rack_no
                instance.save()
                if barcode.status != "Used":
                    barcode.status = "Used"
                    barcode.save()
                response = {
                    "success": True,
                    "message": "Rack Updated Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def delete(self, request, id):
        try:
            with transaction.atomic():
                instance = Racks.objects.get(id=id)
                response = {
                    "success": True,
                    "message": "Rack Deleted Successfully",
                }
                instance.delete()
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ProductsView(APIView, CustomPagination):
    serializer_class = ProductsSerializer

    def get(self, request, id=None):
        try:
            if id:
                if rack_id := request.GET.get("rack_id", None):
                    stocks = (
                        Stocks.objects.select_related("product", "rack")
                        .filter(product=id, rack=rack_id)
                        .values("barcode__barcode_no", "quantity", "rack__rack_no")
                        .order_by("-quantity")
                    )
                    response = {
                        "success": True,
                        "message": "Products Stock List Get Succesfully",
                        "data": stocks,
                    }
                    return Response(response, status=200)
                instance = Products.objects.get(id=id)
                racks = (
                    Racks.objects.filter(stocks__product__id=id)
                    .annotate(net_quantity=Sum("stocks__quantity"))
                    .filter(net_quantity__gt=0)
                    .values("id", "rack_no", "net_quantity")
                )
                history = (
                    StocksHistory.objects.select_related("stock")
                    .filter(stock__product__id=id)
                    .order_by("-created_at")[:10]
                )
                product_serializer = ProductsDetailsSerializer(instance)
                history_serializer = StocksHistorySerializer(history, many=True)
                data = {
                    "product": product_serializer.data,
                    "racks": racks,
                    "histories": history_serializer.data,
                }
                response = {
                    "success": True,
                    "message": "Products Get Succesfully",
                    "data": data,
                }
                return Response(response, status=200)
            f = Q()
            if query := request.GET.get("query"):
                f &= Q(
                    Q(name__icontains=query)
                    | Q(net_quantity__icontains=query)
                    | Q(ucs_code__icontains=query)
                    | Q(description__icontains=query)
                    | Q(description_sap__icontains=query)
                    | Q(price__icontains=query)
                    | Q(category__name__icontains=query)
                )
            if stock_type := request.GET.get("stock_type"):
                if stock_type == "Under Stock":
                    f &= Q(net_quantity__lt=F("min_threshold"))
                elif stock_type == "Over Stock":
                    f &= Q(net_quantity__gt=F("max_threshold"))
                elif stock_type == "In Stock":
                    f &= Q(
                        net_quantity__gte=F("min_threshold"),
                        net_quantity__lte=F("max_threshold"),
                    )

            instance = (
                Products.objects.select_related().filter(f).order_by("-created_at")
            )
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "Products List Get Succesfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None) or None
                category_id = data.get("category", None) or None
                description = data.get("description", None) or None
                sap_description = data.get("sap_description", None) or None
                if price := data.get("price", None) or 0:
                    price = int(price) if isinstance(price, str) else price
                min_threshold = data.get("min_threshold", None) or None
                max_threshold = data.get("max_threshold", None) or None
                unit = data.get("unit", None) or None
                ved_category = data.get("ved_category", None) or None
                if lead_time := data.get("lead_time", None) or 1:
                    lead_time = (
                        int(lead_time) if isinstance(lead_time, str) else lead_time
                    )
                ucs_code = data.get("ucs_code", None) or None
                if not all(
                    [
                        name,
                        min_threshold,
                        ucs_code,
                        unit,
                    ]
                ):
                    response = {
                        "success": False,
                        "message": "Required All Mandatory fields",
                    }
                    return Response(response, status=400)
                if price and price <= 0:
                    response = {
                        "success": False,
                        "message": "Price must be greater than zero",
                    }
                    return Response(response, status=400)

                if price and lead_time <= 0:
                    response = {
                        "success": False,
                        "message": "Lead Time must be greater than zero",
                    }
                    return Response(response, status=400)

                if ved_category and ved_category not in ["Vital", "Essential", "Desirable"]:
                    response = {"success": False,"message": "Invalid VED category"}
                    return Response(response, status=400)

                if unit_type := data.get("unit_type", "mutli"):
                    unit_type = isinstance(unit_type, str) and unit_type == "multi"
                if category_id:
                    product_category = ProductCategory.objects.get(id=category_id)
                else:
                    product_category = None
                unit  = Unit.objects.filter(id = unit).first()
                if unit is None:
                    response = {"success": False,"message": "Invalid Unit"}
                    return Response(response, status=400)
                
                instance = Products.objects.create(
                    name=name,
                    description=description,
                    description_sap=sap_description,
                    min_threshold=min_threshold,
                    max_threshold=max_threshold,
                    price=price,
                    lead_time=lead_time,
                    ved_category=ved_category,
                    is_mutli_type_unit=unit_type,
                    unit=unit,
                    category=product_category,
                    ucs_code=ucs_code,
                )
                response = {
                    "success": True,
                    "message": "Products Created  Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                product_id = data.get("product_id", None)
                name = data.get("name", None) or None
                category_id = data.get("category", None) or None
                description = data.get("description", None) or None
                sap_description = data.get("sap_description", None) or None
                if price := data.get("price", None) or 0:
                    price = int(price) if isinstance(price, str) else price
                min_threshold = data.get("min_threshold", None) or None
                max_threshold = data.get("max_threshold", None) or None
                unit = data.get("unit", None) or None
                ved_category = data.get("ved_category", None) or None
                if lead_time := data.get("lead_time", None) or 1:
                    lead_time = (
                        int(lead_time) if isinstance(lead_time, str) else lead_time
                    )
                ucs_code = data.get("ucs_code", None) or None
                if not all(
                    [   product_id,
                        name,
                        min_threshold,
                        ucs_code,
                        unit
                    ]
                ):
                    response = {
                        "success": False,
                        "message": "Required All fields",
                    }
                    return Response(response, status=400)
                if price and price <= 0:
                    response = {
                        "success": False,
                        "message": "Price must be greater than zero",
                    }
                    return Response(response, status=400)

                if lead_time and lead_time <= 0:
                    response = {
                        "success": False,
                        "message": "Lead Time must be greater than zero",
                    }
                    return Response(response, status=400)

                if ved_category not in ["Vital", "Essential", "Desirable"]:
                    response = {
                        "success": False,
                        "message": "Invalid VED category",
                    }
                    return Response(response, status=400)

                if unit_type := data.get("unit_type", False):
                    unit_type = isinstance(unit_type, str) and unit_type == "multi"
                if category_id:
                    product_category = ProductCategory.objects.get(id=category_id)
                else:
                    product_category = None
                unit = Unit.objects.filter(id = unit).first()
                instance = Products.objects.get(id=product_id)
                instance.name = name
                instance.description = description
                instance.description_sap = sap_description
                instance.min_threshold = min_threshold
                instance.max_threshold = max_threshold
                instance.price = price
                instance.is_mutli_type_unit = unit_type
                instance.unit = unit
                instance.ved_category = ved_category
                instance.lead_time = lead_time
                instance.category = product_category
                instance.ucs_code = ucs_code
                instance.save()
                response = {
                    "success": True,
                    "message": "Product Updated Successfully",
                    "data": ProductsDetailsSerializer(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def delete(self, request, id):
        try:
            with transaction.atomic():
                instance = Products.objects.get(id=id)
                response = {
                    "success": True,
                    "message": "Products Deleted Successfully",
                }
                instance.delete()
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    # upload excel file
    def patch(self, request):
        try:
            with transaction.atomic():
                file = request.FILES.get("file", None)
                if not file:
                    response = {
                        "success": False,
                        "message": "Required a Excel File",
                    }
                    return Response(response, status=400)
                df = pd.read_excel(file)
                error_list = []
                for index, data in df.iterrows():
                    name = data.get("name", None)
                    category = data.get("category", None)
                    description = data.get("description", None)
                    sap_description = data.get("sap_description", None)
                    if price := data.get("price", None):
                        price = int(price) if isinstance(price, str) else price
                    min_threshold = data.get("min_threshold", None)
                    max_threshold = data.get("max_threshold", None)
                    unit = data.get("unit", None)
                    ved_category = data.get("ved_category", None)
                    if lead_time := data.get("lead_time", None):
                        lead_time = (
                            int(lead_time) if isinstance(lead_time, str) else lead_time
                        )
                    ucs_code = data.get("ucs_code", None)
                    if not all(
                        [
                            name,
                            ved_category,
                            lead_time,
                            description,
                            sap_description,
                            category,
                            price,
                            min_threshold,
                            max_threshold,
                            ucs_code,
                            unit,
                        ]
                    ):
                        errors = {"row": index + 1, "message": "Required All fields"}
                        error_list.append(errors)
                        continue
                    if price <= 0:
                        errors = {
                            "row": index + 1,
                            "message": "Price must be greater than zero",
                        }
                        error_list.append(errors)
                        continue
                    if lead_time <= 0:
                        errors = {
                            "row": index + 1,
                            "message": "Lead Time must be greater than zero",
                        }
                        error_list.append(errors)
                        continue
                    if ved_category not in ["Vital", "Essential", "Desirable"]:
                        errors = {"row": index + 1, "message": "Invalid VED category"}
                        error_list.append(errors)
                        continue
                    if Products.objects.filter(ucs_code=ucs_code).exists():
                        errors = {
                            "row": index + 1,
                            "message": "UCS Code already exists",
                        }
                        error_list.append(errors)
                        continue

                    if unit_type := data.get("unit_type", False):
                        unit_type = isinstance(unit_type, str) and unit_type == "Multi"

                    (
                        product_category,
                        created_p_cat,
                    ) = ProductCategory.objects.get_or_create(name=category)

                    instance = Products.objects.create(
                        name=name,
                        description=description,
                        description_sap=sap_description,
                        min_threshold=min_threshold,
                        max_threshold=max_threshold,
                        price=price,
                        lead_time=lead_time,
                        ved_category=ved_category,
                        is_mutli_type_unit=unit_type,
                        unit=unit,
                        category=product_category or created_p_cat,
                        ucs_code=ucs_code,
                    )
                response = {
                    "success": True,
                    "message": "Products Created  Successfully",
                    "data": error_list,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class StocksView(APIView, CustomPagination):
    serializer_class = StocksSerializer

    def get(self, request, id=None):
        try:
            if id:
                instance = Stocks.objects.get(id=id)
                serializer = ProductsDetailsSerializer(instance)
                response = {
                    "success": True,
                    "message": "Products Get Succesfully",
                    "data": serializer.data,
                }
                return Response(response, status=200)
            if barcode := request.GET.get("query"):
                if stock := Stocks.objects.filter(barcode__barcode_no=barcode.upper()).first():
                    if stock.quantity > 0:
                        response = {
                            "success": True,
                            "message": "Stock Get Succesfully",
                            "data": {
                                "id": stock.id,
                                "quantity": stock.quantity,
                                "product": stock.product.name,
                            },
                        }
                        return Response(response, status=200)
                    resp = {
                        "success": False,
                        "message": f"{barcode} Barcode have zero quantity",
                    }
                    return Response(resp, status=400)
                else:
                    response = {
                        "success": False,
                        "message": "Invalid Barcode",
                    }
                    return Response(response, status=400)
            instance = Products.objects.select_related().order_by("-created_at")
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "Products List Get Succesfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    # stock in
    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                user = request.user
                if stock_list := data.get("stock_list", []):
                    for i in stock_list:
                        result = self.create_stock_in(i, user)
                        if isinstance(result, Response):
                            return result
                    response = {
                        "success": True,
                        "message": "Stock IN  Successfully",
                        "data": [],
                    }
                    return Response(response, status=200)
                else:
                    return self.create_stock_in(data, user, True)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    # STOCK OUT SINGLE RACK
    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                stock_list = data.get("stock_list", [])
                if not stock_list:
                    response = {
                        "success": False,
                        "message": "Required Stock OUT List",
                    }
                    return Response(response, status=400)

                stock_ids = [
                    s["stock_id"] for s in stock_list if s["select_quantity"] > 0
                ]
                stocks = (
                    Stocks.objects.select_related("product", "rack")
                    .filter(id__in=stock_ids)
                    .order_by("quantity")
                )
                for i in stocks:
                    quantity = self.get_value_from_stock_list(
                        stock_list, i.id, "select_quantity"
                    )
                    employee_id = self.get_value_from_stock_list(
                        stock_list, i.id, "employee_id"
                    )
                    purpose = self.get_value_from_stock_list(
                        stock_list, i.id, "purpose"
                    )
                    employee = Employees.objects.filter(id=employee_id).first()
                    if employee is None:
                        raise ValueError("Invalid Employee ID")
                    if 0 < quantity <= i.quantity:
                        i.quantity -= quantity
                        i.save()
                        product = Products.objects.get(id=i.product.id)
                        product.net_quantity -= quantity
                        product.save()
                        StocksHistory.objects.create(
                            stock=i,
                            quantity=quantity,
                            product_quantity=product.net_quantity,
                            user=request.user,
                            is_stock_out=True,
                            employee=employee,
                            purpose=purpose,
                        )
                response = {
                    "success": True,
                    "message": "Stock OUT successful",
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def get_value_from_stock_list(
        self, stock_list: list, stock_id: str, required_value
    ):
        default_output = None
        if required_value == "select_quantity":
            default_output = 0
        return next(
            (s.get(required_value) for s in stock_list if s["stock_id"] == stock_id),
            default_output,
        )

    def create_stock_in(self, data, user, is_single_stock=False):
        try:
            product_id = data.get("product_id", None)
            rack_id = data.get("rack_id", None)
            barcode_no = data.get("barcode_no", None)
            source = data.get("source", None)
            quantity = data.get("quantity", 1)
            if not all([product_id, rack_id, barcode_no, source]):
                raise ValueError("Required All fields")

            quantity = int(quantity) if isinstance(quantity, str) else quantity
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero")
            rack = Racks.objects.get(id=rack_id)
            product = Products.objects.get(id=product_id)
            barcode = Barcodes.objects.filter(barcode_no=barcode_no.upper()).first()
            if not barcode:
                raise ValueError("Invalid barcode")

            if not barcode.is_product_type:
                raise ValueError("Not a Material barcode")

            if Stocks.objects.filter(barcode=barcode).exists():
                raise ValueError("Barcode already used")

            with transaction.atomic():
                instance = Stocks.objects.create(
                    source=source,
                    quantity=quantity,
                    barcode=barcode,
                    rack=rack,
                    product=product,
                )
                net_quantity = product.net_quantity + quantity
                product.net_quantity = net_quantity
                product.save()
                barcode.status = "Used"
                barcode.save()
                stock_history = StocksHistory.objects.create(
                    stock=instance,
                    quantity=quantity,
                    product_quantity=net_quantity,
                    user=user,
                    is_stock_out=False,
                )
                if is_single_stock:
                    history_serializer = StocksHistorySerializer(stock_history)
                    resp_data = {
                        "product_net_quantity": product.net_quantity,
                        "rack": {
                            "id": rack.id,
                            "quantity": quantity,
                            "rack_no": rack.rack_no,
                        },
                        "history": history_serializer.data,
                    }
                    response = {
                        "success": True,
                        "message": "Stock IN  Successfully",
                        "data": resp_data,
                    }
                    return Response(response, status=200)
                return True
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class StockHistoryView(APIView, CustomPagination):
    serializer_class = StocksHistorySerializer

    def get(self, request, id=None):
        try:
            if id:
                if product := Products.objects.filter(id=id).first():
                    f = Q(stock__product__id=id)
                    if query := request.GET.get("query"):
                        f &= Q(
                            Q(stock__rack__rack_no__icontains=query)
                            | Q(stock__barcode__barcode_no__icontains=query)
                            | Q(quantity__icontains=query)
                            | Q(stock__source__icontains=query)
                            | Q(user__name__icontains=query)
                        )
                    instance = (
                        StocksHistory.objects.select_related()
                        .filter(f)
                        .order_by("-created_at")
                    )
                    if page := self.paginate_queryset(instance, request, view=self):
                        serializer = self.serializer_class(page, many=True)
                        result = self.get_paginated_response(serializer.data)
                        data = result.data["results"]  # pagination data
                        total = result.data["count"]
                        response = {
                            "success": True,
                            "message": "Stock History List Get Succesfully",
                            "data": data,
                            "product": {"name": product.name, "id": id},
                            "total": total,
                        }
                        return Response(response, status=200)
                else:
                    response = {
                        "success": False,
                        "message": "Product Not Found",
                    }
                    return Response(response, status=400)
            filter = Q()
            if query := request.GET.get("query"):
                filter &= Q(
                    Q(stock__rack__rack_no__icontains=query)
                    | Q(stock__product__name__icontains=query)
                    | Q(stock__product__ucs_code__icontains=query)
                    | Q(stock__barcode__barcode_no__icontains=query)
                    | Q(stock__source__icontains=query)
                    | Q(user__name__icontains=query)
                    | Q(user__email__icontains=query)
                    | Q(employee__email__icontains=query)
                    | Q(employee__name__icontains=query)
                    | Q(purpose__icontains=query)
                    )
            if  history_status:= request.GET.get("status"):
                if history_status == "In":
                    filter &= Q(is_stock_out = False)
                elif history_status == "Out":
                    filter &= Q(is_stock_out = True)
            instance = StocksHistory.objects.select_related().filter(filter).order_by("-created_at")
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()

            response = {
                "success": True,
                "message": "Stock History List Get Succesfully",
                "data": data,
                "total": total,
            }
            self.materialReport()
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def materialReport(self):
        from_date = datetime(2023, 1, 1, 2, 12)
        to_date = datetime(2023, 10, 1, 2, 12)
        f = Q(created_at__gte=from_date, created_at__lte=to_date)
        stock_history = (
            StocksHistory.objects.select_related("stock")
            .filter(f)
            .values("stock__product__name", "stock__product__ucs_code")
            .annotate(
                total_stock_in=Coalesce(
                    Sum("quantity", filter=Q(is_stock_out=False)), 0
                ),
                total_stock_out=Coalesce(
                    Sum("quantity", filter=Q(is_stock_out=True)), 0
                ),
                total_stock_in_price=ExpressionWrapper(
                    F("stock__product__price")
                    * Coalesce(Sum("quantity", filter=Q(is_stock_out=False)), 0),
                    output_field=FloatField(),
                ),
                total_stock_out_price=ExpressionWrapper(
                    F("stock__product__price")
                    * Coalesce(Sum("quantity", filter=Q(is_stock_out=True)), 0),
                    output_field=FloatField(),
                ),
            )
            .order_by("created_at__year")
        )


class BarcodeView(APIView, CustomPagination):
    serializer_class = BarcodeSerializer

    def get(self, request):
        try:
            if product_barcode_no := request.GET.get("product_barcode_no", None):
                barcode = Barcodes.objects.filter(barcode_no=product_barcode_no.upper()).first()
                if not barcode:
                    response = {
                        "success": False,
                        "message": "Invalid barcode",
                    }
                    return Response(response, status=400)
                if not barcode.is_product_type:
                    response = {
                        "success": False,
                        "message": "Not a Material barcode",
                    }
                    return Response(response, status=400)
                response = {
                    "success": True,
                    "message": "Valid Material Barcode",
                    "data": True,
                }
                return Response(response, status=200)
            filter = Q()
            if query := request.GET.get("query"):
                filter &=Q(
                    Q(barcode_no=query.upper())
                    | Q(racks__rack_no=query)
                    | Q(stocks__product__name=query)
                    )
            if barcode_status := request.GET.get("status"):
                filter &= Q(status__exact=barcode_status.capitalize()) if barcode_status in ["Used", "Unused"] else Q()

            instance = Barcodes.objects.select_related("stocks", "racks").filter(filter).order_by("-created_at")
            
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "Barcode List Get Succesfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                barcode_type = data.get("barcode_type", "rack")
                if no_of_barcode := data.get("no_of_barcode", 1):
                    no_of_barcode = (
                        int(no_of_barcode)
                        if isinstance(no_of_barcode, str)
                        else no_of_barcode
                    )

                if not all([barcode_type, no_of_barcode]):
                    response = {
                        "success": False,
                        "message": "Required All Field",
                    }
                    return Response(response, status=400)

                if no_of_barcode > 21:
                    response = {
                        "success": False,
                        "message": "Maximum No of barcode generation upto 20 20",
                    }
                    return Response(response, status=400)

                is_product_type = barcode_type == "product"
                barcode_ids = []
                for _ in range(1, no_of_barcode + 1):
                    barcode = Barcodes.objects.create(
                        is_product_type=is_product_type, status="Unused"
                    )
                    barcode_ids.append(barcode.id)

                instance = Barcodes.objects.filter(id__in=barcode_ids)
                response = {
                    "success": True,
                    "message": "Barcode created  successfully",
                    "data": self.serializer_class(instance, many=True).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


# front end search part


class SearchRacksView(APIView, CustomPagination):
    serializer_class = SearchRacksSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Racks.objects.select_related()
                    .filter(rack_no__icontains=query)
                    .distinct()
                    .order_by("rack_no")
                )
            else:
                instance = Racks.objects.select_related().order_by("-created_at")
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "Rack List Get Succesfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchSourceView(APIView):
    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Stocks.objects.select_related("product", "rack")
                    .filter(source__icontains=query)
                    .values("source")
                    .distinct()
                    .order_by("source")
                )
            else:
                instance = (
                    Stocks.objects.select_related("product", "rack")
                    .all()
                    .values("source")
                    .distinct()
                    .order_by("source")
                )
            response = {
                "success": True,
                "message": "Source List  Succesfully",
                "data": [
                    {"value": d["source"], "label": d["source"]} for d in instance
                ],
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchPurposeView(APIView):
    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    StocksHistory.objects.select_related("stock", "employee")
                    .filter(purpose__icontains=query)
                    .values("purpose")
                    .distinct()
                    .order_by("purpose")
                )
            else:
                instance = (
                    StocksHistory.objects.select_related("stock", "employee")
                    .all()
                    .values("purpose")
                    .distinct()
                    .order_by("purpose")
                )
            response = {
                "success": True,
                "message": "Purpose List  Succesfully",
                "data": [
                    {"value": d["purpose"], "label": d["purpose"]} for d in instance
                ],
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchMaterialView(APIView):
    serializer_class = SearchMaterialSerializer

    def get(self, request):
        try:
            instance = (
                Products.objects.select_related()
                .all()
                .only("name", "id")
                .order_by("name")
            )
            response = {
                "success": True,
                "message": "Material List  Succesfully",
                "data": SearchMaterialSerializer(instance, many=True).data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchProductView(APIView):
    def get(self, request):
        try:
            if query := request.GET.get("query"):
                results = (
                    Products.objects.select_related()
                    .filter(
                        Q(name__icontains=query)
                        | Q(stocks__barcode__barcode_no__icontains=query)
                    )
                    .values("name", "id")
                    .distinct()
                    .order_by("name")
                )
            else:
                results = []
            response = {
                "success": True,
                "message": "Search Result",
                "data": results,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SearchEmployeeView(APIView, CustomPagination):
    serializer_class = SearchEmployeeSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Employees.objects.select_related()
                    .filter(Q(name__icontains=query) | Q(personnel_number__icontains=query))
                    .distinct()
                    .order_by("name")
                )
            else:
                instance = Employees.objects.select_related().order_by("name")
            if request.GET.get("page"):
                page = self.paginate_queryset(instance, request, view=self)
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "Employee List Get Succesfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class DesignationView(APIView):
    serializer_class = DesignationSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Designation.objects.select_related()
                    .filter(name__icontains=query)
                    .order_by("name")
                )
            else:
                instance = Designation.objects.all().order_by("name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Designation List Get Succesfully",
                "data": serializer.data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                if not name:
                    response = {
                        "success": False,
                        "message": "Required designation Name",
                    }
                    return Response(response, status=400)

                if Designation.objects.filter(name=name).exists():
                    response = {
                        "success": False,
                        "message": "Designation already exists",
                    }
                    return Response(response, status=400)

                instance = Designation.objects.create(name=name)
                response = {
                    "success": True,
                    "message": "Designation Created  Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                designation_id = data.get("designation_id", None)
                name = data.get("name", None)
                if not all([name, designation_id]):
                    response = {
                        "success": False,
                        "message": "Required All Field",
                    }
                    return Response(response, status=400)
                instance = Designation.objects.get(id=designation_id)

                if (
                    Designation.objects.filter(name=name)
                    .exclude(name=instance.name)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Designation already exists",
                    }
                    return Response(response, status=400)
                instance.name = name
                instance.save()
                response = {
                    "success": True,
                    "message": "Designation Updated Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)



class UnitView(APIView):
    serializer_class = UnitSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Unit.objects.select_related()
                    .filter(name__icontains=query)
                    .order_by("name")
                )
            else:
                instance = Unit.objects.all().order_by("name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Unit List Get Succesfully",
                "data": serializer.data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                if not name:
                    response = {
                        "success": False,
                        "message": "Required unit Name",
                    }
                    return Response(response, status=400)

                if Unit.objects.filter(name=name).exists():
                    response = {
                        "success": False,
                        "message": "Unit already exists",
                    }
                    return Response(response, status=400)

                instance = Unit.objects.create(name=name)
                response = {
                    "success": True,
                    "message": "Unit Created  Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                unit_id = data.get("unit_id", None)
                name = data.get("name", None)
                if not all([name, unit_id]):
                    response = {
                        "success": False,
                        "message": "Required All Field",
                    }
                    return Response(response, status=400)
                instance = Unit.objects.get(id=unit_id)

                if (
                    Unit.objects.filter(name=name)
                    .exclude(name=instance.name)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Unit already exists",
                    }
                    return Response(response, status=400)
                instance.name = name
                instance.save()
                response = {
                    "success": True,
                    "message": "Unit Updated Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class EmployeeView(APIView, CustomPagination):
    serializer_class = EmployeeSerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    Employees.objects.select_related()
                    .filter(
                        Q(name__icontains=query)
                        | Q(personnel_number__icontains=query)
                        | Q(phone__icontains=query)
                    )
                    .annotate(
                        product=Count("stockshistory__stock__product", distinct=True)
                    )
                    .order_by("name")
                )
            else:
                instance = (
                    Employees.objects.all()
                    .annotate(
                        product=Count("stockshistory__stock__product", distinct=True)
                    )
                    .order_by("name")
                )
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "Employee List Get Succesfully",
                "data": data,
                "total":total
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                personnel_number = data.get("personnel_number", None)
                name = data.get("name", None)
                if not all([personnel_number, name]):
                    response = {
                        "success": False,
                        "message": "Required All fields",
                    }
                    return Response(response, status=400)
                
                if Employees.objects.filter(personnel_number=personnel_number).exists():
                    response = {
                        "success": False,
                        "message": "Employee already exists",
                    }
                    return Response(response, status=400)

                instance = Employees.objects.create(
                    name=name, personnel_number=personnel_number, phone=data.get("phone", None)
                )
                response = {
                    "success": True,
                    "message": "Employee Created  Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                employee_id = data.get("employee_id", None)
                name = data.get("name", None)
                personnel_number = data.get("personnel_number", None)
                if not all([name, personnel_number]):
                    response = {
                        "success": False,
                        "message": "Required All Field",
                    }
                    return Response(response, status=400)
                instance = Employees.objects.get(id=employee_id)

                if (
                    Employees.objects.filter(personnel_number=personnel_number)
                    .exclude(personnel_number=instance.personnel_number)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Employee email already exists",
                    }
                    return Response(response, status=400)
                instance.name = name
                instance.personnel_number = personnel_number
                instance.phone = data.get("phone", None)
                instance.save()
                response = {
                    "success": True,
                    "message": "Employee Updated Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def delete(self, request, id):
        try:
            with transaction.atomic():
                instance = Employees.objects.get(id=id)
                response = {
                    "success": True,
                    "message": "Employee Deleted Successfully",
                }
                instance.delete()
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ProductCategoryView(APIView):
    serializer_class = ProductCategorySerializer

    def get(self, request):
        try:
            if query := request.GET.get("query"):
                instance = (
                    ProductCategory.objects.select_related()
                    .filter(name__icontains=query)
                    .order_by("name")
                )
            else:
                instance = ProductCategory.objects.all().order_by("name")
            serializer = self.serializer_class(instance, many=True)
            response = {
                "success": True,
                "message": "Product Category List Get Succesfully",
                "data": serializer.data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                if not name:
                    response = {
                        "success": False,
                        "message": "Required designation Name",
                    }
                    return Response(response, status=400)

                if ProductCategory.objects.filter(name=name).exists():
                    response = {
                        "success": False,
                        "message": "Product Category already exists",
                    }
                    return Response(response, status=400)

                instance = ProductCategory.objects.create(name=name)
                response = {
                    "success": True,
                    "message": "Product Category Created  Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        try:
            with transaction.atomic():
                data = request.data
                product_category_id = data.get("product_category_id", None)
                name = data.get("name", None)
                if not all([name, product_category_id]):
                    response = {
                        "success": False,
                        "message": "Required All Field",
                    }
                    return Response(response, status=400)
                instance = ProductCategory.objects.get(id=product_category_id)

                if (
                    ProductCategory.objects.filter(name=name)
                    .exclude(name=instance.name)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Designation already exists",
                    }
                    return Response(response, status=400)
                instance.name = name
                instance.save()
                response = {
                    "success": True,
                    "message": "Product Category Updated Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)


class UserView(APIView, CustomPagination):
    serializer_class = UserSerializer

    def get(self, request, id=None):
        if request.user.is_superuser is False:
            response = {"success": False, "message": "User not allowed"}
            return Response(response, status=400)
        try:
            if id:
                instance = Users.objects.filter(id=id, is_superuser=False)
                serializer = self.serializer_class(instance)
                response = {
                    "success": True,
                    "message": "Employee Get Succesfully",
                    "data": serializer.data,
                }
                return Response(response, status=200)
            if query := request.GET.get("query"):
                instance = (
                    Users.objects.select_related()
                    .filter(
                        Q(is_superuser=False),
                        Q(name__icontains=query)
                        | Q(email__icontains=query)
                        | Q(personnel_number__icontains=query)
                        | Q(designation__name__icontains=query)
                        | Q(mobile_number=query),
                    )
                    .order_by("-created_at")
                )
            else:
                instance = (
                    Users.objects.select_related()
                    .filter(is_superuser=False)
                    .order_by("-created_at")
                )
            if page := self.paginate_queryset(instance, request, view=self):
                serializer = self.serializer_class(page, many=True)
                result = self.get_paginated_response(serializer.data)
                data = result.data["results"]  # pagination data
                total = result.data["count"]  # pagination data
            else:
                serializer = self.serializer_class(instance, many=True)
                data = serializer.data
                total = instance.count()
            response = {
                "success": True,
                "message": "User List Get Succesfully",
                "data": data,
                "total": total,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

    def post(self, request):
        try:
            if request.user.is_superuser is False:
                response = {"success": False, "message": "User not allowed"}
                return Response(response, status=400)
            with transaction.atomic():
                data = request.data
                name = data.get("name", None)
                password = data.get("password", None)
                email = data.get("email", None)
                mobile_number = data.get("mobile_number", None)
                designation_id = data.get("designation", None)
                personnel_number = data.get("personnel_number", None)
                if not all(
                    [name, password, email, mobile_number, designation_id, personnel_number]
                ):
                    response = {
                        "success": False,
                        "message": "Required All fields",
                    }
                    return Response(response, status=400)
                phone_pattern = re.compile(r"\b\d{10}\b")
                email_pattern = re.compile(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
                )
                if not email_pattern.match(email):
                    response = {
                        "success": False,
                        "message": "Invalid Email Format",
                    }
                    return Response(response, status=400)
                if not phone_pattern.match(mobile_number):
                    response = {
                        "success": False,
                        "message": "Invalid Mobile Number Format",
                    }
                    return Response(response, status=400)
                designation = Designation.objects.filter(id=designation_id).first()
                if not designation:
                    response = {
                        "success": False,
                        "message": "Invalid designation",
                    }
                    return Response(response, status=400)
                if Users.objects.filter(email=email).exists():
                    response = {
                        "success": False,
                        "message": "Email Already Exists",
                    }
                    return Response(response, status=400)

                instance = Users.objects.create_user(
                    name=name,
                    email=email,
                    password=password,
                    mobile_number=mobile_number,
                    designation=designation,
                    personnel_number=personnel_number,
                    is_superuser=False,
                    is_staff=True,
                    is_active=True,
                    role="User",
                )
                response = {
                    "success": True,
                    "message": "User Created  Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def put(self, request):
        if request.user.is_superuser is False:
            response = {"success": False, "message": "User not allowed"}
            return Response(response, status=400)
        try:
            with transaction.atomic():
                data = request.data
                emp_id = data.get("emp_id", None)
                name = data.get("name", None)
                password = data.get("password", None)
                email = data.get("email", None)
                status = data.get("status", "Active")
                mobile_number = data.get("mobile_number", None)
                designation_id = data.get("designation", None)
                employee_id = data.get("employee_id", None)
                if not all(
                    [emp_id, name, email, mobile_number, designation_id, employee_id]
                ):
                    response = {
                        "success": False,
                        "message": "Required All fields",
                    }
                    return Response(response, status=400)
                phone_pattern = re.compile(r"\b\d{10}\b")
                email_pattern = re.compile(
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
                )
                if not email_pattern.match(email):
                    response = {
                        "success": False,
                        "message": "Invalid Email Format",
                    }
                    return Response(response, status=400)
                if not phone_pattern.match(mobile_number):
                    response = {
                        "success": False,
                        "message": "Invalid Mobile Number Format",
                    }
                    return Response(response, status=400)

                designation = Designation.objects.filter(id=designation_id).first()
                if not designation:
                    response = {
                        "success": False,
                        "message": "Invalid designation",
                    }
                    return Response(response, status=400)
                instance = Users.objects.get(id=emp_id)
                if (
                    Users.objects.filter(email=email)
                    .exclude(email=instance.email)
                    .exists()
                ):
                    response = {
                        "success": False,
                        "message": "Email Already Exists",
                    }
                    return Response(response, status=400)
                instance.name = name
                instance.designation = designation
                instance.email = email
                instance.mobile_number = mobile_number
                instance.employee_id = employee_id
                instance.is_active = status == "Active"
                if password:
                    instance.set_password(password)
                instance.save()
                response = {
                    "success": True,
                    "message": "User Updated Successfully",
                    "data": self.serializer_class(instance).data,
                }
                return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {
                "success": False,
                "message": str(e),
            }
            return Response(response, status=400)

    def delete(self, request, id):
        if request.user.is_superuser is False:
            response = {"success": False, "message": "User not allowed"}
            return Response(response, status=400)
        try:
            with transaction.atomic():
                instance = Users.objects.filter(id=id, is_superuser=False)
                if instance.exists():
                    response = {
                        "success": True,
                        "message": "User Deleted Successfully",
                    }
                    instance.delete()
                    return Response(response, status=200)
                response = {
                    "success": False,
                    "message": f"User Not Found with This ID {id}",
                }
                return Response(response, status=400)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ABCAnalysisView(APIView):
    def get(self, request):
        try:
            f = Q(is_stock_out=True)
            view_type = request.GET.get("view_type")
            if view_type == "30days":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=31)
                f &= Q(created_at__gte=to_date, created_at__lte=from_date)
            elif view_type == "1year":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=366)
                f &= Q(created_at__gte=to_date, created_at__lte=from_date)
            stock_history = StocksHistory.objects.select_related(
                "rack", "stock"
            ).filter(f)
            total_quantity = stock_history.aggregate(total=Sum("quantity"))["total"]
            all_products = (
                stock_history.values("stock__product__name")
                .annotate(sum_quantity=Sum("quantity"))
                .order_by("-sum_quantity")
            )

            a_limit = 0.4 * total_quantity
            b_limit = 0.8 * total_quantity
            cumulative_quantity = 0
            A = 0
            B = 0
            C = 0
            product_data = {"A": [], "B": [], "C": []}
            for product in all_products:
                percent = round((product["sum_quantity"] / total_quantity) * 100, 2)
                if cumulative_quantity <= a_limit:
                    A += 1
                    product_data["A"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "quantity": product["sum_quantity"],
                        }
                    )
                elif cumulative_quantity <= b_limit:
                    B += 1
                    product_data["B"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "quantity": product["sum_quantity"],
                        }
                    )
                else:
                    product_data["C"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "quantity": product["sum_quantity"],
                        }
                    )
                    C += 1
                cumulative_quantity += product["sum_quantity"]

            labels = ["A", "B", "C"]
            output_data = [A, B, C]
            data = {"labels": labels, "data": output_data, "product_data": product_data}

            response = {
                "success": True,
                "message": "Product Forecast",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class VEDAnalysisView(APIView):
    def get(self, request):
        try:
            all_products = Products.objects.all().order_by("-net_quantity")
            prducts = all_products.aggregate(
                vital=Count("id", filter=Q(ved_category="Vital")),
                essential=Count("id", filter=Q(ved_category="Essential")),
                desirable=Count("id", filter=Q(ved_category="Desirable")),
            )
            labels = ["Vital", "Essential", "Desirable"]
            output_data = [prducts["vital"], prducts["essential"], prducts["desirable"]]
            data = {
                "labels": labels,
                "data": output_data,
                "product_data": all_products.values(
                    "name", "ved_category", "net_quantity"
                ),
            }
            response = {
                "success": True,
                "message": "Product Forecast",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class HMLAnalysisView(APIView):
    def get(self, request):
        try:
            f = Q(is_stock_out=True)
            view_type = request.GET.get("view_type")
            if view_type == "30days":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=31)
                f &= Q(created_at__gte=to_date, created_at__lte=from_date)
            elif view_type == "1year":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=366)
                f &= Q(created_at__gte=to_date, created_at__lte=from_date)

            stock_history = StocksHistory.objects.select_related(
                "rack", "stock"
            ).filter(f)
            total_quantity = stock_history.aggregate(
                total=Sum(F("quantity") * F("stock__product__price"))
            )["total"]
            all_products = (
                stock_history.values("stock__product__name")
                .annotate(sum_price=Sum(F("quantity") * F("stock__product__price")))
                .order_by("-sum_price")
            )
            h_limit = 0.2 * total_quantity
            m_limit = 0.3 * total_quantity
            cumulative_quantity = 0
            H = 0
            M = 0
            L = 0
            product_data = {"H": [], "M": [], "L": []}
            for product in all_products:
                percent = round((product["sum_price"] / total_quantity) * 100, 2)
                if cumulative_quantity <= h_limit:
                    H += 1
                    product_data["H"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "price": product["sum_price"],
                        }
                    )
                elif cumulative_quantity <= m_limit:
                    M += 1
                    product_data["M"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "price": product["sum_price"],
                        }
                    )
                else:
                    L += 1
                    product_data["L"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "price": product["sum_price"],
                        }
                    )
                cumulative_quantity += product["sum_price"]

            labels = ["H", "M", "L"]
            output_data = [H, M, L]
            data = {"labels": labels, "data": output_data, "product_data": product_data}
            response = {
                "success": True,
                "message": "Product Forecast",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class FSNAnalysisView(APIView):
    def get(self, request):
        try:
            f = Q(is_stock_out=True)
            view_type = request.GET.get("view_type")
            if view_type == "30days":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=31)
                f &= Q(created_at__gte=to_date, created_at__lte=from_date)
            elif view_type == "1year":
                from_date = datetime.now().date()
                to_date = from_date - timedelta(days=366)
                f &= Q(created_at__gte=to_date, created_at__lte=from_date)
            stock_history = StocksHistory.objects.select_related(
                "rack", "stock"
            ).filter(f)
            total_quantity = stock_history.aggregate(total=Sum("quantity"))["total"]
            all_products = (
                stock_history.values("stock__product__name")
                .annotate(sum_quantity=Sum("quantity"))
                .order_by("-sum_quantity")
            )

            f_limit = 0.15 * total_quantity
            s_limit = 0.35 * total_quantity
            cumulative_quantity = 0
            F = 0
            S = 0
            N = 0
            product_data = {"F": [], "S": [], "N": []}
            for product in all_products:
                percent = round((product["sum_quantity"] / total_quantity) * 100, 2)
                if cumulative_quantity <= f_limit:
                    F += 1
                    product_data["F"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "quantity": product["sum_quantity"],
                        }
                    )
                elif cumulative_quantity <= s_limit:
                    S += 1
                    product_data["S"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "quantity": product["sum_quantity"],
                        }
                    )
                else:
                    N += 1
                    product_data["N"].append(
                        {
                            "name": product["stock__product__name"],
                            "percentage": percent,
                            "quantity": product["sum_quantity"],
                        }
                    )
                cumulative_quantity += product["sum_quantity"]

            labels = ["F", "S", "N"]
            output_data = [F, S, N]
            data = {"labels": labels, "data": output_data, "product_data": product_data}

            response = {
                "success": True,
                "message": "Product Forecast",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class SDEAnalysisView(APIView):
    def get(self, request):
        try:
            products = Products.objects.all()
            total_lead_time = products.aggregate(total=Sum("lead_time"))["total"]
            all_products = products.values("name", "lead_time").order_by("-lead_time")

            s_limit = 0.2 * total_lead_time
            d_limit = 0.3 * total_lead_time
            cumulative_quantity = 0
            S = 0
            D = 0
            E = 0
            product_data = {"S": [], "D": [], "E": []}
            for product in all_products:
                percent = round((product["lead_time"] / total_lead_time) * 100, 2)
                if cumulative_quantity <= s_limit:
                    S += 1
                    product_data["S"].append(
                        {
                            "name": product["name"],
                            "percentage": percent,
                            "lead_time": product["lead_time"],
                        }
                    )
                elif cumulative_quantity <= d_limit:
                    D += 1
                    product_data["D"].append(
                        {
                            "name": product["name"],
                            "percentage": percent,
                            "lead_time": product["lead_time"],
                        }
                    )
                else:
                    E += 1
                    product_data["E"].append(
                        {
                            "name": product["name"],
                            "percentage": percent,
                            "lead_time": product["lead_time"],
                        }
                    )

                cumulative_quantity += product["lead_time"]

            labels = ["S", "D", "E"]
            output_data = [S, D, E]
            data = {"labels": labels, "data": output_data, "product_data": product_data}

            response = {
                "success": True,
                "message": "Product SDE analysis",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class StockAgingAnalysisView(APIView):
    def get(self, request):
        try:
            view_type = request.GET.get("view_type", "1M")
            if view_type == "1M":
                from_date = datetime.now().date() - timedelta(days=31)
            elif view_type == "3M":
                from_date = datetime.now().date() - timedelta(days=91)
            elif view_type == "6M":
                from_date = datetime.now().date() - timedelta(days=181)
            else:
                from_date = datetime.now().date() - timedelta(days=366)
            total_stock = Stocks.objects.aggregate(total=Sum("quantity"))["total"]
            stocks = Stocks.objects.filter(quantity__gt=0, created_at__lte=from_date)
            old_stock = stocks.aggregate(total=Sum("quantity"))["total"]
            product_data = (
                stocks.values("product__name")
                .annotate(quantity=(Sum("quantity")))
                .order_by("-quantity")
            )
            ratio_percen = round((old_stock / total_stock) * 100, 2)
            data = {
                "labels": ["Stock Ratio"],
                "data": [ratio_percen],
                "product_data": product_data,
            }
            response = {
                "success": True,
                "message": "Product SDE analysis",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


##report


class ReportMeterial(APIView, CustomPagination):
    serializer_class = ReportMaterialSerializer

    def get(self, request):
        try:
            from_date = request.GET.get("from_date", "")
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            else:
                from_date = datetime.now().date()

            to_date = request.GET.get("to_date", "")
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            else:
                to_date = from_date - timedelta(days=300)

            f = Q(created_at__gte=from_date, created_at__lte=to_date)
            instance = (
                StocksHistory.objects.select_related("stock")
                .filter(f)
                .values("stock__product__name", "stock__product__ucs_code")
                .annotate(
                    total_stock_in=Coalesce(
                        Sum("quantity", filter=Q(is_stock_out=False)), 0
                    ),
                    total_stock_out=Coalesce(
                        Sum("quantity", filter=Q(is_stock_out=True)), 0
                    ),
                    total_stock_in_price=ExpressionWrapper(
                        F("stock__product__price")
                        * Coalesce(Sum("quantity", filter=Q(is_stock_out=False)), 0),
                        output_field=FloatField(),
                    ),
                    total_stock_out_price=ExpressionWrapper(
                        F("stock__product__price")
                        * Coalesce(Sum("quantity", filter=Q(is_stock_out=True)), 0),
                        output_field=FloatField(),
                    ),
                )
                .order_by("stock__product__name")
            )

            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Material Report List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ReportMeterialTransaction(APIView):
    serializer_class = ReportMaterialTransacrionSerializer

    def get(self, request):
        try:
            from_date = request.GET.get("from_date", "")
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            else:
                from_date = datetime.now().date()

            to_date = request.GET.get("to_date", "")
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            else:
                to_date = from_date - timedelta(days=300)

            f = Q(created_at__gte=from_date, created_at__lte=to_date)
            if product_id := request.GET.get("material_id"):
                product_id_list = product_id.split(",")
                f &= Q(stock__product__id__in=product_id_list)

            instance = (
                StocksHistory.objects.select_related("stock")
                .filter(f)
                .values(
                    "stock__product__name",
                    "created_at__date",
                    "stock__product__ucs_code",
                )
                .annotate(
                    total_stock_in=Coalesce(
                        Sum("quantity", filter=Q(is_stock_out=False)), 0
                    ),
                    total_stock_out=Coalesce(
                        Sum("quantity", filter=Q(is_stock_out=True)), 0
                    ),
                )
                .order_by("created_at__date")
            )

            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Material Transaction Report List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ReportFastReceiveMovingItem(APIView):
    serializer_class = ReportFastReceiveMovingItemSerializer

    def get(self, request):
        try:
            from_date = request.GET.get("from_date", "")
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            else:
                from_date = datetime.now().date()

            to_date = request.GET.get("to_date", "")
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            else:
                to_date = from_date - timedelta(days=300)

            stock_type = request.GET.get("stock_type", "stockout")

            instance = (
                Products.objects.annotate(
                    quantity=Coalesce(
                        Sum(
                            "stocks__stockshistory__quantity",
                            filter=Q(
                                stocks__stockshistory__is_stock_out=stock_type
                                == "stockout",
                                stocks__stockshistory__created_at__gte=from_date,
                                stocks__stockshistory__created_at__lte=to_date,
                            ),
                        ),
                        0,
                    )
                )
                .filter(quantity__gt=0)
                .order_by("-quantity")
                .values("name", "ucs_code", "quantity")
            )

            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Fast Moving Receive Material Report List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ReportCrirticalReorderItem(APIView):
    serializer_class = CrirticalReorderItemSerializer

    def get(self, request):
        try:
            instance = Products.objects.filter(
                net_quantity__lt=F("min_threshold")
            ).order_by("-net_quantity")
            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Critical Reorder Item Report List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ReportEmployee(APIView):
    serializer_class = ReportEmployeeSerializer

    def get(self, request):
        try:
            from_date = request.GET.get("from_date", "")
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            else:
                from_date = datetime.now().date()

            to_date = request.GET.get("to_date", "")
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            else:
                to_date = from_date - timedelta(days=300)

            f = Q(
                created_at__gte=from_date,
                created_at__lte=to_date,
                is_stock_out=True,
                employee__isnull=False,
            )
            if employee_id := request.GET.get("employee_id"):
                employee_id_list = employee_id.split(",")
                f &= Q(employee__id__in=employee_id_list)

            instance = (
                StocksHistory.objects.select_related("stock")
                .filter(f)
                .values(
                    "stock__product__name",
                    "stock__product__ucs_code",
                    "employee__name",
                    "employee__personnel_number",
                )
                .annotate(
                    total_stock_out=Coalesce(Sum("quantity"), 0),
                    total_stock_out_price=ExpressionWrapper(
                        F("stock__product__price") * Coalesce(Sum("quantity"), 0),
                        output_field=FloatField(),
                    ),
                )
                .order_by("employee__name")
            )

            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Employee Report List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ReportMaterialUsage(APIView):
    serializer_class = ReportMaterialUsageSerializer

    def get(self, request):
        try:
            from_date = request.GET.get("from_date", "")
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            else:
                from_date = datetime.now().date()

            to_date = request.GET.get("to_date", "")
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            else:
                to_date = from_date - timedelta(days=300)

            f = Q(
                created_at__gte=from_date,
                created_at__lte=to_date,
                is_stock_out=True,
                purpose__isnull=False,
            )
            if purpose := request.GET.get("purpose"):
                purpose_list = purpose.split(",")
                f &= Q(purpose__in=purpose_list)

            instance = (
                StocksHistory.objects.select_related("stock")
                .filter(f)
                .values(
                    "purpose",
                    "stock__product__name",
                    "created_at__date",
                    "stock__product__ucs_code",
                )
                .annotate(
                    total_stock_out=Coalesce(Sum("quantity"), 0),
                )
                .order_by("purpose")
            )

            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Material Usage Report List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class ReportDeadStockItem(APIView):
    serializer_class = ReportDeadStockItemSerializer

    def get(self, request):
        try:
            from_date = request.GET.get("from_date", "")
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d")
            else:
                from_date = datetime.now().date()

            to_date = request.GET.get("to_date", "")
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d")
            else:
                to_date = from_date - timedelta(days=300)

            f = Q(created_at__gte=from_date, created_at__lte=to_date, is_stock_out=True)
            product_ids = (
                StocksHistory.objects.select_related("stock")
                .filter(f)
                .values_list("stock__product__id")
            )
            instance = (
                Products.objects.exclude(id__in=product_ids)
                .order_by("-net_quantity")
                .values("name", "ucs_code", "net_quantity")
            )
            serializer = self.serializer_class(instance, many=True)
            data = serializer.data

            response = {
                "success": True,
                "message": "Critical Reorder Item Report List Get Succesfully",
                "data": data,
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)


class GenerateStockData(APIView):
    serializer_class = ReportDeadStockItemSerializer

    def post(self, request):
        try:
            end_date = request.GET.get("end_date", "")
            if end_date:
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end_date = datetime.now().date()

            start_date = request.GET.get("start_date", "")
            if start_date:
                start_date = datetime.strptime(start_date, "%Y-%m-%d")
            else:
                start_date =  end_date - timedelta(days=8)

            if start_date >= end_date:
                response = {"success": False, "message": "Start Date must be less than End Date"}
                return Response(response, status=400)

            from AuthApp.scripts import stock_in_out
            stock_in_out(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

            response = {
                "success": True,
                "message": "Stock Data Generated Succesfully",
            }
            return Response(response, status=200)
        except Exception as e:
            Syserror(e)
            response = {"success": False, "message": str(e)}
            return Response(response, status=400)

