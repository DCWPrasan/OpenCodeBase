# import pandas as pd
# from sklearn.ensemble import RandomForestRegressor
# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import LabelEncoder
# from sklearn.metrics import mean_squared_error
# import joblib
# from django.conf import settings

# from AdminApp.models import StocksHistory
# from django.db.models import Sum, F
# from django.db.models.functions import TruncMonth
# from datetime import datetime
# from io import BytesIO

# from AdminApp.utils import putMlModel


# def train_initial_monthly_model():
#     today_date = datetime.now()
#     history_data =  (
#             StocksHistory.objects.select_related('stock', 'stock__product')
#             .filter(is_stock_out=True, created_at__month__lt=today_date.month, created_at__year__lt=today_date.year, )
#             .annotate(stock_out_month=TruncMonth('created_at__date')).values('stock_out_month')
#             .annotate(stock_out_quantity=Sum('quantity'), product_name=F('stock__product__name'))
#             .order_by('stock_out_month')
#         )
    
#     if not history_data:
#         print("No Data exist to train a monthly model")
#         return False
#     # convert history data to dataFrame
#     df  = pd.DataFrame(history_data)
#     # Convert date to datetime format
#     df['stock_out_month'] = pd.to_datetime(df['stock_out_month'])

#     # Create new columns for year, month, and day
#     df['Year'] = df['stock_out_month'].dt.year
#     df['Month'] = df['stock_out_month'].dt.month

#     # Drop the original date column
#     df.drop(columns=['stock_out_month'], inplace=True)

#     # Label encode product names
#     encoder = LabelEncoder()
#     df['product_name'] = encoder.fit_transform(df['product_name'])

#     # Create features (X) and target (y)
#     X = df.drop(columns=['stock_out_quantity'])
#     y = df['stock_out_quantity']

#     # Train-test split
#     X_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     # Random Forest Model
#     model = RandomForestRegressor(n_estimators=100, random_state=42)
#     model.fit(X_train, y_train)
#     # Predict stock-out quantities on the test set
#     y_pred = model.predict(x_test)

#     # Calculate mean squared error
#     mse = mean_squared_error(y_test, y_pred)
#     print(f"Mean Squared Error: {mse}")

#     # Print column names to make sure you know what they are when using the model for prediction
#     print("Column names in X_train:", X_train.columns)
#     if settings.DEBUG:
#         joblib.dump(model, 'MLModel/rf_model.pkl')
#         joblib.dump(encoder, 'MLModel/encoder.pkl')
#     else:
#         model_file_name = 'rf_model.pkl'
#         encoder_file_name = 'encoder.pkl'
#         # Serialize model and encoder to bytes
#         model_buffer = BytesIO()
#         encoder_buffer = BytesIO()
#         # Then save the model and encoder
#         joblib.dump(model, model_buffer)
#         joblib.dump(encoder, encoder_buffer)
#         putMlModel(model_file_name, model_buffer)
#         putMlModel(encoder_file_name, encoder_buffer)

#     print("Monthly Model trained succesfully ")
#     return True


