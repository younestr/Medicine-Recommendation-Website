# Import necessary libraries
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import pandas as pd
import os
from PIL import Image
from collections import defaultdict
from urllib.parse import quote_plus


# Initialize the Flask application
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the medicine dataset
medicine_df = pd.read_excel('datasets/Medicine_Description.xlsx')

# Connect to MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="myDEEZ"
)
cursor = db.cursor()

# Function to authenticate users
def authenticate(username, password):
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    return user is not None

# Route for the login page
@app.route('/')
def login():
    return render_template('login.html')

# Route for handling login form submission
@app.route('/login', methods=['POST'])
def login_submit():
    username = request.form['username']
    password = request.form['password']
    if authenticate(username, password):
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password', 'error')
        return redirect(url_for('login'))

# Route for the registration page
@app.route('/register')
def register():
    return render_template('register.html')

# Route for handling registration form submission
@app.route('/register', methods=['POST'])
def register_submit():
    username = request.form['username']
    password = request.form['password']

    # Check if the username already exists in the database
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        flash('Username already exists. Please choose a different one.', 'error')
        return redirect(url_for('register'))

    # Insert the new user into the database
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    except mysql.connector.Error as err:
        flash(f"Error: {err.msg}", 'error')
        return redirect(url_for('register'))

# Route for the dashboard page (after successful login)
@app.route('/dashboard')
def dashboard():
    reasons = ['Acne', 'Adhd', 'Allergies', 'Alzheimer', 'Amoebiasis', 'Anaemia', 'Angina', 'Anxiety', 'Appetite', 'Arrhythmiasis', 'Arthritis', 'Cleanser', 'Constipation', 'Contraception', 'Dandruff', 'Depression', 'Diabetes', 'Diarrhoea', 'Digestion', 'Fever', 'Fungal', 'General', 'Glaucoma', 'Gout', 'Haematopoiesis', 'Haemorrhoid', 'Hyperpigmentation', 'Hypertension', 'Hyperthyroidism', 'Hypnosis', 'Hypotension', 'Hypothyroidism', 'Infection', 'Leprosy', 'Malarial', 'Migraine', 'Mydriasis', 'Osteoporosis', 'Pain', 'Parkinson', 'Psychosis', 'Pyrexia', 'Scabies', 'Schizophrenia', 'Smoking', 'Supplement', 'Thrombolysis', 'Vaccines', 'Vertigo', 'Viral', 'Wound']
    return render_template('dashboard.html', reasons=reasons)   


def resize_images(image_dir, target_size=(256, 256)):
    for filename in os.listdir(image_dir):
        if filename.endswith('.png'):
            # Open the image file
            image_path = os.path.join(image_dir, filename)
            img = Image.open(image_path)
            
            # Resize the image
            img_resized = img.resize(target_size, Image.ANTIALIAS)
            
            # Save the resized image, overwrite the original
            img_resized.save(image_path)


# Define the directory where the images are stored
image_dir = os.path.join(app.root_path, 'static', 'images')
resize_images(image_dir, target_size=(256, 256))


@app.route('/recommend', methods=['POST'])
def recommend():
    reason = request.form['reason']
    recommended_medicines = medicine_df[medicine_df['Reason'] == reason]['Drug_Name'].unique()
    
    # Define the file paths for each medicine type icon
    med_icons = {
        'Tablet': os.path.join(image_dir, 'tablet.png'),
        'Injection': os.path.join(image_dir, 'injection.png'),
        'Capsule': os.path.join(image_dir, 'capsule.png'),
        'Gel': os.path.join(image_dir, 'gel.png'),
        'Solution': os.path.join(image_dir, 'solution.png'),
        'Ointment': os.path.join(image_dir, 'ointment.png'),
        'Powder': os.path.join(image_dir, 'powder.png'),
        'Cream': os.path.join(image_dir, 'cream.png'),
        'Other': os.path.join(image_dir, 'other.png')
    }

    # Initialize a dictionary to hold recommended medicines with purchase links
    recommended_medicines_with_links = {med_type: [] for med_type in med_icons.keys()}

    # Generate purchase links for each recommended medicine
    for med in recommended_medicines:
        # Determine the type of medicine
        med_type = classify_med_type(med)
        
        # Generate the purchase link for the medicine
        purchase_link = f"https://pharmeasy.in/search/all?name={quote_plus(med)}"
        
        # Add the medicine and its purchase link to the dictionary
        recommended_medicines_with_links[med_type].append((med, purchase_link))

    return render_template('recommendation.html', reason=reason, recommended_medicines=recommended_medicines_with_links, med_icons=med_icons)

def classify_med_type(med):
    # Classify medicine type based on its name
    med = med.lower()
    if 'tablet' in med:
        return 'Tablet'
    elif 'injection' in med:
        return 'Injection'
    elif 'capsule' in med:
        return 'Capsule'
    elif 'gel' in med:
        return 'Gel'
    elif 'solution' in med:
        return 'Solution'
    elif 'ointment' in med:
        return 'Ointment'
    elif 'powder' in med:
        return 'Powder'
    elif 'cream' in med:
        return 'Cream'
    else:
        return 'Other'

# Run the Flask application
if __name__ == '__main__':
    app.run(debug=True)
