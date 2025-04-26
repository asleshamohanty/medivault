from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Prescription, MedicationReminder, Appointment, PatientAccess, MedicalHistory, LabReport, DoctorRequest, MedicineEntry
import logging

logger = logging.getLogger(__name__)

patient_bp = Blueprint('patient', __name__)

def get_doctor_name(doctor_id):
    doctor = User.query.get(doctor_id)
    return doctor.name if doctor else "Unknown Doctor"

def extract_user_identity():
    current_user = get_jwt_identity()
    return current_user['user_id'], current_user['role']

@patient_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def patient_dashboard():
    try:
        current_user = get_jwt_identity()
        logger.info(f"JWT Identity: {current_user}")
        
        if current_user['role'] != 'Patient':
            logger.warning(f"Unauthorized access attempt by user {current_user['user_id']} with role {current_user['role']}")
            return jsonify({"error": "Unauthorized"}), 403

        user_id = current_user['user_id']

        # Fetch all necessary data in parallel queries
        medical_history = MedicalHistory.query.filter_by(patient_id=user_id).first()
        prescriptions = Prescription.query.filter_by(patient_id=user_id).all()
        appointments = Appointment.query.filter_by(patient_id=user_id).all()
        lab_reports = LabReport.query.filter_by(patient_id=user_id).all()
        access_requests = DoctorRequest.query.filter_by(patient_id=user_id, status='Pending').all()
        current_access = PatientAccess.query.filter_by(patient_id=user_id, access_granted=True).all()
        reminders = MedicationReminder.query.filter_by(patient_id=user_id).all()

        medical_history_data = {
            'disease': medical_history.disease if medical_history else '',
            'allergies': medical_history.allergies if medical_history else '',
            'surgery_history': medical_history.surgery_history if medical_history else ''
        }

        # Prepare prescriptions data with doctor names
        prescriptions_data = [{
            'prescription_id': prescription.prescription_id,
            'doctor_name': get_doctor_name(prescription.doctor_id),
            'diagnosis': prescription.diagnosis,
            'date_issued': prescription.date_issued.strftime('%Y-%m-%d'),
            'medicines': [{
                'name': medicine.name,
                'dosage': medicine.dosage,
                'frequency': medicine.frequency,
                'timing': medicine.timing
            } for medicine in prescription.medicine_entries]
        } for prescription in prescriptions]

        # Prepare appointments data with doctor names
        appointments_data = [{
            'appointment_id': appointment.appointment_id,
            'doctor_name': get_doctor_name(appointment.doctor_id),
            'date': appointment.date_time.strftime('%Y-%m-%d'),
            'time': appointment.date_time.strftime('%H:%M'),
            'status': appointment.status
        } for appointment in appointments]

        # Prepare lab reports data
        lab_reports_data = [{
            'report_id': report.report_id,
            'report_type': report.report_type,
            'file_url': report.file_url,
            'uploaded_on': report.uploaded_on.strftime('%Y-%m-%d')
        } for report in lab_reports]

        # Prepare access requests data
        access_requests_data = [{
            'request_id': request.request_id,
            'doctor_name': get_doctor_name(request.doctor_id),
            'status': request.status,
            'purpose': request.purpose,
            'request_date': request.request_date.strftime('%Y-%m-%d') if request.request_date else None
        } for request in access_requests]

        # Prepare current access data
        current_access_data = [{
            'access_id': access.access_id,
            'doctor_name': get_doctor_name(access.doctor_id),
            'granted_date': access.granted_on.strftime('%Y-%m-%d') if access.granted_on else None,
            'expiry_date': access.expiry_date.strftime('%Y-%m-%d') if access.expiry_date else None
        } for access in current_access]

        # Prepare reminders data
        reminders_data = [{
            'reminder_id': reminder.reminder_id,
            'medicine_name': MedicineEntry.query.get(reminder.medicine_entry_id).name if reminder.medicine_entry_id else 'Unknown Medicine',
            'dosage': MedicineEntry.query.get(reminder.medicine_entry_id).dosage if reminder.medicine_entry_id else 'Unknown Dosage',
            'time': reminder.remind_at.strftime('%H:%M'),
            'is_active': reminder.is_active
        } for reminder in reminders]

        return jsonify({
            'medical_history': medical_history_data,
            'prescriptions': prescriptions_data,
            'appointments': appointments_data,
            'lab_reports': lab_reports_data,
            'access_requests': access_requests_data,
            'current_access': current_access_data,
            'reminders': reminders_data
        })

    except Exception as e:
        logger.error(f"Error in patient_dashboard: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@patient_bp.route('/prescriptions', methods=['GET'])
@jwt_required()
def get_prescriptions():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'Patient':
            return jsonify({"error": "Unauthorized"}), 403

        prescriptions = Prescription.query.filter_by(patient_id=current_user['user_id']).all()
        prescriptions_data = [{
            'prescription_id': prescription.prescription_id,
            'doctor_name': get_doctor_name(prescription.doctor_id),
            'diagnosis': prescription.diagnosis,
            'date_issued': prescription.date_issued.strftime('%Y-%m-%d'),
            'medicines': [{
                'name': medicine.name,
                'dosage': medicine.dosage,
                'frequency': medicine.frequency,
                'timing': medicine.timing
            } for medicine in prescription.medicine_entries]
        } for prescription in prescriptions]

        return jsonify(prescriptions_data), 200

    except Exception as e:
        logger.error(f"Error in get_prescriptions: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@patient_bp.route('/reminders', methods=['GET'])
@jwt_required()
def get_reminders():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'Patient':
            return jsonify({"error": "Unauthorized"}), 403

        reminders = MedicationReminder.query.filter_by(patient_id=current_user['user_id']).all()
        reminders_data = [{
            'reminder_id': reminder.reminder_id,
            'medicine_name': MedicineEntry.query.get(reminder.medicine_entry_id).name if reminder.medicine_entry_id else 'Unknown Medicine',
            'dosage': MedicineEntry.query.get(reminder.medicine_entry_id).dosage if reminder.medicine_entry_id else 'Unknown Dosage',
            'time': reminder.remind_at.strftime('%H:%M'),
            'is_active': reminder.is_active
        } for reminder in reminders]

        return jsonify(reminders_data), 200

    except Exception as e:
        logger.error(f"Error in get_reminders: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@patient_bp.route('/appointments', methods=['GET'])
@jwt_required()
def get_appointments():
    try:
        current_user = get_jwt_identity()
        if current_user['role'] != 'Patient':
            return jsonify({"error": "Unauthorized"}), 403

        appointments = Appointment.query.filter_by(patient_id=current_user['user_id']).all()
        appointments_data = [{
            'appointment_id': appointment.appointment_id,
            'doctor_name': get_doctor_name(appointment.doctor_id),
            'date': appointment.date_time.strftime('%Y-%m-%d'),
            'time': appointment.date_time.strftime('%H:%M'),
            'status': appointment.status
        } for appointment in appointments]

        return jsonify(appointments_data), 200

    except Exception as e:
        logger.error(f"Error in get_appointments: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@patient_bp.route('/grant-access', methods=['POST'])
@jwt_required()
def grant_access():
    try:
        # Get the user ID from the token identity
        current_user = get_jwt_identity()
        
        if current_user['role'] != 'Patient':
            return jsonify({"error": "Unauthorized"}), 403

        doctor_id = request.json.get('doctor_id')
        if not doctor_id:
            return jsonify({"error": "Doctor ID is required"}), 400

        existing_access = PatientAccess.query.filter_by(patient_id=current_user['user_id'], doctor_id=doctor_id).first()
        if existing_access:
            return jsonify({"message": "Access already granted"}), 200

        new_access = PatientAccess(patient_id=current_user['user_id'], doctor_id=doctor_id, access_granted=True)
        try:
            db.session.add(new_access)
            db.session.commit()
            return jsonify({"message": "Access granted successfully"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error granting access"}), 500
    except Exception as e:
        logger.error(f"Error in grant_access: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
