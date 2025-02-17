from werkzeug.security import generate_password_hash, check_password_hash
from src.helpers import db_connector
import pandas as pd
import json

def create_template(data, environment):

    query = f"""
            INSERT INTO audir_templates 
            (template_file, email,  audit_type, questions)
            VALUES 
            ('{data.get("uploadTemplate")}', '{data.get("eMail")}', '{data.get("type")}', '{json.dumps(data.get("questions"))}');
        """

    result, status = db_connector.write_query(query, environment)

    if status == 200:
        return {'message': "Template Added Successfully"}, status
    else:
        return {'message': result}, 409

def read_questions(file_path):
    try:
        df = pd.read_excel(file_path)

        questions = df['Questions'].dropna().tolist()

        return questions, 200
    except Exception as e:
        return str(e), 400


def list_templates(data, environment):
    query = f"""
                SELECT t.id, t.audit_type, t.email
                FROM audir_templates t
                JOIN "audir_users" u ON t.email = u.email
                WHERE u.organisation = (
                    SELECT organisation
                    FROM "audir_users"
                    WHERE email = '{data.get("eMail").lower()}'
                    LIMIT 1
                );
                """
    query_data, status = db_connector.read_all_query(query, environment)
    if status == 200:

        columns = ['id', 'name', 'email']
        templates = [dict(zip(columns, row)) for row in query_data]

        grouped_data = []
        for template in templates:
            grouped_data.append(
            {"id": template['id'], "name": template['name'], "email": template['email']})

        sorted_grouped_data = sorted(grouped_data, key=lambda x: x["name"])
        return sorted_grouped_data
    else:
        return "Issue fetching Templates"
