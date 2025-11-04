import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import GradientBoostingRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.cluster import KMeans
import time
from typing import Dict, List, Tuple, Optional
import threading
from collections import deque
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False

class ProductivityPredictor:
    """
    Advanced predictive analytics for productivity forecasting using multiple models.
    Combines Linear Regression, ARIMA, SARIMAX, Prophet, Gradient Boosting, and LSTM.
    Includes automatic model retraining on a schedule.
    """

    def __init__(self, max_history: int = 2000):
        """Initialize the productivity predictor."""
        self.max_history = max_history

        # Data storage - high resolution
        self.productivity_history = deque(maxlen=max_history)
        self.time_series_data = deque(maxlen=max_history)
        self.lock = threading.Lock()

        # Model storage
        self.models = {
            'linear': {'model': None, 'trained': False, 'scaler': StandardScaler()},
            'arima': {'model': None, 'trained': False},
            'sarimax': {'model': None, 'trained': False},
            'prophet': {'model': None, 'trained': False},
            'gradient_boost': {'model': None, 'trained': False, 'scaler': StandardScaler()},
            'lstm': {'model': None, 'trained': False, 'scaler': MinMaxScaler()},
        }

        # Performance metrics
        self.model_performance = {}
        self.last_training_time = 0
        self.training_interval = 3600  # 60 minutes in seconds
        self.min_samples_for_training = 48  # About 2 days of hourly data

        # Threading for background training
        self.training_thread = None
        self.auto_train_enabled = True

    def add_productivity_data(self, productivity_score: float, timestamp: Optional[float] = None,
                            context: Optional[Dict] = None):
        """Add a new productivity data point."""
        if timestamp is None:
            timestamp = time.time()

        if context is None:
            context = {}

        # Extract temporal features
        local_time = time.localtime(timestamp)
        day_of_week = local_time.tm_wday
        hour_of_day = local_time.tm_hour
        minute_of_hour = local_time.tm_min
        is_weekend = 1 if day_of_week >= 5 else 0
        is_work_hours = 1 if 9 <= hour_of_day <= 17 else 0

        data_point = {
            'timestamp': timestamp,
            'productivity_score': productivity_score,
            'day_of_week': day_of_week,
            'hour_of_day': hour_of_day,
            'minute_of_hour': minute_of_hour,
            'is_weekend': is_weekend,
            'is_work_hours': is_work_hours,
            'context': context
        }

        with self.lock:
            self.productivity_history.append(data_point)
            self.time_series_data.append(productivity_score)

        # Auto-trigger training if interval has elapsed
        if self._should_retrain():
            self.schedule_model_training()

    def _should_retrain(self) -> bool:
        """Check if models should be retrained based on time interval."""
        current_time = time.time()
        return (current_time - self.last_training_time) >= self.training_interval

    def schedule_model_training(self):
        """Schedule background model training in a separate thread."""
        if self.training_thread is not None and self.training_thread.is_alive():
            return  # Already training

        self.training_thread = threading.Thread(target=self._train_all_models, daemon=True)
        self.training_thread.start()

    def _train_all_models(self):
        """Train all available models (runs in background)."""
        try:
            with self.lock:
                if len(self.productivity_history) < self.min_samples_for_training:
                    return

                # Get data as DataFrame
                data = list(self.productivity_history)
                df = pd.DataFrame(data)
                self.last_training_time = time.time()

            # Train each model
            self.train_linear_model()
            self.train_gradient_boost_model()
            self.train_arima_model()
            self.train_sarimax_model()
            if HAS_PROPHET:
                self.train_prophet_model()
            if HAS_TENSORFLOW:
                self.train_lstm_model()

            print("[AUTO-TRAIN] All models trained successfully at", time.strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            print(f"[ERROR] Auto-training failed: {e}")

    def get_historical_data(self, days: int = 30) -> pd.DataFrame:
        """Get historical productivity data resampled to hourly averages."""
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        with self.lock:
            historical_data = [
                point for point in self.productivity_history
                if point['timestamp'] >= cutoff_time
            ]

        if not historical_data:
            return pd.DataFrame()

        df = pd.DataFrame(historical_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('datetime', inplace=True)

        # Resample to hourly averages
        if not df.empty:
            hourly_data = df['productivity_score'].resample('H').mean()
            # Forward fill missing hours
            hourly_data = hourly_data.fillna(method='ffill').fillna(method='bfill')
            df_hourly = hourly_data.reset_index()
            df_hourly.columns = ['datetime', 'productivity_score']
            df_hourly.set_index('datetime', inplace=True)
            return df_hourly

        return df

    def get_daily_data(self, days: int = 30) -> pd.DataFrame:
        """Get daily average productivity data."""
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        with self.lock:
            historical_data = [
                point for point in self.productivity_history
                if point['timestamp'] >= cutoff_time
            ]

        if not historical_data:
            return pd.DataFrame()

        df = pd.DataFrame(historical_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('datetime', inplace=True)

        # Resample to daily averages
        if not df.empty:
            daily_data = df['productivity_score'].resample('D').mean()
            daily_data = daily_data.fillna(method='ffill').fillna(method='bfill')
            df_daily = daily_data.reset_index()
            df_daily.columns = ['datetime', 'productivity_score']
            df_daily.set_index('datetime', inplace=True)
            return df_daily

        return df

    def train_linear_model(self) -> bool:
        """Train linear regression model with proper feature engineering."""
        try:
            with self.lock:
                if len(self.productivity_history) < self.min_samples_for_training:
                    return False

                data = list(self.productivity_history)
                df = pd.DataFrame(data)

            # Feature engineering
            df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()) / (24 * 60 * 60)
            df['hours_since_start'] = (df['timestamp'] - df['timestamp'].min()) / (60 * 60)

            # Cyclical encoding for temporal patterns
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
            df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)

            # Lagged features (previous hours productivity)
            df['prev_1h'] = df['productivity_score'].shift(1).fillna(df['productivity_score'].mean())
            df['prev_2h'] = df['productivity_score'].shift(2).fillna(df['productivity_score'].mean())
            df['rolling_3h_mean'] = df['productivity_score'].rolling(3, min_periods=1).mean()

            feature_cols = ['days_since_start', 'hours_since_start', 'day_sin', 'day_cos', 
                          'hour_sin', 'hour_cos', 'is_weekend', 'is_work_hours',
                          'prev_1h', 'prev_2h', 'rolling_3h_mean']
            
            X = df[feature_cols].fillna(0)
            y = df['productivity_score']

            X_scaled = self.models['linear']['scaler'].fit_transform(X)

            model = LinearRegression()
            model.fit(X_scaled, y)
            
            self.models['linear']['model'] = model
            self.models['linear']['trained'] = True

            # Calculate metrics
            y_pred = model.predict(X_scaled)
            mse = mean_squared_error(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            self.model_performance['linear'] = {'mse': mse, 'mae': mae, 'r2': r2}

            return True

        except Exception as e:
            print(f"Error training linear model: {e}")
            return False

    def train_gradient_boost_model(self) -> bool:
        """Train Gradient Boosting model for better non-linear relationships."""
        try:
            with self.lock:
                if len(self.productivity_history) < self.min_samples_for_training:
                    return False

                data = list(self.productivity_history)
                df = pd.DataFrame(data)

            # Feature engineering (same as linear)
            df['days_since_start'] = (df['timestamp'] - df['timestamp'].min()) / (24 * 60 * 60)
            df['hours_since_start'] = (df['timestamp'] - df['timestamp'].min()) / (60 * 60)
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
            df['hour_sin'] = np.sin(2 * np.pi * df['hour_of_day'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour_of_day'] / 24)
            df['prev_1h'] = df['productivity_score'].shift(1).fillna(df['productivity_score'].mean())
            df['prev_2h'] = df['productivity_score'].shift(2).fillna(df['productivity_score'].mean())
            df['rolling_3h_mean'] = df['productivity_score'].rolling(3, min_periods=1).mean()

            feature_cols = ['days_since_start', 'hours_since_start', 'day_sin', 'day_cos',
                          'hour_sin', 'hour_cos', 'is_weekend', 'is_work_hours',
                          'prev_1h', 'prev_2h', 'rolling_3h_mean']

            X = df[feature_cols].fillna(0)
            y = df['productivity_score']

            X_scaled = self.models['gradient_boost']['scaler'].fit_transform(X)

            model = GradientBoostingRegressor(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
            model.fit(X_scaled, y)

            self.models['gradient_boost']['model'] = model
            self.models['gradient_boost']['trained'] = True

            y_pred = model.predict(X_scaled)
            mse = mean_squared_error(y, y_pred)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            self.model_performance['gradient_boost'] = {'mse': mse, 'mae': mae, 'r2': r2}

            return True

        except Exception as e:
            print(f"Error training gradient boost model: {e}")
            return False

    def train_arima_model(self) -> bool:
        """Train ARIMA model for time series forecasting."""
        try:
            with self.lock:
                if len(self.productivity_history) < self.min_samples_for_training:
                    return False

                data = list(self.productivity_history)
                df = pd.DataFrame(data)

            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('datetime', inplace=True)

            # Resample to hourly for better ARIMA performance
            hourly_data = df['productivity_score'].resample('H').mean()
            hourly_data = hourly_data.fillna(method='ffill').fillna(method='bfill')

            if len(hourly_data) < 24:  # Need at least 24 hours
                return False

            # Auto ARIMA parameter selection
            try:
                self.models['arima']['model'] = ARIMA(hourly_data, order=(1, 1, 1))
                self.models['arima']['model'] = self.models['arima']['model'].fit()
                self.models['arima']['trained'] = True
                return True
            except Exception as e:
                print(f"ARIMA fitting error: {e}")
                return False

        except Exception as e:
            print(f"Error training ARIMA model: {e}")
            return False

    def train_sarimax_model(self) -> bool:
        """Train SARIMAX model with seasonal components."""
        try:
            with self.lock:
                if len(self.productivity_history) < self.min_samples_for_training * 2:
                    return False

                data = list(self.productivity_history)
                df = pd.DataFrame(data)

            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('datetime', inplace=True)

            # Resample to daily
            daily_data = df['productivity_score'].resample('D').mean()
            daily_data = daily_data.fillna(method='ffill').fillna(method='bfill')

            if len(daily_data) < 14:  # Need at least 2 weeks
                return False

            try:
                self.models['sarimax']['model'] = SARIMAX(daily_data, order=(1, 1, 1), 
                                                          seasonal_order=(1, 1, 1, 7))
                self.models['sarimax']['model'] = self.models['sarimax']['model'].fit(disp=False)
                self.models['sarimax']['trained'] = True
                return True
            except Exception as e:
                print(f"SARIMAX fitting error: {e}")
                return False

        except Exception as e:
            print(f"Error training SARIMAX model: {e}")
            return False

    def train_prophet_model(self) -> bool:
        """Train Facebook Prophet model for robust time series forecasting."""
        if not HAS_PROPHET:
            return False

        try:
            with self.lock:
                if len(self.productivity_history) < self.min_samples_for_training:
                    return False

                data = list(self.productivity_history)
                df = pd.DataFrame(data)

            df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
            df.set_index('datetime', inplace=True)

            # Resample to hourly
            hourly_data = df['productivity_score'].resample('H').mean()
            hourly_data = hourly_data.fillna(method='ffill').fillna(method='bfill')

            if len(hourly_data) < 48:  # Need at least 2 days
                return False

            # Prepare data for Prophet
            prophet_df = hourly_data.reset_index()
            prophet_df.columns = ['ds', 'y']

            model = Prophet(yearly_seasonality=False, weekly_seasonality=True, 
                          daily_seasonality=True, interval_width=0.95)
            model.fit(prophet_df)

            self.models['prophet']['model'] = model
            self.models['prophet']['trained'] = True
            return True

        except Exception as e:
            print(f"Error training Prophet model: {e}")
            return False

    def train_lstm_model(self) -> bool:
        """Train LSTM neural network for complex patterns."""
        if not HAS_TENSORFLOW:
            return False

        try:
            with self.lock:
                if len(self.time_series_data) < self.min_samples_for_training * 3:
                    return False

                data = np.array(list(self.time_series_data))

            # Normalize data
            scaler = self.models['lstm']['scaler']
            data_scaled = scaler.fit_transform(data.reshape(-1, 1))

            # Prepare sequences
            seq_length = 12  # 12 hours
            X, y = [], []

            for i in range(len(data_scaled) - seq_length):
                X.append(data_scaled[i:i+seq_length])
                y.append(data_scaled[i+seq_length])

            X = np.array(X)
            y = np.array(y)

            if len(X) < 20:  # Need sufficient samples
                return False

            # Build LSTM model
            model = keras.Sequential([
                layers.LSTM(64, activation='relu', input_shape=(seq_length, 1), return_sequences=True),
                layers.Dropout(0.2),
                layers.LSTM(32, activation='relu'),
                layers.Dropout(0.2),
                layers.Dense(16, activation='relu'),
                layers.Dense(1)
            ])

            model.compile(optimizer='adam', loss='mse', metrics=['mae'])
            model.fit(X, y, epochs=20, batch_size=8, verbose=0, validation_split=0.1)

            self.models['lstm']['model'] = model
            self.models['lstm']['trained'] = True
            return True

        except Exception as e:
            print(f"Error training LSTM model: {e}")
            return False

    def forecast_productivity(self, hours_ahead: int = 24) -> Dict:
        """Generate productivity forecast from all available models."""
        forecasts = {}
        current_time = time.time()

        # Linear regression forecast
        if self.models['linear']['trained']:
            try:
                forecasts['linear'] = self._forecast_linear(hours_ahead, current_time)
            except Exception as e:
                print(f"Linear forecast failed: {e}")

        # Gradient Boosting forecast
        if self.models['gradient_boost']['trained']:
            try:
                forecasts['gradient_boost'] = self._forecast_gradient_boost(hours_ahead, current_time)
            except Exception as e:
                print(f"Gradient Boost forecast failed: {e}")

        # ARIMA forecast
        if self.models['arima']['trained']:
            try:
                forecasts['arima'] = self._forecast_arima(hours_ahead)
            except Exception as e:
                print(f"ARIMA forecast failed: {e}")

        # SARIMAX forecast
        if self.models['sarimax']['trained']:
            try:
                forecasts['sarimax'] = self._forecast_sarimax(hours_ahead)
            except Exception as e:
                print(f"SARIMAX forecast failed: {e}")

        # Prophet forecast
        if self.models['prophet']['trained']:
            try:
                forecasts['prophet'] = self._forecast_prophet(hours_ahead)
            except Exception as e:
                print(f"Prophet forecast failed: {e}")

        # LSTM forecast
        if self.models['lstm']['trained']:
            try:
                forecasts['lstm'] = self._forecast_lstm(hours_ahead)
            except Exception as e:
                print(f"LSTM forecast failed: {e}")

        # Ensemble forecast
        if forecasts:
            forecasts['ensemble'] = self._create_ensemble_forecast(forecasts, hours_ahead)

        return forecasts

    def _forecast_linear(self, hours_ahead: int, current_time: float) -> Dict:
        """Generate linear regression forecast."""
        future_features = []

        with self.lock:
            first_timestamp = self.productivity_history[0]['timestamp'] if self.productivity_history else current_time

        for i in range(hours_ahead):
            future_time = current_time + (i + 1) * 3600  # 1 hour
            local_time = time.localtime(future_time)
            
            day_of_week = local_time.tm_wday
            hour_of_day = local_time.tm_hour
            is_weekend = 1 if day_of_week >= 5 else 0
            is_work_hours = 1 if 9 <= hour_of_day <= 17 else 0

            days_since_start = (future_time - first_timestamp) / (24 * 3600)
            hours_since_start = (future_time - first_timestamp) / 3600
            day_sin = np.sin(2 * np.pi * day_of_week / 7)
            day_cos = np.cos(2 * np.pi * day_of_week / 7)
            hour_sin = np.sin(2 * np.pi * hour_of_day / 24)
            hour_cos = np.cos(2 * np.pi * hour_of_day / 24)

            # Use last known values for lagged features
            with self.lock:
                if len(self.time_series_data) > 0:
                    prev_1h = list(self.time_series_data)[-1]
                    prev_2h = list(self.time_series_data)[-2] if len(self.time_series_data) > 1 else prev_1h
                    rolling_3h_mean = np.mean(list(self.time_series_data)[-3:])
                else:
                    prev_1h = 50
                    prev_2h = 50
                    rolling_3h_mean = 50

            features = [days_since_start, hours_since_start, day_sin, day_cos, hour_sin, hour_cos, 
                       is_weekend, is_work_hours, prev_1h, prev_2h, rolling_3h_mean]
            future_features.append(features)

        future_features_scaled = self.models['linear']['scaler'].transform(future_features)
        predictions = self.models['linear']['model'].predict(future_features_scaled)
        predictions = np.clip(predictions, 0, 100)

        return {
            'predictions': predictions.tolist(),
            'confidence_intervals': None,
            'method': 'Linear Regression'
        }

    def _forecast_gradient_boost(self, hours_ahead: int, current_time: float) -> Dict:
        """Generate Gradient Boosting forecast."""
        future_features = []

        with self.lock:
            first_timestamp = self.productivity_history[0]['timestamp'] if self.productivity_history else current_time

        for i in range(hours_ahead):
            future_time = current_time + (i + 1) * 3600
            local_time = time.localtime(future_time)
            
            day_of_week = local_time.tm_wday
            hour_of_day = local_time.tm_hour
            is_weekend = 1 if day_of_week >= 5 else 0
            is_work_hours = 1 if 9 <= hour_of_day <= 17 else 0

            days_since_start = (future_time - first_timestamp) / (24 * 3600)
            hours_since_start = (future_time - first_timestamp) / 3600
            day_sin = np.sin(2 * np.pi * day_of_week / 7)
            day_cos = np.cos(2 * np.pi * day_of_week / 7)
            hour_sin = np.sin(2 * np.pi * hour_of_day / 24)
            hour_cos = np.cos(2 * np.pi * hour_of_day / 24)

            with self.lock:
                if len(self.time_series_data) > 0:
                    prev_1h = list(self.time_series_data)[-1]
                    prev_2h = list(self.time_series_data)[-2] if len(self.time_series_data) > 1 else prev_1h
                    rolling_3h_mean = np.mean(list(self.time_series_data)[-3:])
                else:
                    prev_1h = 50
                    prev_2h = 50
                    rolling_3h_mean = 50

            features = [days_since_start, hours_since_start, day_sin, day_cos, hour_sin, hour_cos,
                       is_weekend, is_work_hours, prev_1h, prev_2h, rolling_3h_mean]
            future_features.append(features)

        future_features_scaled = self.models['gradient_boost']['scaler'].transform(future_features)
        predictions = self.models['gradient_boost']['model'].predict(future_features_scaled)
        predictions = np.clip(predictions, 0, 100)

        return {
            'predictions': predictions.tolist(),
            'confidence_intervals': None,
            'method': 'Gradient Boosting'
        }

    def _forecast_arima(self, hours_ahead: int) -> Dict:
        """Generate ARIMA forecast."""
        try:
            forecast = self.models['arima']['model'].forecast(steps=hours_ahead)
            forecast_ci = self.models['arima']['model'].get_forecast(steps=hours_ahead).conf_int()
            predictions = np.clip(forecast, 0, 100)
            confidence_intervals = forecast_ci.values.tolist()

            return {
                'predictions': predictions.tolist(),
                'confidence_intervals': confidence_intervals,
                'method': 'ARIMA'
            }
        except:
            return {'predictions': [], 'confidence_intervals': None, 'method': 'ARIMA'}

    def _forecast_sarimax(self, hours_ahead: int) -> Dict:
        """Generate SARIMAX forecast (convert to hours if needed)."""
        try:
            days_ahead = max(1, hours_ahead // 24)
            forecast = self.models['sarimax']['model'].forecast(steps=days_ahead)
            forecast_ci = self.models['sarimax']['model'].get_forecast(steps=days_ahead).conf_int()
            
            # Interpolate daily forecast to hourly
            if len(forecast) > 0:
                predictions = np.interp(np.linspace(0, len(forecast)-1, hours_ahead), 
                                       np.arange(len(forecast)), forecast)
                predictions = np.clip(predictions, 0, 100)
            else:
                predictions = [50] * hours_ahead

            return {
                'predictions': predictions.tolist(),
                'confidence_intervals': forecast_ci.values.tolist() if len(forecast_ci) > 0 else None,
                'method': 'SARIMAX'
            }
        except:
            return {'predictions': [], 'confidence_intervals': None, 'method': 'SARIMAX'}

    def _forecast_prophet(self, hours_ahead: int) -> Dict:
        """Generate Prophet forecast."""
        if not HAS_PROPHET:
            return {'predictions': [], 'confidence_intervals': None, 'method': 'Prophet'}

        try:
            future = self.models['prophet']['model'].make_future_dataframe(periods=hours_ahead, freq='H')
            forecast_df = self.models['prophet']['model'].predict(future)

            predictions = forecast_df['yhat'].tail(hours_ahead).values
            predictions = np.clip(predictions, 0, 100)

            lower = forecast_df['yhat_lower'].tail(hours_ahead).values
            upper = forecast_df['yhat_upper'].tail(hours_ahead).values

            confidence_intervals = [[lower[i], upper[i]] for i in range(len(lower))]

            return {
                'predictions': predictions.tolist(),
                'confidence_intervals': confidence_intervals,
                'method': 'Prophet'
            }
        except:
            return {'predictions': [], 'confidence_intervals': None, 'method': 'Prophet'}

    def _forecast_lstm(self, hours_ahead: int) -> Dict:
        """Generate LSTM forecast."""
        if not HAS_TENSORFLOW:
            return {'predictions': [], 'confidence_intervals': None, 'method': 'LSTM'}

        try:
            scaler = self.models['lstm']['scaler']
            seq_length = 12

            with self.lock:
                last_sequence = np.array(list(self.time_series_data)[-seq_length:])

            last_sequence_scaled = scaler.transform(last_sequence.reshape(-1, 1))
            predictions = []

            current_sequence = last_sequence_scaled.reshape(1, seq_length, 1)

            for _ in range(hours_ahead):
                next_pred = self.models['lstm']['model'].predict(current_sequence, verbose=0)
                predictions.append(next_pred[0, 0])
                current_sequence = np.append(current_sequence[0, 1:], next_pred)[np.newaxis, :, np.newaxis]

            # Inverse transform
            predictions_original = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
            predictions_original = np.clip(predictions_original, 0, 100)

            return {
                'predictions': predictions_original.flatten().tolist(),
                'confidence_intervals': None,
                'method': 'LSTM'
            }
        except:
            return {'predictions': [], 'confidence_intervals': None, 'method': 'LSTM'}

    def _create_ensemble_forecast(self, forecasts: Dict, hours_ahead: int) -> Dict:
        """Create ensemble forecast by averaging available models."""
        predictions = []
        lower_bounds = []
        upper_bounds = []

        for i in range(hours_ahead):
            day_predictions = []

            for method, forecast_data in forecasts.items():
                if method != 'ensemble' and forecast_data['predictions'] and i < len(forecast_data['predictions']):
                    pred = forecast_data['predictions'][i]
                    day_predictions.append(pred)

                    if forecast_data['confidence_intervals'] and i < len(forecast_data['confidence_intervals']):
                        ci = forecast_data['confidence_intervals'][i]
                        if isinstance(ci, (list, tuple)) and len(ci) >= 2:
                            lower_bounds.append(ci[0])
                            upper_bounds.append(ci[1])

            if day_predictions:
                predictions.append(np.mean(day_predictions))
            else:
                predictions.append(50)

        return {
            'predictions': predictions,
            'confidence_intervals': [[lower_bounds[i] if i < len(lower_bounds) else 40,
                                    upper_bounds[i] if i < len(upper_bounds) else 60]
                                   for i in range(len(predictions))],
            'method': 'Ensemble (Average)'
        }

    def get_seasonal_decomposition(self, days: int = 30) -> Optional[Dict]:
        """Get seasonal decomposition analysis."""
        try:
            df = self.get_daily_data(days)
            if len(df) < 14:
                return None

            decomposition = seasonal_decompose(df['productivity_score'], model='additive', period=7)

            return {
                'trend': decomposition.trend.tolist(),
                'seasonal': decomposition.seasonal.tolist(),
                'residual': decomposition.resid.tolist(),
                'observed': decomposition.observed.tolist(),
                'dates': [str(d) for d in df.index]
            }
        except Exception as e:
            print(f"Seasonal decomposition failed: {e}")
            return None

    def get_correlation_analysis(self, days: int = 7) -> Dict:
        """Get correlation analysis between time periods."""
        try:
            df = self.get_hourly_data(days)
            if len(df) < 24:
                return {}

            # Hour-to-hour correlation
            correlations = {}
            for lag in [1, 24]:
                if lag < len(df):
                    corr = df['productivity_score'].autocorr(lag=lag)
                    correlations[f'{lag}h_lag'] = float(corr) if not np.isnan(corr) else 0

            return correlations
        except:
            return {}

    def get_hourly_data(self, days: int = 7) -> pd.DataFrame:
        """Get hourly productivity data."""
        cutoff_time = time.time() - (days * 24 * 60 * 60)

        with self.lock:
            historical_data = [
                point for point in self.productivity_history
                if point['timestamp'] >= cutoff_time
            ]

        if not historical_data:
            return pd.DataFrame()

        df = pd.DataFrame(historical_data)
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df.set_index('datetime', inplace=True)

        hourly_data = df['productivity_score'].resample('H').mean()
        hourly_data = hourly_data.fillna(method='ffill').fillna(method='bfill')
        df_hourly = hourly_data.reset_index()
        df_hourly.columns = ['datetime', 'productivity_score']
        df_hourly.set_index('datetime', inplace=True)

        return df_hourly

    def get_model_performance_summary(self) -> Dict:
        """Get summary of all model performance metrics."""
        return {
            'models': {name: model['trained'] for name, model in self.models.items()},
            'performance': self.model_performance,
            'last_training': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.last_training_time)),
            'data_points': len(self.productivity_history)
        }

    def get_clustering_insights(self, n_clusters: int = 3) -> Dict:
        """Get productivity patterns via clustering."""
        try:
            df = self.get_daily_data(30)
            if len(df) < 10:
                return {}

            X = df[['productivity_score']].values
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X)

            return {
                'cluster_centers': kmeans.cluster_centers_.flatten().tolist(),
                'cluster_labels': clusters.tolist(),
                'inertia': float(kmeans.inertia_),
                'dates': [str(d) for d in df.index]
            }
        except:
            return {}