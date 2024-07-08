CREATE TABLE appointment (
	cost						 FLOAT(8) NOT NULL DEFAULT 50,
	date_time					 TIMESTAMP NOT NULL,
	doctor_license_employee_contractdetails_person_id INTEGER NOT NULL,
	service_billing_id				 INTEGER,
	PRIMARY KEY(service_billing_id)
);

CREATE TABLE hospitalization (
	cost					 FLOAT(8) NOT NULL DEFAULT 100,
	date_start				 TIMESTAMP NOT NULL,
	date_end				 TIMESTAMP NOT NULL,
	nurse_employee_contractdetails_person_id INTEGER NOT NULL,
	service_billing_id			 INTEGER,
	PRIMARY KEY(service_billing_id)
);

CREATE TABLE surgery (
	id						 SERIAL,
	cost						 FLOAT(8) NOT NULL DEFAULT 200,
	date_time					 TIMESTAMP NOT NULL,
	hospitalization_service_billing_id		 INTEGER NOT NULL,
	doctor_license_employee_contractdetails_person_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE employee_contractdetails (
	contractdetails_salary	 FLOAT(8) NOT NULL,
	contractdetails_date_start TIMESTAMP NOT NULL,
	contractdetails_date_end	 TIMESTAMP NOT NULL,
	person_id			 INTEGER,
	PRIMARY KEY(person_id)
);

CREATE TABLE assistant (
	employee_contractdetails_person_id INTEGER,
	PRIMARY KEY(employee_contractdetails_person_id)
);

CREATE TABLE doctor_license (
	license_details			 TEXT NOT NULL,
	employee_contractdetails_person_id INTEGER,
	PRIMARY KEY(employee_contractdetails_person_id)
);

CREATE TABLE nurse (
	nurse_employee_contractdetails_person_id INTEGER NOT NULL,
	employee_contractdetails_person_id	 INTEGER,
	PRIMARY KEY(employee_contractdetails_person_id)
);

CREATE TABLE patient (
	person_id INTEGER,
	PRIMARY KEY(person_id)
);

CREATE TABLE rolenurse (
	role					 TEXT,
	nurse_employee_contractdetails_person_id INTEGER,
	surgery_id				 INTEGER,
	PRIMARY KEY(nurse_employee_contractdetails_person_id,surgery_id)
);

CREATE TABLE prescription (
	id		 SERIAL,
	service_billing_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE medicine_sideeffect_medication (
	id			 SERIAL,
	sideeffect_severity	 FLOAT(8) NOT NULL,
	sideeffect_prob	 FLOAT(8) NOT NULL,
	medication_date_start TIMESTAMP NOT NULL,
	medication_date_end	 TIMESTAMP NOT NULL,
	medication_interval	 TIMESTAMP NOT NULL,
	medication_dosage	 FLOAT(8) NOT NULL,
	effect_id		 INTEGER NOT NULL,
	prescription_id	 INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE effect (
	id	 SERIAL,
	name VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE payment (
	id		 SERIAL,
	amount		 FLOAT(8) NOT NULL,
	ispaid		 BOOL NOT NULL DEFAULT false,
	amout_payed	 FLOAT(8) NOT NULL,
	time_payed	 TIMESTAMP,
	service_billing_id INTEGER,
	PRIMARY KEY(id,service_billing_id)
);

CREATE TABLE specialization (
	id		 SERIAL,
	specialization	 VARCHAR(512),
	specialization_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE service_billing (
	id		 SERIAL,
	patient_person_id INTEGER NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE person (
	id	 SERIAL,
	name	 VARCHAR(512) NOT NULL,
	gender	 BOOL NOT NULL,
	date_birth DATE,
	username	 VARCHAR(512),
	password	 VARCHAR(512),
	PRIMARY KEY(id)
);

CREATE TABLE specialization_doctor_license (
	specialization_id				 INTEGER,
	doctor_license_employee_contractdetails_person_id INTEGER,
	PRIMARY KEY(specialization_id,doctor_license_employee_contractdetails_person_id)
);

ALTER TABLE appointment ADD CONSTRAINT appointment_fk1 FOREIGN KEY (doctor_license_employee_contractdetails_person_id) REFERENCES doctor_license(employee_contractdetails_person_id);
ALTER TABLE appointment ADD CONSTRAINT appointment_fk2 FOREIGN KEY (service_billing_id) REFERENCES service_billing(id);
ALTER TABLE appointment ADD CONSTRAINT costConstraint CHECK (cost > 0);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk1 FOREIGN KEY (nurse_employee_contractdetails_person_id) REFERENCES nurse(employee_contractdetails_person_id);
ALTER TABLE hospitalization ADD CONSTRAINT hospitalization_fk2 FOREIGN KEY (service_billing_id) REFERENCES service_billing(id);
ALTER TABLE hospitalization ADD CONSTRAINT costConstraint CHECK (cost > 0);
ALTER TABLE hospitalization ADD CONSTRAINT constraint_1 CHECK (date_end > date_start);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk1 FOREIGN KEY (hospitalization_service_billing_id) REFERENCES hospitalization(service_billing_id);
ALTER TABLE surgery ADD CONSTRAINT surgery_fk2 FOREIGN KEY (doctor_license_employee_contractdetails_person_id) REFERENCES doctor_license(employee_contractdetails_person_id);
ALTER TABLE surgery ADD CONSTRAINT constraint_0 CHECK (cost > 0);
ALTER TABLE employee_contractdetails ADD CONSTRAINT employee_contractdetails_fk1 FOREIGN KEY (person_id) REFERENCES person(id);
ALTER TABLE assistant ADD CONSTRAINT assistant_fk1 FOREIGN KEY (employee_contractdetails_person_id) REFERENCES employee_contractdetails(person_id);
ALTER TABLE doctor_license ADD CONSTRAINT doctor_license_fk1 FOREIGN KEY (employee_contractdetails_person_id) REFERENCES employee_contractdetails(person_id);
ALTER TABLE nurse ADD UNIQUE (nurse_employee_contractdetails_person_id);
ALTER TABLE nurse ADD CONSTRAINT nurse_fk1 FOREIGN KEY (nurse_employee_contractdetails_person_id) REFERENCES nurse(employee_contractdetails_person_id);
ALTER TABLE nurse ADD CONSTRAINT nurse_fk2 FOREIGN KEY (employee_contractdetails_person_id) REFERENCES employee_contractdetails(person_id);
ALTER TABLE patient ADD CONSTRAINT patient_fk1 FOREIGN KEY (person_id) REFERENCES person(id);
ALTER TABLE rolenurse ADD CONSTRAINT rolenurse_fk1 FOREIGN KEY (nurse_employee_contractdetails_person_id) REFERENCES nurse(employee_contractdetails_person_id);
ALTER TABLE rolenurse ADD CONSTRAINT rolenurse_fk2 FOREIGN KEY (surgery_id) REFERENCES surgery(id);
ALTER TABLE prescription ADD CONSTRAINT prescription_fk1 FOREIGN KEY (service_billing_id) REFERENCES service_billing(id);
ALTER TABLE medicine_sideeffect_medication ADD CONSTRAINT medicine_sideeffect_medication_fk1 FOREIGN KEY (effect_id) REFERENCES effect(id);
ALTER TABLE medicine_sideeffect_medication ADD CONSTRAINT medicine_sideeffect_medication_fk2 FOREIGN KEY (prescription_id) REFERENCES prescription(id);
ALTER TABLE payment ADD CONSTRAINT payment_fk1 FOREIGN KEY (service_billing_id) REFERENCES service_billing(id);
ALTER TABLE payment ADD CONSTRAINT constraint_0 CHECK (amount > 0);
ALTER TABLE specialization ADD CONSTRAINT specialization_fk1 FOREIGN KEY (specialization_id) REFERENCES specialization(id);
ALTER TABLE specialization ADD CONSTRAINT id_constraint CHECK (id > 0);
ALTER TABLE service_billing ADD CONSTRAINT service_billing_fk1 FOREIGN KEY (patient_person_id) REFERENCES patient(person_id);
ALTER TABLE specialization_doctor_license ADD CONSTRAINT specialization_doctor_license_fk1 FOREIGN KEY (specialization_id) REFERENCES specialization(id);
ALTER TABLE specialization_doctor_license ADD CONSTRAINT specialization_doctor_license_fk2 FOREIGN KEY (doctor_license_employee_contractdetails_person_id) REFERENCES doctor_license(employee_contractdetails_person_id);

