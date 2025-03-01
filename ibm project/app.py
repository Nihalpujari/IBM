from flask import Flask, render_template, request, jsonify
import mysql.connector
from flask_cors import CORS  # Import CORS to handle cross-origin requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "2309"),
            database=os.getenv("DB_NAME", "healthcare_system")
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None  # Return None if the connection fails

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_patient', methods=['POST'])
def add_patient():
    try:
        data = request.get_json() or request.form  # Support JSON and form data
        if not data:
            print("No data received")
            return jsonify({'message': 'Failed to add patient! No data received'}), 400

        print(f"Received data: {data}")  # Debugging log

        # Extract data from the request
        name = data.get('name')
        age = data.get('age')
        gender = data.get('gender')
        contact_number = data.get('contact_number')
        address = data.get('address')
        medical_history = data.get('medicalHistory')
        admission_date = data.get('admissionDate')

        # Check if all required fields are present
        if not all([name, age, gender, contact_number, address, medical_history, admission_date]):
            return jsonify({'message': 'Failed to add patient! Missing required fields'}), 400

        # Insert patient into the database
        connection = get_db_connection()
        if not connection:
            return jsonify({'message': 'Database connection failed'}), 500

        cursor = connection.cursor()
        cursor.execute(''' 
            INSERT INTO patients (name, age, gender, contact_number, address, medical_history, admission_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (name, age, gender, contact_number, address, medical_history, admission_date))
        connection.commit()

        return jsonify({'message': 'Patient added successfully!'})

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        if connection:
            connection.rollback()
        return jsonify({'message': 'Failed to add patient! Database error occurred'}), 500
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'Failed to add patient! An error occurred'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/view_patients')
def view_patients():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'message': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM patients')
        patients = cursor.fetchall()
        return render_template('view_patients.html', patients=patients)
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({'message': 'Failed to retrieve patients! Database error occurred'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@app.route('/delete_patient/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'message': 'Database connection failed'}), 500

        cursor = connection.cursor()
        cursor.execute('DELETE FROM patients WHERE id = %s', (patient_id,))
        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({'message': 'Patient not found'}), 404

        return jsonify({'message': 'Patient deleted successfully!'})

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        if connection:
            connection.rollback()
        return jsonify({'message': 'Failed to delete patient! Database error occurred'}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
