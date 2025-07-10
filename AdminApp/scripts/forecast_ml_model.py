import pandas as pd
from prophet import Prophet
import joblib
from AdminApp.models import StocksHistory
from django.db.models import Sum, F
from django.db.models.functions import TruncMonth
from datetime import datetime
from pathlib import Path
from django.conf import settings


def train_model_on_weekly_basis():
    """Train the initial monthly demand forecast model using Prophet."""
    today_date = datetime.now().date()
    history_data = (
        StocksHistory.objects.select_related('stock', 'stock__product')
        .filter(
            is_stock_out=True,
            created_at__date__lt=today_date,  # Use date to filter past dates
        )
        .annotate(stock_out_month=TruncMonth('created_at'))
        .values('stock_out_month')
        .annotate(stock_out_quantity=Sum('quantity'), product_name=F('stock__product__name'))
        .order_by('stock_out_month')
    )

    if not history_data.exists():
        print("No data exists to train a monthly model.")
        return False

    # Convert history data to DataFrame
    df = pd.DataFrame.from_records(history_data)
    df['stock_out_month'] = pd.to_datetime(df['stock_out_month'])

    # Prepare data for Prophet
    df = df.rename(columns={'stock_out_month': 'ds', 'stock_out_quantity': 'y'})

    # Shift all dates to align with the current year
    current_year = datetime.now().year
    df['ds'] = df['ds'].apply(lambda x: x.replace(year=current_year))

    # Train separate models for each product
    product_models = {}

    for product_name, product_df in df.groupby('product_name'):
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
        )
        model.fit(product_df[['ds', 'y']])
        product_models[product_name] = model

    # Save all models
    model_path = Path(settings.BASE_DIR, 'MLModel', 'prophet_models.pkl')
    joblib.dump(product_models, model_path)
    print("Monthly demand forecast models trained successfully.")
    return True


def train_model_on_daily_basis():
    """Update the model with new data."""
    model_path = Path(settings.BASE_DIR, 'MLModel', 'prophet_models.pkl')

    # Load existing models
    if not model_path.exists():
        print("Model file does not exist. Run initial training first.")
        return False

    product_models = joblib.load(model_path)

    today_date = datetime.now().date()
    new_data = (
        StocksHistory.objects.select_related('stock', 'stock__product')
        .filter(is_stock_out=True, created_at__date=today_date)
        .annotate(stock_out_month=TruncMonth('created_at'))
        .values('stock_out_month')
        .annotate(stock_out_quantity=Sum('quantity'), product_name=F('stock__product__name'))
        .order_by('stock_out_month')
    )

    if not new_data.exists():
        print(f"No new data available for {today_date}")
        return False

    # Convert to DataFrame
    df = pd.DataFrame.from_records(new_data)
    df['stock_out_month'] = pd.to_datetime(df['stock_out_month'])
    df = df.rename(columns={'stock_out_month': 'ds', 'stock_out_quantity': 'y'})

    # Update models with new data
    for product_name, product_df in df.groupby('product_name'):
        if product_name in product_models:
            model = product_models[product_name]
        else:
            print(f"New product {product_name} detected. Creating new model.")
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=False,
                daily_seasonality=False,
            )

        model.fit(product_df[['ds', 'y']])
        product_models[product_name] = model

    # Save updated models
    joblib.dump(product_models, model_path)
    print(f"Model updated with new data for {today_date}")
    return True


def forecast_future_demand(product_name, periods=12):
    """Forecast future demand for a product."""
    model_path = Path(settings.BASE_DIR, 'MLModel', 'prophet_models.pkl')

    if not model_path.exists():
        print("Model file does not exist. Run initial training first.")
        return None

    product_models = joblib.load(model_path)

    if product_name not in product_models:
        print(f"No model found for product: {product_name}")
        return None

    model = product_models[product_name]

    # Create a future DataFrame starting from today to predict future dates
    future_df = pd.date_range(
        start=datetime.now().date(),
        periods=periods,
        freq='ME',  # Month end frequency
    ).to_frame(index=False, name='ds')

    # Make predictions
    forecast = model.predict(future_df)

    # Return only future predictions
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


def forecast_all_demand(product_name, periods=12):
    """Forecast future demand for a product."""
    model_path = Path(settings.BASE_DIR, 'MLModel', 'prophet_models.pkl')

    if not model_path.exists():
        print("Model file does not exist. Run initial training first.")
        return None

    product_models = joblib.load(model_path)

    if product_name not in product_models:
        print(f"No model found for product: {product_name}")
        return None

    model = product_models[product_name]

    # Get historical data for the product
    history_data = (
        StocksHistory.objects.select_related('stock', 'stock__product')
        .filter(
            is_stock_out=True,
            stock__product__name=product_name,
        )
        .annotate(stock_out_month=TruncMonth('created_at'))
        .values('stock_out_month')
        .annotate(stock_out_quantity=Sum('quantity'))
        .order_by('stock_out_month')
    )

    if not history_data.exists():
        print(f"No historical data available for product: {product_name}")
        return None

    # Convert history data to DataFrame
    history_df = pd.DataFrame.from_records(history_data)
    history_df['stock_out_month'] = pd.to_datetime(history_df['stock_out_month'])
    history_df = history_df.rename(columns={'stock_out_month': 'ds', 'stock_out_quantity': 'y'})

    # Get the maximum date from the historical data
    last_date = history_df['ds'].max()

    # Generate future dates for prediction
    future_df = pd.date_range(
        start=last_date + pd.DateOffset(months=1),
        periods=periods,
        freq='ME'  # Month end
    ).to_frame(index=False, name='ds')

    # Predict only future dates
    future_forecast = model.predict(future_df)

    # Add historical data to the forecast DataFrame
    history_df['yhat'] = history_df['y']  # Use actual historical values
    history_df['yhat_lower'] = history_df['y']
    history_df['yhat_upper'] = history_df['y']

    # Concatenate historical and future predictions
    forecast = pd.concat([history_df[['ds', 'yhat', 'yhat_lower', 'yhat_upper']], future_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]], ignore_index=True)

    # Return the DataFrame with predictions
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


def compare_actual_vs_forecast(product_name, periods=12):
    """Compare actual and forecasted demand for a product."""
    # Get actual stock-out data
    history_data = (
        StocksHistory.objects.select_related('stock', 'stock__product')
        .filter(
            is_stock_out=True,
            stock__product__name=product_name,
        )
        .annotate(stock_out_month=TruncMonth('created_at__date'))
        .values('stock_out_month')
        .annotate(stock_out_quantity=Sum('quantity'))
        .order_by('stock_out_month')
    )

    if not history_data.exists():
        print(f"No actual data available for product: {product_name}")
        return None

    # Convert actual data to DataFrame
    actual_df = pd.DataFrame.from_records(history_data)
    actual_df['stock_out_month'] = pd.to_datetime(actual_df['stock_out_month'])
    actual_df = actual_df.rename(columns={'stock_out_month': 'ds', 'stock_out_quantity': 'actual_demand'})

    # Get forecasted data
    forecast_df = forecast_all_demand(product_name, periods)

    if forecast_df is None:
        print(f"Unable to generate forecast for product: {product_name}")
        return None

    # Merge actual and forecasted data
    comparison_df = pd.merge(actual_df, forecast_df[['ds', 'yhat']], on='ds', how='outer')
    comparison_df = comparison_df.rename(columns={'yhat': 'forecast_demand'})
    comparison_df = comparison_df.fillna(0)  # Fill missing values with 0 for comparison

    # Return final DataFrame
    return comparison_df[['ds', 'actual_demand', 'forecast_demand']]