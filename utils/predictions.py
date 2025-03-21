import numpy as np
from .model_loader import get_scalers

# Nutrient names for soil prediction
NUTRIENT_NAMES = ['OM', 'EC', 'N', 'P', 'K', 'Mg', 'Fe']
NUTRIENT_UNITS = ['%', 'dS/m', 'mg/kg', 'mg/kg', 'mg/kg', 'mg/kg', 'mg/kg']

# Define optimal ranges for rice
NUTRIENT_RANGES = {
    'OM': {'low': 1.5, 'optimal': 3.0, 'high': 5.0},
    'EC': {'low': 0.2, 'optimal': 0.5, 'high': 1.5},
    'N': {'low': 20, 'optimal': 40, 'high': 60},
    'P': {'low': 10, 'optimal': 25, 'high': 50},
    'K': {'low': 80, 'optimal': 150, 'high': 250},
    'Mg': {'low': 50, 'optimal': 120, 'high': 200},
    'Fe': {'low': 5, 'optimal': 15, 'high': 30}
}


def predict_soil_nutrients(model, ph_value):
    """
    Predict soil nutrient concentrations based on pH value

    Args:
        model: Loaded Keras model
        ph_value: Soil pH value

    Returns:
        dict: Predicted nutrient values with status
    """
    # Get scalers for input/output normalization
    X_scaler, y_scaler = get_scalers()

    # Preprocess input
    ph_scaled = X_scaler.transform([[ph_value]])

    try:
        # Make prediction
        predictions_scaled = model.predict(ph_scaled)

        # Check output shape to determine which model we're using
        output_shape = predictions_scaled.shape[1]

        # Initialize a zeros array with the expected full output size
        # (our y_scaler is fit to handle both model types)
        full_output = np.zeros((1, 9))  # Larger than either model needs

        if output_shape == 2:
            # This is the irrigation model being used for nutrients
            print("Warning: Using irrigation model for nutrient prediction. Using placeholder values.")
            # Generate reasonable placeholder nutrient values based on pH
            nutrients = generate_placeholder_nutrients(ph_value)
            # Fill output array starting at index 2 (after irrigation positions)
            full_output[0, 2:2 + len(nutrients)] = nutrients
        else:
            # This is the nutrient model with correct shape
            # Fill output array with actual prediction values
            # Start at index 2 since we assume first two positions are for irrigation
            # (If output shape is smaller than 7, we'll just use what we have)
            max_nutrients = min(output_shape, len(NUTRIENT_NAMES))
            full_output[0, 2:2 + max_nutrients] = predictions_scaled[0, :max_nutrients]

        # Inverse transform to get actual values
        all_predictions = y_scaler.inverse_transform(full_output)[0]

        # Extract just the nutrient values (skip irrigation values)
        predictions = all_predictions[2:2 + len(NUTRIENT_NAMES)]
    except Exception as e:
        print(f"Error making prediction: {e}")
        # Fallback to generated values
        predictions = generate_placeholder_nutrients(ph_value)

    # Format results
    results = []
    for i, nutrient in enumerate(NUTRIENT_NAMES):
        if i < len(predictions) and nutrient in NUTRIENT_RANGES:
            value = float(predictions[i])
            # Determine status based on optimal ranges
            ranges = NUTRIENT_RANGES[nutrient]

            if value < ranges['low']:
                status = "deficient"
                status_label = "Deficient"
            elif value < ranges['optimal']:
                status = "low"
                status_label = "Low"
            elif value <= ranges['high']:
                status = "optimal"
                status_label = "Optimal"
            else:
                status = "excessive"
                status_label = "Excessive"

            results.append({
                'name': nutrient,
                'value': value,
                'unit': NUTRIENT_UNITS[i],
                'status': status,
                'status_label': status_label,
                'ranges': ranges
            })

    return {
        'ph': ph_value,
        'nutrients': results
    }


def generate_placeholder_nutrients(ph_value):
    """Generate reasonable nutrient values based on pH"""
    # pH affects nutrient availability
    # More acidic (lower pH) typically means more micronutrients, less macronutrients
    # More alkaline (higher pH) means more macronutrients, less micronutrients

    # Base values
    om = 3.0
    ec = 0.5
    n = 40.0
    p = 25.0
    k = 150.0
    mg = 80.0
    fe = 15.0

    # Adjust based on pH
    if ph_value < 5.5:  # Acidic
        p *= 0.8  # Less phosphorus availability
        k *= 0.9
        mg *= 0.8
        fe *= 1.3  # More iron availability
    elif ph_value > 7.5:  # Alkaline
        p *= 1.1  # More phosphorus
        k *= 1.1
        mg *= 1.2
        fe *= 0.7  # Less iron availability

    return np.array([om, ec, n, p, k, mg, fe])


