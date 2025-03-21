import os
import numpy as np
from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
from utils.model_loader import load_models
from utils.predictions import (
    predict_soil_nutrients,
    predict_irrigation,
    get_irrigation_recommendations,
    get_fertilizer_recommendations
)
from utils.disease_data import get_disease_prediction, get_disease_info

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Load models at startup
nutrient_model, irrigation_model = load_models()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Get form data
        ph_value = float(request.form.get('ph', 7.0))
        temperature = float(request.form.get('temperature', 25.0))

        # Debug output
        print(f"Form data received - pH: {ph_value}, Temperature: {temperature}")
        print(f"Files in request: {list(request.files.keys())}")

        # Process file upload if provided
        uploaded_image_path = None
        if 'image' in request.files:
            file = request.files['image']
            print(f"File received: {file.filename}, Empty: {file.filename == ''}")

            if file and file.filename != '' and allowed_file(file.filename):
                # Generate a unique filename to avoid overwrites
                import time
                unique_prefix = int(time.time())
                secure_name = secure_filename(file.filename)
                filename = f"{unique_prefix}_{secure_name}"

                # Make sure upload folder exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                # Save the file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                print(f"File saved successfully to: {filepath}")

                # Generate URL for the template
                uploaded_image_path = url_for('static', filename=f'uploads/{filename}')
                print(f"Image path for template: {uploaded_image_path}")
            else:
                print("No valid file provided or file type not allowed")
        else:
            print("No 'image' field in the request files")

        # Make predictions
        print("Making predictions...")
        soil_nutrients = predict_soil_nutrients(nutrient_model, ph_value)
        irrigation_data = predict_irrigation(irrigation_model, temperature)

        # Get recommendations
        print("Generating recommendations...")
        fertilizer_recommendations = get_fertilizer_recommendations(soil_nutrients)
        irrigation_recommendations = get_irrigation_recommendations(irrigation_data, temperature)

        # For disease, use hardcoded predictions since model is unavailable
        disease_results = get_disease_prediction(uploaded_image_path)
        disease_info = get_disease_info(disease_results['disease'])

        # Prepare response data
        results = {
            'soil_nutrients': soil_nutrients,
            'irrigation_data': irrigation_data,
            'fertilizer_recommendations': fertilizer_recommendations,
            'irrigation_recommendations': irrigation_recommendations,
            'disease_results': disease_results,
            'disease_info': disease_info,
            'image_path': uploaded_image_path
        }

        print(f"Results prepared. Image path: {uploaded_image_path}")

        # Return JSON response for AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(results)

        # Return rendered template for direct form submissions
        return render_template('index.html', results=results)

    except Exception as e:
        # Log the full error with traceback
        import traceback
        print(f"Error in analyze route: {str(e)}")
        print(traceback.format_exc())

        # Return error page or message
        return render_template('index.html', error=f"An error occurred: {str(e)}")


@app.route('/analyze_demo', methods=['GET'])
def analyze_demo():
    """Demo route for the 'See a demo' button"""
    try:
        # Predefined values for the demo
        ph_value = 6.5
        temperature = 28.0

        # For demo, use a sample image from static/img folder if it exists
        # or check if there's any image in uploads folder to use as sample
        sample_image_path = url_for('static', filename='img/rice_sample.jpg')

        # If the sample image doesn't exist, try to find an image in uploads folder
        sample_image_file = os.path.join('static', 'img', 'rice_sample.jpg')
        if not os.path.exists(sample_image_file):
            print("Sample image not found, looking for alternatives")
            # Look for any image in uploads folder
            uploads_dir = os.path.join('static', 'uploads')
            if os.path.exists(uploads_dir):
                image_files = [f for f in os.listdir(uploads_dir)
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if image_files:
                    # Use the most recent uploaded image
                    sample_image_path = url_for('static', filename=f'uploads/{image_files[0]}')
                    print(f"Using existing upload as sample: {sample_image_path}")

        # Make predictions
        soil_nutrients = predict_soil_nutrients(nutrient_model, ph_value)
        irrigation_data = predict_irrigation(irrigation_model, temperature)

        # Get recommendations
        fertilizer_recommendations = get_fertilizer_recommendations(soil_nutrients)
        irrigation_recommendations = get_irrigation_recommendations(irrigation_data, temperature)

        # For disease, use hardcoded predictions
        disease_results = get_disease_prediction(None, is_demo=True)
        disease_info = get_disease_info(disease_results['disease'])

        # Prepare response data
        results = {
            'soil_nutrients': soil_nutrients,
            'irrigation_data': irrigation_data,
            'fertilizer_recommendations': fertilizer_recommendations,
            'irrigation_recommendations': irrigation_recommendations,
            'disease_results': disease_results,
            'disease_info': disease_info,
            'image_path': sample_image_path,
            'is_demo': True
        }

        print(f"Demo results prepared. Using image: {sample_image_path}")

        # Return rendered template for the demo
        return render_template('index.html', results=results)

    except Exception as e:
        # Log error
        import traceback
        print(f"Error in demo route: {str(e)}")
        print(traceback.format_exc())

        # Return error page
        return render_template('index.html', error=f"An error occurred in demo: {str(e)}")


if __name__ == '__main__':
    print("Starting Soil Health Monitoring application...")
    print(f"Upload folder: {os.path.abspath(app.config['UPLOAD_FOLDER'])}")

    # Ensure upload folder exists with proper permissions
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    try:
        # Create a test file to check permissions
        test_file = os.path.join(app.config['UPLOAD_FOLDER'], 'test_write.txt')
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("Upload folder is writable")
    except Exception as e:
        print(f"Warning: Upload folder may not be writable: {e}")

    app.run(debug=True)
