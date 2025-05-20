from datetime import datetime
from AdminApp.models import Products, StocksHistory
from AdminApp.utils import sendEmail_template
from AdminApp.models import Users
from django.db.models import Q, Sum, F
from django.db.models import Sum, Q, F


def daily_stock_report():
    try:
        today_date = datetime.now().date()

        stock_history = StocksHistory.objects.filter(
            created_at__date=today_date
        ).aggregate(
            stock_in=Sum("quantity", filter=Q(is_stock_out=False), default=0),
            stock_out=Sum("quantity", filter=Q(is_stock_out=True), default=0),
        )

        total_under_stock_product = Products.objects.filter(
            net_quantity__lt=F("min_threshold"), net_quantity__gt=0
        ).count()

        stock_data = (
            StocksHistory.objects.filter(created_at__date=today_date)
            .values("stock__product__id", "stock__product__name", "is_stock_out")
            .annotate(total_quantity=Sum("quantity"))
        )

        most_stocked_in_today = [
            entry for entry in stock_data if not entry["is_stock_out"]
        ][:5]

        most_stocked_out_today = [
            entry for entry in stock_data if entry["is_stock_out"]
        ][:5]

        return {
            "today_date": today_date.strftime("%d %b %Y"),
            "today_stock_in": stock_history["stock_in"],
            "today_stock_out": stock_history["stock_out"],
            "under_stock": total_under_stock_product,
            "most_stocked_in_today": most_stocked_in_today,
            "most_stocked_out_today": most_stocked_out_today,
        }
    except Exception as e:
        print("Error:", e)
        return None


def send_daily_stock_report_mail():
    email_to_list = Users.objects.filter(is_allow_email_daily_report=True).values_list(
        "email", flat=True
    )
    if not email_to_list:
        return False
    template_path = "daily_stock_report.html"
    subject = "InteliStock Daily Stock Report"
    email_context = daily_stock_report()
    sendEmail_template(
        email_to=email_to_list,
        subject=subject,
        email_template_path=template_path,
        email_context=email_context,
    )
