import os
import tensorflow as tf
from tensorflow.keras.models import load_model
import joblib
import numpy as np


def load_models():
    """
    Load the fine-tuned models for soil nutrient prediction and irrigation optimization

    Returns:
        tuple: (nutrient_model, irrigation_model)
    """
    # Model paths
    nutrient_model_path = os.path.join('models', 'crop_fine_tuned_model.keras')
    irrigation_model_path = os.path.join('models', 'best_fine_tuned_model.keras')

    try:
        # Load soil nutrient model
        print("Loading soil nutrient model...")
        nutrient_model = load_model(nutrient_model_path)
        print("Soil nutrient model loaded successfully")

        # Load irrigation model
        print("Loading irrigation optimization model...")
        irrigation_model = load_model(irrigation_model_path)
        print("Irrigation model loaded successfully")

        return nutrient_model, irrigation_model

    except Exception as e:
        print(f"Error loading models: {e}")

        # Create dummy models for testing if real models can't be loaded
        print("Creating dummy models for testing...")

        # Dummy nutrient model (1 input -> multiple outputs)
        dummy_nutrient_model = create_dummy_nutrient_model()

        # Dummy irrigation model (1 input -> 2 outputs)
        dummy_irrigation_model = create_dummy_irrigation_model()

        return dummy_nutrient_model, dummy_irrigation_model


def create_dummy_nutrient_model():
    """Create a dummy model for soil nutrient prediction"""
    inputs = tf.keras.Input(shape=(1,))
    x = tf.keras.layers.Dense(10, activation='relu')(inputs)
    outputs = tf.keras.layers.Dense(7, activation='linear')(x)  # OM, EC, N, P, K, etc.
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mse')
    return model


def create_dummy_irrigation_model():
    """Create a dummy model for irrigation recommendation"""
    inputs = tf.keras.Input(shape=(1,))
    x = tf.keras.layers.Dense(10, activation='relu')(inputs)
    outputs = tf.keras.layers.Dense(2, activation='linear')(x)  # rainfall and water usage efficiency
    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mse')
    return model


def get_scalers():
    """
    Try to load the model scalers for input/output normalization
    Returns default scalers if files don't exist
    """
    try:
        # Load scalers if they exist
        X_scaler = joblib.load(os.path.join('models', 'X_scaler.pkl'))
        y_scaler = joblib.load(os.path.join('models', 'y_scaler.pkl'))
        return X_scaler, y_scaler
    except:
        # Create basic scalers if files don't exist
        from sklearn.preprocessing import MinMaxScaler

        # Input scaler that can handle both pH and temperature
        X_scaler = MinMaxScaler()
        X_scaler.fit(np.array([[3.0], [10.0], [15.0], [40.0]]))  # pH and temperature ranges

        # Output scaler that can handle both nutrient and irrigation outputs
        y_scaler = MinMaxScaler()

        # Create a dummy array with enough dimensions for both models
        # First two columns are for irrigation: rainfall and water efficiency
        # Remaining columns are for nutrients: OM, EC, N, P, K, Mg, Fe
        y_dummy = np.array([
            [50.0, 0.2, 1.0, 0.1, 10.0, 5.0, 40.0, 2.0, 1.0],  # Min values
            [500.0, 0.9, 10.0, 2.0, 80.0, 60.0, 300.0, 50.0, 30.0]  # Max values
        ])
        y_scaler.fit(y_dummy)

        return X_scaler, y_scaler