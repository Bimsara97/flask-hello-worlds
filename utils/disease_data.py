import random

# Since we don't have the rice_disease_fine_tuned_model.keras, we'll hardcode disease detection
# This file provides hardcoded disease data for demonstration purposes

# Common rice diseases and their information
RICE_DISEASES = {
    'bacterial_leaf_blight': {
        'scientific_name': 'Xanthomonas oryzae pv. oryzae',
        'symptoms': 'Water-soaked lesions on leaf margins that turn yellow and then white/gray as they enlarge.',
        'causes': 'Bacterial pathogen that enters through wounds or natural openings, favored by warm, humid conditions.',
        'management': 'Use resistant varieties, practice field sanitation, avoid excessive nitrogen fertilization, treat seeds with hot water or antibiotics.',
        'severity': 'high',
        'confidence': 0.92,
    },
    'bacterial_leaf_streak': {
        'scientific_name': 'Xanthomonas oryzae pv. oryzicola',
        'symptoms': 'Narrow, dark brown streaks between leaf veins that may later turn yellowish at margins.',
        'causes': 'Bacterial pathogen that enters through stomata and wounds, spreads via rain splash and irrigation.',
        'management': 'Use resistant varieties, practice crop rotation, maintain field hygiene, avoid overhead irrigation.',
        'severity': 'medium',
        'confidence': 0.87,
    },
    'brown_spot': {
        'scientific_name': 'Cochliobolus miyabeanus (Bipolaris oryzae)',
        'symptoms': 'Oval brown spots on leaves, often with yellow halos; affected seeds may have discolored husks.',
        'causes': 'Fungal infection, often associated with nutrient deficiency especially potassium.',
        'management': 'Balanced fertilization, particularly potassium; fungicide treatment; proper spacing; resistant varieties.',
        'severity': 'medium',
        'confidence': 0.90,
    },
    'blast': {
        'scientific_name': 'Magnaporthe oryzae',
        'symptoms': 'Diamond-shaped lesions on leaves with dark borders and gray/white centers, can affect stems and panicles.',
        'causes': 'Fungal pathogen that spreads via spores, favored by high humidity and moderate temperatures.',
        'management': 'Use resistant varieties, fungicide application, balanced fertilization, proper water management.',
        'severity': 'high',
        'confidence': 0.95,
    },
    'tungro': {
        'scientific_name': 'Rice tungro bacilliform virus (RTBV) and Rice tungro spherical virus (RTSV)',
        'symptoms': 'Yellow to orange discoloration of leaves, stunted growth, reduced tillering.',
        'causes': 'Viral disease transmitted by green leafhoppers (Nephotettix virescens).',
        'management': 'Vector control with insecticides, resistant varieties, adjusting planting time, removing infected plants.',
        'severity': 'high',
        'confidence': 0.88,
    },
    'healthy': {
        'scientific_name': 'N/A',
        'symptoms': 'No disease symptoms, normal green coloration, vigorous growth.',
        'causes': 'N/A',
        'management': 'Maintain balanced nutrition, proper water management, regular monitoring for early disease detection.',
        'severity': 'none',
        'confidence': 0.93,
    }
}

# List of diseases for random selection
DISEASE_LIST = list(RICE_DISEASES.keys())

def get_disease_prediction(image_path, is_demo=False):
    """
    Return hardcoded disease prediction data
    In a real application, this would call the model to analyze the image
    
    Args:
        image_path: Path to the uploaded image
        is_demo: Whether this is a demo request
        
    Returns:
        dict: Disease prediction data
    """
    if is_demo:
        # For demo, always return blast disease
        disease = 'blast'
    else:
        # For real uploads, return a random disease (excluding healthy 70% of the time)
        non_healthy = [d for d in DISEASE_LIST if d != 'healthy']
        weighted_list = non_healthy * 7 + ['healthy'] * 3  # 70% disease, 30% healthy
        disease = random.choice(weighted_list)
    
    disease_info = RICE_DISEASES[disease]
    
    # Create a prediction probabilities dict for visualization
    probabilities = {}
    for d in DISEASE_LIST:
        if d == disease:
            probabilities[d] = disease_info['confidence']
        else:
            # Assign lower probabilities to other diseases
            probabilities[d] = round(random.uniform(0.01, 0.10), 2)
    
    # Normalize probabilities to ensure they sum to 1
    total = sum(probabilities.values())
    probabilities = {k: v/total for k, v in probabilities.items()}
    
    return {
        'disease': disease,
        'confidence': disease_info['confidence'],
        'severity': disease_info['severity'],
        'probabilities': probabilities
    }

def get_disease_info(disease_name):
    """
    Get detailed information about a specific disease
    
    Args:
        disease_name: Name of the disease
        
    Returns:
        dict: Disease information
    """
    if disease_name in RICE_DISEASES:
        return RICE_DISEASES[disease_name]
    else:
        # Return default info if disease not found
        return {
            'scientific_name': 'Unknown',
            'symptoms': 'Information not available',
            'causes': 'Information not available',
            'management': 'Please consult an agricultural expert',
            'severity': 'unknown',
            'confidence': 0.5
        }