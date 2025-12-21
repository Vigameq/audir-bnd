import os
import time
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file

from src.helpers import load_env
from werkzeug.utils import secure_filename
from src.database_modules import audir_user, audir_template, audir_plan, audir_audit

import io
import pandas as pd

app = Flask(__name__)
cors = CORS(app)

DEFAULT_ENVIRONMENT = "development"


@app.route("/audire/api/createUser", methods=['POST'])
def create_user():
    try:
        if 'userProfileImage' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['userProfileImage']
        filename = secure_filename(file.filename)
        upload_folder = load_env.folder_env()['profile_pic']
        os.makedirs(upload_folder, exist_ok=True)
        new_filename = str(int(time.time()))+"_"+filename
        filepath = os.path.join(upload_folder, new_filename)
        file.save(filepath)

        user_data = request.form.to_dict()
        user_data['user_pic'] = new_filename
        environment = user_data.get('environment', DEFAULT_ENVIRONMENT)

        create_response, status_code = audir_user.create(user_data,environment)

        return create_response, status_code

    except Exception as e:
        return {"error": str(e)}, 400


@app.route("/audire/api/userLogin", methods=['POST'])
def user_login():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        login_response, status_code = audir_user.authenticate(data, environment)
        return login_response,status_code
    except Exception as e:
        return {"error": str(e)}, 400

@app.route('/audire/api/profilePic/<string:image_id>', methods=['GET'])
def get_image(image_id):
    upload_folder = load_env.folder_env()['profile_pic']
    filepath = os.path.join(upload_folder, image_id)
    if not os.path.exists(filepath):
        return {"error": "Image Not Found"}, 400
    return send_file(filepath, mimetype='image/jpeg')

@app.route('/audire/api/downloadAuditTemplate', methods=['Get'])
def download_audit_template():
    standard_audit_template_path = load_env.folder_env()['standard_audit_template_path']
    return send_file(standard_audit_template_path, mimetype='application/vnd.ms-excel')

@app.route('/audire/api/downloadAuditPlan', methods=['Get'])
def download_audit_plan():
    standard_audit_plan_path = load_env.folder_env()['standard_audit_plan_path']
    return send_file(standard_audit_plan_path, mimetype='application/vnd.ms-excel')

@app.route('/audire/api/uploadTemplate', methods=['POST'])
def upload_template():
    try:
        if 'uploadTemplate' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['uploadTemplate']
        filename = secure_filename(file.filename)
        upload_folder = load_env.folder_env()['uploaded_template_path']
        os.makedirs(upload_folder, exist_ok=True)
        new_filename = str(int(time.time()))+"_"+filename
        filepath = os.path.join(upload_folder, new_filename)
        file.save(filepath)

        upload_data = request.form.to_dict()
        upload_data['uploadTemplate'] = new_filename
        questions, status = audir_template.read_questions(filepath)
        if status !=200 or len(questions)==0:
            return {"error": "Issue with Uploaded Template, Please check the uploaded Template"}, 400
        upload_data['questions'] = questions
        environment = upload_data.get('environment', DEFAULT_ENVIRONMENT)

        create_response, status_code = audir_template.create_template(upload_data,environment)

        return create_response, status_code

    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/updateTemplateQuestions", methods=['POST'])
def update_template_questions():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        update_response, status_code = audir_template.update_template_questions(data, environment)
        return update_response, status_code
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/listUsers", methods=['POST'])
def list_users():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        users_response = audir_user.list_users(data, environment)
        return users_response, 200
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/updateUser", methods=['POST'])
def update_user():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        update_response, status_code = audir_user.update_user(data, environment)
        return update_response, status_code
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/updatePassword", methods=['POST'])
def update_password():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        update_response, status_code = audir_user.update_password(data, environment)
        return update_response, status_code
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/deleteUser", methods=['POST'])
def delete_user():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        delete_response, status_code = audir_user.delete_user(data, environment)
        return delete_response, status_code
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/planItems", methods=['POST'])
def plan_items():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        plan_response, status_code = audir_plan.get_planning_items(data, environment)
        return plan_response,status_code
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/planAudit", methods=['POST'])
def plan_audit():
    data = request.json
    environment = data.get('environment', DEFAULT_ENVIRONMENT)
    try:
        plan_response, status_code = audir_audit.create_audit(data, environment)
        return plan_response,status_code
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/validateAuditPlan", methods=['POST'])
def validate_audit_plan():
    try:
        if 'uploadAuditPlan' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['uploadAuditPlan']
        audit_plan_excel_data = file.read()  # Read file as bytes
        audit_plan_df = pd.read_excel(io.BytesIO(audit_plan_excel_data))
        audit_plan_df = audit_plan_df.map(lambda x: None if pd.isna(x) else x)
        audit_plan_data = audit_plan_df.head().to_dict(orient='records')
        if len(audit_plan_data) == 0:
            return {"error": "Issue with Uploaded Audit Plan, Please validate uploaded Audit Plan is not blank"}, 400

        upload_data = request.form.to_dict()
        environment = upload_data.get('environment', DEFAULT_ENVIRONMENT)
        data = {'eMail': upload_data.get('eMail')}

        validation_response, status_code = audir_plan.validate_audit_plan(audit_plan_data, environment, data)

        return validation_response, status_code

    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/audire/api/bulkAuditCreate", methods=['POST'])
def bulk_audit_create():
    try:
        if 'uploadAuditPlan' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['uploadAuditPlan']
        audit_plan_excel_data = file.read()  # Read file as bytes
        audit_plan_df = pd.read_excel(io.BytesIO(audit_plan_excel_data))
        audit_plan_df = audit_plan_df.map(lambda x: None if pd.isna(x) else x)
        audit_plan_data = audit_plan_df.head().to_dict(orient='records')
        if len(audit_plan_data) == 0:
            return {"error": "Issue with Uploaded Audit Plan, Please validate uploaded Audit Plan is not blank"}, 400

        upload_data = request.form.to_dict()
        environment = upload_data.get('environment', DEFAULT_ENVIRONMENT)
        email = upload_data.get('eMail')

        bulk_creation_response, status_code = audir_audit.create_audit_bulk(audit_plan_data, email, environment)

        return bulk_creation_response, status_code

    except Exception as e:
        return {"error": str(e)}, 400


if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run()