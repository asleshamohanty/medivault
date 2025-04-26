from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Doctor, Appointment, DoctorRequest, PatientAccess, Prescription, MedicineEntry
from datetime import datetime

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/eligible-patients', methods=['GET'])
@jwt_required()
def get_eligible_patients():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Doctor':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Fetch patients who have had appointments with the logged-in doctor
        patients = db.session.query(User.user_id, User.name, User.username).join(
            Appointment, User.user_id == Appointment.patient_id
        ).filter(
            Appointment.doctor_id == current_user['user_id']
        ).distinct().all()

        patients_data = [{
            'id': patient.user_id,
            'name': patient.name,
            'username': patient.username
        } for patient in patients]

        return jsonify(patients_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@doctor_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def doctor_dashboard():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Doctor':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Fetch doctor's patients with names in the same query
        patients = db.session.query(User.user_id, User.name, User.username).join(
            Appointment, User.user_id == Appointment.patient_id
        ).filter(
            Appointment.doctor_id == current_user['user_id']
        ).distinct().all()

        patients_data = [{
            'id': patient.user_id,
            'name': patient.name,
            'username': patient.username
        } for patient in patients]

        # Fetch doctor's appointments with patient names in the same query
        appointments = db.session.query(
            Appointment.appointment_id, 
            Appointment.patient_id, 
            Appointment.date, 
            Appointment.time, 
            Appointment.purpose, 
            Appointment.status,
            User.name.label('patient_name')  # Fetch patient name in the same query
        ).join(User, User.user_id == Appointment.patient_id).filter(
            Appointment.doctor_id == current_user['user_id']
        ).all()

        appointments_data = [{
            'id': appointment.appointment_id,
            'patient_id': appointment.patient_id,
            'patient_name': appointment.patient_name,
            'date': appointment.date.strftime('%Y-%m-%d'),
            'time': appointment.time.strftime('%H:%M'),
            'purpose': appointment.purpose,
            'status': appointment.status
        } for appointment in appointments]

        return jsonify({
            'patients': patients_data,
            'appointments': appointments_data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@doctor_bp.route('/prescriptions', methods=['POST'])
@jwt_required()
def create_prescription():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Doctor':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        diagnosis = data.get('diagnosis')
        medicines = data.get('medicines', [])

        # Verify patient exists and has had an appointment with this doctor
        patient = User.query.get(patient_id)
        if not patient or patient.role != 'Patient':
            return jsonify({"error": "Patient not found"}), 404

        appointment = Appointment.query.filter_by(
            doctor_id=current_user['user_id'],
            patient_id=patient_id
        ).first()
        if not appointment:
            return jsonify({"error": "Patient has not had an appointment with this doctor"}), 400

        # Create prescription
        prescription = Prescription(
            patient_id=patient_id,
            doctor_id=current_user['user_id'],
            diagnosis=diagnosis,
            date_issued=datetime.now()
        )
        db.session.add(prescription)
        db.session.flush()  # Get the prescription ID

        # Add medicines to the prescription
        for medicine in medicines:
            medicine_entry = MedicineEntry(
                prescription_id=prescription.prescription_id,
                name=medicine['name'],
                dosage=medicine['dosage'],
                frequency=medicine['frequency'],
                timing=medicine['timing']
            )
            db.session.add(medicine_entry)

        db.session.commit()

        return jsonify({
            "message": "Prescription created successfully",
            "prescription_id": prescription.prescription_id
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@doctor_bp.route('/appointments/<int:appointment_id>/complete', methods=['PUT'])
@jwt_required()
def complete_appointment(appointment_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'Doctor':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment or appointment.doctor_id != current_user['user_id']:
            return jsonify({"error": "Appointment not found"}), 404

        appointment.status = 'completed'
        db.session.commit()

        return jsonify({"message": "Appointment marked as completed"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@doctor_bp.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
@jwt_required()
def cancel_appointment(appointment_id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'Doctor':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment or appointment.doctor_id != current_user['user_id']:
            return jsonify({"error": "Appointment not found"}), 404

        appointment.status = 'cancelled'
        db.session.commit()

        return jsonify({"message": "Appointment cancelled successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@doctor_bp.route('/request-access', methods=['POST'])
@jwt_required()
def request_access():
    current_user = get_jwt_identity()
    if current_user['role'] != 'Doctor':
        return jsonify({"error": "Unauthorized"}), 403

    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        purpose = data.get('purpose')

        # Verify patient exists
        patient = User.query.get(patient_id)
        if not patient or patient.role != 'Patient':
            return jsonify({"error": "Patient not found"}), 404

        # Check if request already exists
        existing_request = DoctorRequest.query.filter_by(
            doctor_id=current_user['user_id'],
            patient_id=patient_id,
            status='pending'
        ).first()

        if existing_request:
            return jsonify({"error": "Access request already pending"}), 400

        # Create new request
        new_request = DoctorRequest(
            doctor_id=current_user['user_id'],
            patient_id=patient_id,
            purpose=purpose,
            status='pending'
        )
        db.session.add(new_request)
        db.session.commit()

        return jsonify({"message": "Access request sent successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