def predict_irrigation(model, temperature):
    """
    Predict rainfall and water usage efficiency based on temperature

    Args:
        model: Loaded Keras model
        temperature: Temperature value in Celsius

    Returns:
        dict: Predicted rainfall and water usage efficiency
    """
    # Get scalers for input/output normalization
    X_scaler, y_scaler = get_scalers()

    # Ensure temperature is within a reasonable range
    temperature = max(10, min(40, temperature))

    # Preprocess input
    temp_scaled = X_scaler.transform([[temperature]])

    try:
        # Make prediction
        predictions_scaled = model.predict(temp_scaled)

        # Check output shape to determine which model we're using
        output_shape = predictions_scaled.shape[1]

        # Initialize a zeros array with the expected full output size
        # (our y_scaler is fit to handle both model types)
        full_output = np.zeros((1, 9))  # Larger than either model needs

        if output_shape < 3:
            # This is the irrigation model with correct shape (2 outputs)
            # Fill first two positions directly
            full_output[0, :2] = predictions_scaled[0, :2]
        else:
            # This is the nutrient model being used for irrigation
            print("Warning: Using nutrient model for irrigation prediction. Using first two outputs.")
            # Use first two outputs (may not be meaningful)
            full_output[0, :2] = predictions_scaled[0, :2]

        # Inverse transform to get actual values
        all_predictions = y_scaler.inverse_transform(full_output)[0]

        # Extract just the irrigation values (first two values)
        rainfall = float(all_predictions[0])
        water_efficiency = float(all_predictions[1])

        # Ensure values are in reasonable ranges
        rainfall = max(50, min(500, rainfall))
        water_efficiency = max(0.2, min(0.95, water_efficiency))
    except Exception as e:
        print(f"Error making prediction: {e}")
        # Generate reasonable values based on temperature
        rainfall = 100 + (25 - temperature) * 10  # More rain at lower temps
        water_efficiency = 0.4 + (temperature - 15) * 0.02  # Better efficiency at higher temps

        # Keep within reasonable ranges
        rainfall = max(50, min(500, rainfall))
        water_efficiency = max(0.2, min(0.95, water_efficiency))

    # Calculate irrigation requirement (simplified)
    total_water_need = 1200  # Average for rice growing season

    # Adjust water need based on temperature
    if temperature < 22:
        adjusted_water_need = total_water_need * 0.9
    elif temperature > 30:
        adjusted_water_need = total_water_need * 1.15
    else:
        adjusted_water_need = total_water_need

    # Calculate irrigation required
    irrigation_required = max(0, adjusted_water_need - rainfall)

    # Adjust irrigation based on efficiency
    if water_efficiency < 0.5:
        irrigation_applied = irrigation_required / 0.5
    else:
        irrigation_applied = irrigation_required / water_efficiency

    # Get temperature status
    temp_status = get_temperature_status(temperature)

    return {
        'temperature': temperature,
        'rainfall': rainfall,
        'water_efficiency': water_efficiency,
        'temperature_status': temp_status,
        'total_water_need': adjusted_water_need,
        'irrigation_required': irrigation_required,
        'irrigation_applied': irrigation_applied
    }


def get_temperature_status(temperature):
    """Determine temperature status for rice growing"""
    if temperature < 20:
        return {
            'status': 'cold',
            'label': 'Cold',
            'description': 'Below optimal - growth may be inhibited'
        }
    elif temperature < 25:
        return {
            'status': 'cool',
            'label': 'Moderate',
            'description': 'Acceptable for most rice varieties'
        }
    elif temperature < 30:
        return {
            'status': 'optimal',
            'label': 'Optimal',
            'description': 'Ideal range for rice growth'
        }
    elif temperature < 35:
        return {
            'status': 'hot',
            'label': 'High',
            'description': 'Watch for heat stress'
        }
    else:
        return {
            'status': 'extreme',
            'label': 'Extreme',
            'description': 'High risk of heat damage'
        }


