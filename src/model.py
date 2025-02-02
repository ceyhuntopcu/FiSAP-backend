import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

from config import MODEL_PATH

class WildfireLSTM(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(WildfireLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return self.sigmoid(out)


def preprocess_test_df(df, feature_columns, sequence_length=24):
    """Processes test data: normalizes features and creates 24-hour sequences."""

    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Extract date (for reporting)
    df['date'] = df['timestamp'].dt.date

    # Normalize features using the same scaler as training
    scaler = StandardScaler()
    df[feature_columns] = scaler.fit_transform(df[feature_columns])

    # Drop timestamp before creating sequences
    df.drop(columns=['timestamp'], inplace=True)

    # Create sequences for the model
    X_test, dates = create_test_sequences(df, feature_columns, sequence_length)

    return X_test, dates


def create_test_sequences(data, feature_cols, sequence_length=24):
    """Creates 24-hour sequences from environmental data."""
    X, dates = [], []
    for i in range(len(data) - sequence_length):
        X.append(data.iloc[i:i + sequence_length][feature_cols].values)
        dates.append(data.iloc[i + sequence_length]['date'])  # Store corresponding date
    return np.array(X), dates

def predict_fire_risk(model, device, X_test, dates):
    """Runs inference and aggregates predictions to a single daily prediction."""

    with torch.no_grad():
        X_test_tensor = torch.tensor(X_test, dtype=torch.float32).to(device)
        predictions = model(X_test_tensor).cpu().numpy()

    # Convert probabilities to binary predictions
    binary_predictions = (predictions > 0.5).astype(int)

    # Aggregate predictions to a single daily value (max value of the day)
    df_results = pd.DataFrame({"Date": dates, "Fire_Predicted": binary_predictions.flatten()})
    df_daily = df_results.groupby("Date")["Fire_Predicted"].max().reset_index()  # Ensure fire if any hour predicts fire

    return df_daily

def load_trained_model(model_path, input_size, hidden_size=64, num_layers=2, output_size=1):
    """Loads the trained LSTM model from file."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = WildfireLSTM(input_size, hidden_size, num_layers, output_size).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model, device

def predict(df):

    feature_columns = ['temperature', 'humidity', 'wind_speed', 'precipitation',
                       'vegetation_index', 'human_activity_index']

    X_test, dates = preprocess_test_df(df, feature_columns)

    # Load trained model
    model, device = load_trained_model(MODEL_PATH, input_size=len(feature_columns))

    # Make predictions
    df_results = predict_fire_risk(model, device, X_test, dates)
    return df_results
