from flask import jsonify, make_response, request, Flask
import logging
import psycopg2
from flask_jwt_extended import JWTManager,create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import timedelta, datetime

# Defina a chave secreta para autenticação JWT e proteção
app = Flask(__name__)
# Defina a chave secreta para autenticação JWT
app.config['JWT_SECRET_KEY'] = 'rnd'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'jwt'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 60 * 60 * 24  # 24 hours
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['WTF_CSRF_ENABLE'] = False

# Inicialize os pacotes JWTManager e CSRFProtect com o aplicativo Flask
jwt = JWTManager(app)
#acesso a base de dados
def get_db_connection():
    db_connection = psycopg2.connect(
        user='aulaspl',
        password='aulaspl',
        host='localhost',
        port='5432',
        database='projeto'
    )
    return db_connection

class User:
    @staticmethod
    #procura se há algum utilizador com aquele na tabela das pessoas
    def get_by_id(id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM person WHERE id = %s", (id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        return user

StatusCodes = {
    'success': 200,
    'client_error': 400,
    'internal_error': 500
}

###########################################
###############END POINTS##################
###########################################
            
def insert_person(name, gender, date_birth, username, password, cursor):
    hashed_password = generate_password_hash(password)
    cursor.execute(
        """
        INSERT INTO person (name, gender, date_birth, username, password)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
        """,
        (name, gender, date_birth, username, hashed_password)
    )
    return cursor.fetchone()[0]

@app.route('/dbproj/user', methods=['PUT'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, password FROM person WHERE username = %s
        """, (username,)
    )
    user = cursor.fetchone()

    conn.close()

    
    if user and check_password_hash(user[1], password):
        access_token = create_access_token(identity=data['username'])

        response = make_response(jsonify({"msg": "Login successful"}), 200)
        response.set_cookie('jwt', access_token)
        return response
    else:
        return jsonify({"msg": "Bad username or password"}), 401


@app.route('/dbproj/register/assistant', methods=['POST'])
def register_assistant():
    data = request.json
    name = data['name']
    gender = data['gender']
    date_birth = data['date_birth']
    username = data['username']
    password = data['password']
    salary = data['salary']
    date_start = data['date_start']
    date_end = data['date_end']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if username already exists
        cursor.execute(
            """
            SELECT 1 FROM person WHERE username = %s
            """, 
            (username,)
        )
        if cursor.fetchone():
            return jsonify({"status_code": StatusCodes['client_error'], "error": "Username already exists"}), 400
        
        person_id = insert_person(name, gender, date_birth, username, password, cursor)
        
        cursor.execute(
            """
            INSERT INTO employee_contractdetails (person_id, contractdetails_salary, contractdetails_date_start, contractdetails_date_end)
            VALUES (%s, %s, %s, %s)
            """,
            (person_id, salary, date_start, date_end)
        )

        cursor.execute(
            """
            INSERT INTO assistant (employee_contractdetails_person_id)
            VALUES (%s)
            """,
            (person_id,)
        )

        conn.commit()
        return jsonify({"status_code": StatusCodes['success'], "user_id": person_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"status_code": StatusCodes['client_error'], "error": "Credenciais Inválidas"}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/dbproj/register/patient', methods=['POST'])
def register_patient():
    data = request.json
    name = data['name']
    gender = data['gender']
    date_birth = data['date_birth']
    username = data['username']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the username already exists
        cursor.execute(
            """
            SELECT 1 FROM person WHERE username = %s
            """, 
            (username,)
        )
        if cursor.fetchone():
            return jsonify({"status_code": StatusCodes['client_error'], "error": "Username already exists"}), 400
        
        person_id = insert_person(name, gender, date_birth, username, password, cursor)
        
        cursor.execute(
            """
            INSERT INTO patient (person_id)
            VALUES (%s)
            """,
            (person_id,)
        )
        conn.commit()
        return jsonify({"status_code": StatusCodes['success'], "user_id": person_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"status_code": StatusCodes['client_error'], "error": "Credenciais Inválidas"}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/dbproj/register/doctor', methods=['POST'])
def register_doctor():
    data = request.json
    name = data['name']
    gender = data['gender']
    date_birth = data['date_birth']
    username = data['username']
    password = data['password']
    license_details = data['license_details']
    salary = data['salary']
    date_start = data['date_start']
    date_end = data['date_end']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the username already exists
        cursor.execute(
            """
            SELECT 1 FROM person WHERE username = %s
            """, 
            (username,)
        )
        if cursor.fetchone():
            return jsonify({"status_code": StatusCodes['client_error'], "error": "Username already exists"}), 400
        
        person_id = insert_person(name, gender, date_birth, username, password, cursor)
        
        cursor.execute(
            """
            INSERT INTO employee_contractdetails (person_id, contractdetails_salary, contractdetails_date_start, contractdetails_date_end)
            VALUES (%s, %s, %s, %s)
            """,
            (person_id, salary, date_start, date_end)
        )

        cursor.execute(
            """
            INSERT INTO doctor_license (employee_contractdetails_person_id, license_details)
            VALUES (%s, %s)
            """,
            (person_id, license_details)
        )

        conn.commit()
        return jsonify({"status_code": StatusCodes['success'], "user_id": person_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"status_code": StatusCodes['client_error'], "error": "Credenciais Inválidas"}), 400
    finally:
        cursor.close()
        conn.close()


@app.route('/dbproj/register/nurse', methods=['POST'])
def register_nurse():
    data = request.json
    name = data['name']
    gender = data['gender']
    date_birth = data['date_birth']
    username = data['username']
    password = data['password']
    salary = data['salary']
    date_start = data['date_start']
    date_end = data['date_end']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the username already exists
        cursor.execute(
            """
            SELECT 1 FROM person WHERE username = %s
            """, 
            (username,)
        )
        if cursor.fetchone():
            return jsonify({"status_code": StatusCodes['client_error'], "error": "Username already exists"}), 400
            
        person_id = insert_person(name, gender, date_birth, username, password, cursor)
            
        cursor.execute(
            """
            INSERT INTO employee_contractdetails (person_id, contractdetails_salary, contractdetails_date_start, contractdetails_date_end)
            VALUES (%s, %s, %s, %s)
            """,
            (person_id, salary, date_start, date_end)
        )

        cursor.execute(
            """
            INSERT INTO nurse (nurse_employee_contractdetails_person_id, employee_contractdetails_person_id)
            VALUES (%s, %s)
            """,
            (person_id, person_id)
        )

        conn.commit()
        return jsonify({"status_code": StatusCodes['success'], "user_id": person_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"status_code": StatusCodes['client_error'], "error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()    


@app.route('/dbproj/appointment', methods=['POST'])
@jwt_required()
def create_appointment():
    doctor_id = request.json.get('doctor_id')
    date = request.json.get('date')
    patient_username = get_jwt_identity()

    if not doctor_id or not date:
        return jsonify({"status_code": StatusCodes['client_error'], "errors": "Doctor ID and date are required"}), 400

    try:
        # Convert string date to datetime object
        appointment_time = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        appointment_end_time = appointment_time + timedelta(hours=1)

        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o paciente existe na tabela patient usando o username
        cursor.execute("""
            SELECT pt.person_id
            FROM patient pt
            JOIN person p ON pt.person_id = p.id
            WHERE p.username = %s
            FOR UPDATE
        """, (patient_username,))
        patient = cursor.fetchone()

        if not patient:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Unauthorized access"}), 400

        patient_id = patient[0]

        # Verifica se o médico já tem um compromisso no horário solicitado (considerando 1 hora)
        cursor.execute("""
            SELECT 1
            FROM appointment
            WHERE doctor_license_employee_contractdetails_person_id = %s
            AND (date_time < %s AND (date_time + interval '1 hour') > %s)
            FOR UPDATE
        """, (doctor_id, appointment_end_time, appointment_time))
        doctor_busy = cursor.fetchone()

        if doctor_busy:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Doctor is not available at this time"}), 400

        # Verifica se o paciente já tem um compromisso no horário solicitado (considerando 1 hora)
        cursor.execute("""
            SELECT 1
            FROM appointment a
            JOIN service_billing sb ON a.service_billing_id = sb.id
            WHERE sb.patient_person_id = %s
            AND (a.date_time < %s AND (a.date_time + interval '1 hour') > %s)
            FOR UPDATE
        """, (patient_id, appointment_end_time, appointment_time))
        patient_busy = cursor.fetchone()

        if patient_busy:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Patient already has an appointment at this time"}), 400

        # Cria um novo service_billing para o paciente
        cursor.execute(
            """
            INSERT INTO service_billing (patient_person_id)
            VALUES (%s)
            RETURNING id
            """,
            (patient_id,)
        )

        service_billing = cursor.fetchone()

        if not service_billing:
            conn.rollback()
            return jsonify({
                "status_code": StatusCodes['internal_error'],
                "errors": "Failed to create service_billing",
                "results": None
            }), 500

        service_billing_id = service_billing[0]

        # Insere um novo appointment
        cursor.execute(
            """
            INSERT INTO appointment (doctor_license_employee_contractdetails_person_id, date_time, service_billing_id)
            VALUES (%s, %s, %s)
            RETURNING service_billing_id
            """,
            (doctor_id, appointment_time, service_billing_id)
        )

        row = cursor.fetchone()

        if row is not None:
            service_billing_id = row[0]
            conn.commit()
            return jsonify({
                "status_code": StatusCodes['success'],
                "results": service_billing_id
            }), 200
        else:
            conn.rollback()
            return jsonify({
                "status_code": StatusCodes['internal_error'],
                "errors": "Failed to get service_billing_id",
                "results": None
            }), 500

    except Exception as e:
        print("Exception:", e)  # Adding a log for the exception
        conn.rollback()
        return jsonify({
            "status_code": StatusCodes['client_error'],
            "errors": "Dados Inválidos",
            "results": None
        }), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/dbproj/appointments/<int:patient_user_id>', methods=['GET'])
@jwt_required()
def get_appointments(patient_user_id):
    user_identity = get_jwt_identity()      # Obtém o username do usuário autenticado

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o usuário é um assistente
        cursor.execute("""
            SELECT ac.employee_contractdetails_person_id
            FROM assistant ac
            JOIN person p ON ac.employee_contractdetails_person_id = p.id
            WHERE p.username = %s
        """, (user_identity,))
        is_assistant = cursor.fetchone()

        # Verifica se o usuário é o próprio paciente
        cursor.execute("""
            SELECT p.id
            FROM person p
            JOIN patient pt ON p.id = pt.person_id
            WHERE p.username = %s
        """, (user_identity,))
        is_patient = cursor.fetchone()

        if not is_assistant and (not is_patient or is_patient[0] != patient_user_id):
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Unauthorized access"}), 403

        # Busca os appointments do paciente
        cursor.execute("""
            SELECT a.service_billing_id, a.date_time, a.doctor_license_employee_contractdetails_person_id, 
                   p.name as doctor_name
            FROM appointment a
            JOIN service_billing sb ON a.service_billing_id = sb.id
            JOIN patient pt ON sb.patient_person_id = pt.person_id
            JOIN doctor_license dl ON a.doctor_license_employee_contractdetails_person_id = dl.employee_contractdetails_person_id
            JOIN person p ON dl.employee_contractdetails_person_id = p.id
            WHERE pt.person_id = %s
        """, (patient_user_id,))

        appointments = cursor.fetchall()

        results = []
        for appointment in appointments:
            results.append({
                "id": appointment[0],
                "doctor_id": appointment[2],
                "date": appointment[1].strftime("%Y-%m-%d %H:%M:%S"),
                "doctor_name": appointment[3]
            })

        return jsonify({"status_code": StatusCodes['success'], "results": results}), 200

    except Exception as e:
        print("Exception:", e)  # Logging the exception
        return jsonify({"status_code": StatusCodes['internal_error'], "errors": str(e), "results": None}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/dbproj/surgery', methods=['POST'])
@app.route('/dbproj/surgery/<int:hospitalization_id>', methods=['POST'])
@jwt_required()
def schedule_surgery(hospitalization_id=None):
    user_identity = get_jwt_identity()
    user_username = user_identity  # Assuming that the user's identity is the username

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user is an assistant
        cursor.execute("""
            SELECT a.employee_contractdetails_person_id
            FROM assistant a
            JOIN person p ON a.employee_contractdetails_person_id = p.id
            WHERE p.username = %s
            FOR UPDATE
        """, (user_username,))
        assistant = cursor.fetchone()

        if not assistant:
            return jsonify({"status_code": StatusCodes['forbidden'], "errors": "Only assistants can access this endpoint"}), 403

        data = request.json
        patient_id = data['patient_id']
        doctor_id = data['doctor_id']
        nurses = data.get('nurses', [])
        date = data['date']

        if not patient_id or not doctor_id or not date or not nurses:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Patient ID, doctor ID, date and nurses are required"}), 400

        # Ensure nurses is a list and contains lists with nurse_id and role
        if not isinstance(nurses, list):
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "'nurses' must be a list"}), 400

        for nurse_info in nurses:
            if not isinstance(nurse_info, list) or len(nurse_info) != 2:
                return jsonify({"status_code": StatusCodes['client_error'], "errors": "Each nurse info must be a list with two elements: nurse_id and role"}), 400

        # Convert string date to datetime object
        date_object = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        surgery_end_time = date_object + timedelta(hours=8)

        # Check if the patient exists
        cursor.execute("SELECT person_id FROM patient WHERE person_id = %s FOR UPDATE", (patient_id,))
        if not cursor.fetchone():
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Patient ID not found"}), 400

        # Check if the doctor is available in appointments
        cursor.execute("""
            SELECT 1
            FROM appointment
            WHERE doctor_license_employee_contractdetails_person_id = %s
            AND (date_time < %s AND (date_time + interval '1 hour') > %s)
            FOR UPDATE
        """, (doctor_id, surgery_end_time, date_object))
        doctor_busy_appointment = cursor.fetchone()

        # Check if the doctor is available in surgeries
        cursor.execute("""
            SELECT 1
            FROM surgery
            WHERE doctor_license_employee_contractdetails_person_id = %s
            AND (date_time < %s AND date_time + interval '8 hour' > %s)
            FOR UPDATE
        """, (doctor_id, surgery_end_time, date_object))
        doctor_busy_surgery = cursor.fetchone()

        if doctor_busy_appointment or doctor_busy_surgery:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Doctor is not available at this time"}), 400

        # Check if the patient is available in appointments
        cursor.execute("""
            SELECT 1
            FROM appointment a
            JOIN service_billing sb ON a.service_billing_id = sb.id
            WHERE sb.patient_person_id = %s
            AND (a.date_time < %s AND (a.date_time + interval '1 hour') > %s)
            FOR UPDATE
        """, (patient_id, surgery_end_time, date_object))
        patient_busy_appointment = cursor.fetchone()

        # Check if the patient is available in surgeries
        cursor.execute("""
            SELECT 1
            FROM surgery s
            JOIN hospitalization h ON s.hospitalization_service_billing_id = h.service_billing_id
            JOIN service_billing sb ON h.service_billing_id = sb.id
            WHERE sb.patient_person_id = %s
            AND (s.date_time < %s AND s.date_time + interval '8 hour' > %s)
            FOR UPDATE
        """, (patient_id, surgery_end_time, date_object))
        patient_busy_surgery = cursor.fetchone()

        if patient_busy_appointment or patient_busy_surgery:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Patient already has an appointment or surgery at this time"}), 400

        # Check if each nurse is available
        for nurse_info in nurses:
            nurse_id = nurse_info[0]
            role = nurse_info[1]
            cursor.execute("""
                SELECT 1
                FROM rolenurse rn
                JOIN surgery s ON rn.surgery_id = s.id
                WHERE rn.nurse_employee_contractdetails_person_id = %s
                AND (s.date_time < %s AND s.date_time + interval '8 hour' > %s)
                FOR UPDATE
            """, (nurse_id, surgery_end_time, date_object))
            nurse_busy_surgery = cursor.fetchone()

            cursor.execute("""
                SELECT 1
                FROM hospitalization h
                WHERE nurse_employee_contractdetails_person_id = %s
                AND (h.date_start < %s AND h.date_end > %s)
                FOR UPDATE
            """, (nurse_id, surgery_end_time, date_object))
            nurse_busy_hospitalization = cursor.fetchone()

            if nurse_busy_surgery or nurse_busy_hospitalization:
                return jsonify({"status_code": StatusCodes['client_error'], "errors": f"Nurse {nurse_id} is not available at this time"}), 400

        # Check if the hospitalization exists if provided, otherwise create a new one
        if hospitalization_id:
            cursor.execute("SELECT service_billing_id FROM hospitalization WHERE service_billing_id = %s FOR UPDATE", (hospitalization_id,))
            if cursor.fetchone() is None:
                return jsonify({"status_code": StatusCodes['client_error'], "errors": "Hospitalization ID not found"}), 400
        else:
            # Create a new service_billing for the patient
            cursor.execute(
                """
                INSERT INTO service_billing (patient_person_id)
                VALUES (%s)
                RETURNING id
                """,
                (patient_id,)
            )

            service_billing = cursor.fetchone()

            if not service_billing:
                conn.rollback()
                return jsonify({
                    "status_code": StatusCodes['internal_error'],
                    "errors": "Failed to create service_billing",
                    "results": None
                }), 500

            # Create a new hospitalization for the patient
            cursor.execute(
                """
                INSERT INTO hospitalization (service_billing_id, date_start, date_end, nurse_employee_contractdetails_person_id)
                VALUES (%s, %s, %s, %s)
                RETURNING service_billing_id
                """,
                (service_billing[0], date_object, surgery_end_time, nurses[0][0])
            )

            hospitalization = cursor.fetchone()

            if not hospitalization:
                conn.rollback()
                return jsonify({
                    "status_code": StatusCodes['internal_error'],
                    "errors": "Failed to create hospitalization",
                    "results": None
                }), 500

        # Create a new surgery
        cursor.execute(
            """
            INSERT INTO surgery (date_time, doctor_license_employee_contractdetails_person_id, hospitalization_service_billing_id)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (date_object, doctor_id, hospitalization_id or hospitalization[0])
        )

        surgery_id = cursor.fetchone()[0]

        # Insert nurses into rolenurse
        for nurse_info in nurses:
            cursor.execute(
                """
                INSERT INTO rolenurse (role, nurse_employee_contractdetails_person_id, surgery_id)
                VALUES (%s, %s, %s)
                """,
                (nurse_info[1], nurse_info[0], surgery_id)
            )

        conn.commit()
        return jsonify({
            "status_code": StatusCodes['success'],
            "results": {
                "hospitalization_id": hospitalization_id or hospitalization[0],
                "surgery_id": surgery_id,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "date": date
            }
        }), 200

    except Exception as e:
        print(f"Exception: {e}")
        conn.rollback()
        return jsonify({
            "status_code": StatusCodes['internal_error'],
            "errors": "Dados Inválidos",
            "results": None
        }), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/dbproj/prescriptions/<int:patient_person_id>', methods=['GET'])
@jwt_required()
def get_prescriptions(patient_person_id):
    current_user = get_jwt_identity()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch patient details if the user is the patient
        cursor.execute("""
            SELECT p.id, p.name, p.date_birth, p.gender
            FROM person p
            JOIN patient pt ON p.id = pt.person_id
            WHERE pt.person_id = %s AND p.username = %s
        """, (patient_person_id, current_user,))
        patient_details = cursor.fetchone()

        # Always fetch patient details, even if the user is an employee
        cursor.execute("""
            SELECT p.id, p.name, p.date_birth, p.gender
            FROM person p
            JOIN patient pt ON p.id = pt.person_id
            WHERE pt.person_id = %s
        """, (patient_person_id,))
        patient_details = cursor.fetchone()

        if not patient_details:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Patient not found"}), 404

        # Verify if the user is an employee
        cursor.execute("""
            SELECT 1 FROM employee_contractdetails WHERE person_id = (SELECT id FROM person WHERE username = %s LIMIT 1)
        """, (current_user,))
        is_employee = cursor.fetchone() is not None

        # Fetch prescriptions for the patient
        cursor.execute("""
            SELECT pr.id, msm.medication_date_start, msm.medication_date_end, msm.id as medicine_id, e.name as medicine_name,
                msm.sideeffect_severity, msm.sideeffect_prob,
                msm.medication_date_start, msm.medication_date_end,
                msm.medication_interval, msm.medication_dosage
            FROM prescription pr
            JOIN medicine_sideeffect_medication msm ON pr.id = msm.prescription_id
            JOIN effect e ON msm.effect_id = e.id
            JOIN service_billing sb ON pr.service_billing_id = sb.id
            WHERE sb.patient_person_id = %s
        """, (patient_person_id,))

        prescriptions = cursor.fetchall()

        results = []

        # Append patient information first
        results.append({
            "patient": {
                "id": patient_person_id,
                "name": patient_details[1],
                "date_birth": patient_details[2].strftime("%Y-%m-%d"),
                "gender": "Male" if patient_details[3] else "Female"
            }
        })

        # Then append prescription information for each prescription
        for prescription in prescriptions:
            results.append({
                "id": prescription[0],
                "date_start": prescription[1].strftime("%Y-%m-%d"),
                "date_end": prescription[2].strftime("%Y-%m-%d"),
                "posology": {
                    "medicine_id": prescription[3],
                    "medicine_name": prescription[4],
                    "sideeffect_severity": prescription[5],
                    "sideeffect_prob": prescription[6],
                    "medication_date_start": prescription[7].strftime("%Y-%m-%d"),
                    "medication_date_end": prescription[8].strftime("%Y-%m-%d"),
                    "medication_interval": prescription[9],
                    "medication_dosage": prescription[10]
                }
            })

        return jsonify({"status_code": StatusCodes['success'], "results": results}), 200

    except Exception as e:
        print("Exception:", e)  # Logging the exception
        return jsonify({"status_code": StatusCodes['internal_error'], "errors": "Prescription Data Invalid"}), 500

    finally:
        cursor.close()
        conn.close()

def insert_prescription(cursor, event_id, medicines):
    try:
        # Inserir na tabela de prescrição
        cursor.execute("""
            INSERT INTO prescription (service_billing_id)
            VALUES (%s)
            RETURNING id
        """, (event_id,))
        prescription_id = cursor.fetchone()[0]

        # Chaves necessárias
        required_keys = [
            'sideeffect_severity',
            'sideeffect_prob',
            'medication_date_start',
            'medication_date_end',
            'medication_interval',
            'medication_dosage',
            'effect_id'
        ]

        for medicine in medicines:
            # Verificar se todas as chaves necessárias estão no dicionário de medicamentos
            if not all(key in medicine for key in required_keys):
                raise KeyError("Uma ou mais chaves necessárias estão faltando no dicionário de medicamentos")

            # Verificar se o effect_id existe na tabela effect
            cursor.execute("""
                SELECT id FROM effect WHERE id = %s
            """, (medicine['effect_id'],))
            effect = cursor.fetchone()

            if effect is None:
                # Adicionar o novo efeito se ele não existir
                cursor.execute("""
                    INSERT INTO effect (name) 
                    VALUES (%s)
                    RETURNING id
                """, (f"Efeito para id {medicine['effect_id']}",))
                medicine['effect_id'] = cursor.fetchone()[0]

            # Inserir na tabela medicine_sideeffect_medication
            cursor.execute("""
                INSERT INTO medicine_sideeffect_medication (
                    sideeffect_severity,
                    sideeffect_prob,
                    medication_date_start,
                    medication_date_end,
                    medication_interval,
                    medication_dosage,
                    effect_id,
                    prescription_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                medicine['sideeffect_severity'],
                medicine['sideeffect_prob'],
                medicine['medication_date_start'],
                medicine['medication_date_end'],
                medicine['medication_interval'],
                medicine['medication_dosage'],
                medicine['effect_id'],
                prescription_id
            ))

        return {"status_code": StatusCodes['success'], "results": {"prescription_id": prescription_id}}

    except Exception as e:
        return {"status_code": StatusCodes['internal_error'], "errors": "Dados Inválidos", "results": None}

    
@app.route('/dbproj/prescription/', methods=['POST'])
@jwt_required()
def create_prescription():
    current_user = get_jwt_identity()
    
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Verificar se o usuário atual é um médico
        cursor.execute("""
            SELECT p.id
            FROM person p
            JOIN doctor_license dl ON p.id = dl.employee_contractdetails_person_id
            WHERE p.username = %s
        """, (current_user,))
        doctor = cursor.fetchone()

        if not doctor:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Unauthorized access. Only doctors can create prescriptions."}), 403

        data = request.get_json()
        type_event = data.get('type')
        event_id = data.get('event_id')
        validity = data.get('validity')
        medicines = data.get('medicines')

        if not all([type_event, event_id, validity, medicines]):
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Missing required fields"}), 400

        # Validar tipo e ID do evento
        if type_event == "hospitalization":
            cursor.execute("SELECT service_billing_id FROM hospitalization WHERE service_billing_id = %s", (event_id,))
        elif type_event == "appointment":
            cursor.execute("SELECT service_billing_id FROM appointment WHERE service_billing_id = %s", (event_id,))
        else:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Invalid type"}), 400

        event = cursor.fetchone()
        if not event:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Event not found"}), 404

        # Inserir prescrição
        result = insert_prescription(cursor, event_id, medicines)
        if 'errors' in result and result['errors']:
            raise Exception(result['errors'])

        conn.commit()
        return jsonify(result), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"status_code": StatusCodes['internal_error'], "errors": "Dados Inválidos",  "results": None}), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/dbproj/bills/<int:bill_id>', methods=['POST'])
@jwt_required()
def make_payment(bill_id):
    service_billing_id = bill_id
    amount = request.json['amount']
    patient_username = get_jwt_identity()

    if not service_billing_id or not amount:
        return jsonify({ "status_code": StatusCodes['client_error'], "errors": "Service billing ID and amount are required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o paciente existe na tabela patient usando o username
        cursor.execute("""
            SELECT pt.person_id
            FROM patient pt
            JOIN person p ON pt.person_id = p.id
            WHERE p.username = %s
        """, (patient_username,))
        patient = cursor.fetchone()

        if not patient:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Patient username not found"}), 400

        patient_id = patient[0]

        # Verifica se o service_billing_id pertence ao paciente
        cursor.execute("""
            SELECT id
            FROM service_billing
            WHERE id = %s AND patient_person_id = %s
        """, (service_billing_id, patient_id))
        service_billing = cursor.fetchone()

        if not service_billing:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Service billing ID not found or does not belong to the patient"}), 400

        # Encontra todos os pagamentos associados ao service_billing_id, ordenados por id
        cursor.execute("""
            SELECT id, amount, amout_payed, ispaid
            FROM payment
            WHERE service_billing_id = %s
            ORDER BY id
            FOR UPDATE
        """, (service_billing_id,))
        payments = cursor.fetchall()

        if not payments:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Payment record not found for the given service billing ID"}), 400

        remaining_amount = amount

        for payment_id, current_amount, amount_paid, ispaid in payments:
            if ispaid and current_amount == amount_paid:
                continue  # Se o pagamento está completo, passa para o próximo

            if not ispaid:
                new_amount_paid = amount_paid + remaining_amount
                if new_amount_paid >= current_amount:
                    remaining_amount = new_amount_paid - current_amount
                    cursor.execute("""
                        UPDATE payment
                        SET amout_payed = %s, ispaid = %s, time_payed = NOW()
                        WHERE id = %s
                    """, (current_amount, True, payment_id))
                else:
                    cursor.execute("""
                        UPDATE payment
                        SET amout_payed = %s, ispaid = %s, time_payed = NOW()
                        WHERE id = %s
                    """, (new_amount_paid, True, payment_id))
                    remaining_amount = current_amount - new_amount_paid
                    break

        if remaining_amount > 0:
            # Cria um novo pagamento para o valor restante
            cursor.execute("""
                INSERT INTO payment (amount, amout_payed, ispaid, time_payed, service_billing_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (remaining_amount, 0.0, False, None, service_billing_id))
            
            new_payment_id = cursor.fetchone()[0]

            conn.commit()
            return jsonify({
                "status_code": StatusCodes['success'],
                "results": {
                    "message": "Partial payment received. New payment created for the remaining amount.",
                    "remaining_payment_id": new_payment_id
                }
            }), 200
        else:
            conn.commit()
            return jsonify({
                "status_code": StatusCodes['success'],
                "results": {
                    "message": "Payment completed"
                }
            }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({
            "status_code": StatusCodes['internal_error'],
            "errors": "Dados Inválidos",
            "results": None
        }), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/dbproj/top3', methods=['GET'])
@jwt_required()
def get_top_patients():
    assistant_username = get_jwt_identity()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o usuário é um assistente
        cursor.execute("""
            SELECT a.employee_contractdetails_person_id
            FROM assistant a
            JOIN employee_contractdetails ecd ON a.employee_contractdetails_person_id = ecd.person_id
            JOIN person p ON ecd.person_id = p.id
            WHERE p.username = %s
        """, (assistant_username,))
        assistant = cursor.fetchone()

        if not assistant:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Apenas assistentes podem usar este endpoint"}), 400

        # Obtém os 3 principais pacientes pelo dinheiro gasto no mês atual
        cursor.execute("""
            SELECT
                p.name AS nome_paciente,
                SUM(py.amout_payed) AS total_gasto,
                json_agg(
                    json_build_object(
                        'service_billing_id', sb.id,
                        'appointment_date_time', a.date_time,
                        'appointment_cost', a.cost,
                        'hospitalization_date_start', h.date_start,
                        'hospitalization_date_end', h.date_end,
                        'hospitalization_cost', h.cost,
                        'surgery_date_time', s.date_time,
                        'surgery_cost', s.cost
                    )
                ) AS service_billing_details
            FROM person p
            JOIN service_billing sb ON p.id = sb.patient_person_id
            LEFT JOIN appointment a ON sb.id = a.service_billing_id
            LEFT JOIN hospitalization h ON sb.id = h.service_billing_id
            LEFT JOIN surgery s ON h.service_billing_id = s.hospitalization_service_billing_id
            LEFT JOIN payment py ON sb.id = py.service_billing_id
            GROUP BY p.name
            ORDER BY total_gasto DESC
            LIMIT 3;
        """)
        top_patients = cursor.fetchall()

        results = []
        for patient in top_patients:
            results.append({
                "nome_paciente": patient[0],
                "total_gasto": patient[1],
                "service_billing_details": patient[2]
            })

        return jsonify({
            "status_code": StatusCodes['success'],
            "results": results
        }), 200

    except Exception as e:
        return jsonify({
            "status_code": StatusCodes['internal_error'],
            "errors": str(e),
            "results": None
        }), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/dbproj/daily/<date>', methods=['GET'])
@jwt_required()
def get_daily_summary(date):
    assistant_username = get_jwt_identity()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify if the user is an assistant
        cursor.execute("""
            SELECT a.employee_contractdetails_person_id
            FROM assistant a
            JOIN employee_contractdetails ecd ON a.employee_contractdetails_person_id = ecd.person_id
            JOIN person p ON ecd.person_id = p.id
            WHERE p.username = %s
        """, (assistant_username,))
        assistant = cursor.fetchone()

        if not assistant:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Only assistants can use this endpoint"}), 400

        # Get the daily summary for the given date
        cursor.execute("""
            SELECT
                COALESCE(SUM(py.amout_payed), 0) AS amount_spent,
                COALESCE(COUNT(DISTINCT sr.id), 0) AS surgeries,
                COALESCE(COUNT(DISTINCT pr.id), 0) AS prescriptions
            FROM 
                hospitalization h
            LEFT JOIN surgery sr ON h.service_billing_id = sr.hospitalization_service_billing_id
            LEFT JOIN prescription pr ON h.service_billing_id = pr.service_billing_id
            LEFT JOIN payment py ON h.service_billing_id = py.service_billing_id
            WHERE 
                DATE(h.date_start) = %s
                OR DATE(h.date_end) = %s
                OR DATE(sr.date_time) = %s
                OR DATE(py.time_payed) = %s
        """, (date, date, date, date))
        daily_summary = cursor.fetchone()

        results = {
            "amount_spent": daily_summary[0],
            "surgeries": daily_summary[1],
            "prescriptions": daily_summary[2]
        }

        return jsonify({
            "status_code": StatusCodes['success'],
            "results": results
        }), 200

    except Exception as e:
        return jsonify({
            "status_code": StatusCodes['internal_error'],
            "errors": str(e),
            "results": None
        }), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/dbproj/report', methods=['GET'])
@jwt_required()
def get_monthly_report():
    assistant_username = get_jwt_identity()

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verifica se o usuário é um assistente
        cursor.execute("""
            SELECT a.employee_contractdetails_person_id
            FROM assistant a
            JOIN employee_contractdetails ecd ON a.employee_contractdetails_person_id = ecd.person_id
            JOIN person p ON ecd.person_id = p.id
            WHERE p.username = %s
        """, (assistant_username,))
        assistant = cursor.fetchone()

        if not assistant:
            return jsonify({"status_code": StatusCodes['client_error'], "errors": "Only assistants can use this endpoint"}), 400

        # Consulta para obter o relatório dos últimos 12 meses
        cursor.execute("""
            WITH monthly_surgeries AS (
                SELECT 
                    TO_CHAR(DATE_TRUNC('month', s.date_time), 'YYYY-MM') AS month,
                    p.name AS doctor,
                    COUNT(s.id) AS total_surgeries,
                    ROW_NUMBER() OVER (PARTITION BY TO_CHAR(DATE_TRUNC('month', s.date_time), 'YYYY-MM') ORDER BY COUNT(s.id) DESC) AS rank
                FROM 
                    surgery s
                JOIN 
                    doctor_license dl ON s.doctor_license_employee_contractdetails_person_id = dl.employee_contractdetails_person_id
                JOIN 
                    person p ON dl.employee_contractdetails_person_id = p.id
                WHERE 
                    s.date_time >= NOW() - INTERVAL '12 months'
                GROUP BY 
                    month, doctor
            )
            SELECT month, doctor, total_surgeries
            FROM monthly_surgeries
            WHERE rank = 1;
        """)

        report_data = cursor.fetchall()

        # Processa os dados para gerar o relatório
        report = [{"month": row[0], "doctor": row[1], "surgeries": row[2]} for row in report_data]

        return jsonify({
            "status_code": StatusCodes['success'],
            "results": report
        }), 200

    except Exception as e:
        return jsonify({
            "status_code": StatusCodes['internal_error'],
            "errors": str(e),
            "results": None
        }), 500

    finally:
        cursor.close()
        conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    try:
        response = make_response(jsonify({"status_code": StatusCodes['success'], "message": "Cookies cleared"}))
        
        # Clear the cookies by setting their values to empty strings and expiry date to a past date
        for cookie in request.cookies:
            response.set_cookie(cookie, '', expires=0)
        
        return response
    except Exception as e:
        return jsonify({
            "status_code": StatusCodes['internal_error'],
            "errors": str(e),
            "message": "Failed to clear cookies"
        }), 500

if __name__ == '__main__':

    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')