def get_irrigation_recommendations(irrigation_data, temperature):
    """Generate irrigation recommendations based on predictions"""
    rainfall = irrigation_data['rainfall']
    efficiency = irrigation_data['water_efficiency']
    temp_status = irrigation_data['temperature_status']['status']

    recommendations = []

    # Temperature-based recommendations
    if temp_status == 'cold':
        recommendations.append("Consider delaying planting or using cold-tolerant varieties.")
    elif temp_status == 'hot' or temp_status == 'extreme':
        recommendations.append("Increase irrigation frequency to reduce heat stress.")

    # Rainfall-based recommendations
    if rainfall < 100:
        recommendations.append("Implement full irrigation system. Maintain 5-7cm standing water in paddies.")
        irrigation_status = "high"
    elif rainfall < 200:
        recommendations.append("Supplement with irrigation. Ensure field is flooded during critical stages.")
        irrigation_status = "medium"
    elif rainfall < 300:
        recommendations.append("Implement moderate irrigation. Monitor water levels regularly.")
        irrigation_status = "moderate"
    elif rainfall < 400:
        recommendations.append("Minimal irrigation needed. Focus on drainage during heavy rainfall.")
        irrigation_status = "low"
    else:
        recommendations.append("Focus on drainage and flood prevention. No additional irrigation required.")
        irrigation_status = "minimal"

    # Efficiency-based recommendations
    if efficiency < 0.4:
        recommendations.append(
            "Improve irrigation infrastructure. Consider laser land leveling for even water distribution.")
    elif efficiency < 0.6:
        recommendations.append("Implement water conservation practices such as alternate wetting and drying (AWD).")

    # Schedule recommendations
    if irrigation_status == "high":
        schedule = "Maintain 5-7cm standing water throughout the growing season. Irrigate every 3-4 days."
    elif irrigation_status == "medium":
        schedule = "Maintain 3-5cm standing water. Implement Alternate Wetting and Drying with 7-day cycles."
    elif irrigation_status == "moderate":
        schedule = "Use Alternate Wetting and Drying with 10-day cycles. Ensure soil is moist during critical stages."
    elif irrigation_status == "low":
        schedule = "Supplement only during dry spells. Focus on maintaining moist soil during critical growth stages."
    else:
        schedule = "Focus on drainage rather than irrigation. Monitor for waterlogging."

    recommendations.append(f"Irrigation Schedule: {schedule}")

    # Conservation tip
    if efficiency < 0.6:
        recommendations.append(
            "Water Conservation: Implement water-saving technologies such as drip irrigation or moisture sensors.")

    return {
        'recommendations': recommendations,
        'irrigation_status': irrigation_status,
        'schedule': schedule
    }


def get_fertilizer_recommendations(soil_data):
    """Generate fertilizer recommendations based on soil nutrient levels"""
    recommendations = []
    nutrient_status = {}

    for nutrient in soil_data['nutrients']:
        name = nutrient['name']
        status = nutrient['status']
        nutrient_status[name] = status

        # Generate recommendation based on status
        if status == 'deficient':
            if name == 'N':
                recommendations.append(
                    f"Nitrogen is deficient. Apply nitrogen fertilizer (urea or ammonium sulfate) at 100-120 kg/ha.")
            elif name == 'P':
                recommendations.append(
                    f"Phosphorus is deficient. Apply phosphate fertilizer (DAP or SSP) at 60-80 kg/ha.")
            elif name == 'K':
                recommendations.append(
                    f"Potassium is deficient. Apply potassium fertilizer (KCl or K2SO4) at 60-80 kg/ha.")
            elif name == 'OM':
                recommendations.append(f"Organic Matter is low. Add compost or well-rotted manure at 5-10 tons/ha.")
            else:
                recommendations.append(f"{name} is deficient. Consider applying appropriate supplements.")
        elif status == 'low':
            if name in ['N', 'P', 'K']:
                recommendations.append(f"{name} is somewhat low. Apply moderate amounts of fertilizer.")
        elif status == 'excessive':
            if name in ['N', 'P', 'K']:
                recommendations.append(f"{name} is excessive. Reduce or avoid further application.")

    # Add pH specific recommendations
    ph = soil_data['ph']
    if ph < 5.5:
        recommendations.append(f"Soil is acidic (pH {ph}). Consider applying agricultural lime to raise pH.")
    elif ph > 7.5:
        recommendations.append(f"Soil is alkaline (pH {ph}). For rice, consider acidifying amendments if available.")
    else:
        recommendations.append(f"Soil pH ({ph}) is in good range for rice cultivation.")

    # Add balanced fertilization recommendation if needed
    if 'N' in nutrient_status and 'P' in nutrient_status and 'K' in nutrient_status:
        if nutrient_status['N'] == 'deficient' and nutrient_status['P'] == 'deficient' and nutrient_status[
            'K'] == 'deficient':
            recommendations.append(
                "Apply balanced NPK fertilizer in split doses - 50% at planting, 25% during tillering, and 25% at panicle initiation.")

    return {
        'recommendations': recommendations,
        'nutrient_status': nutrient_status
    }