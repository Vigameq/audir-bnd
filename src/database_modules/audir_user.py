from werkzeug.security import generate_password_hash, check_password_hash

from src.helpers import db_connector

def create(data, environment):

    query = f"""
            INSERT INTO audir_users 
            (first_name, last_name,  email, password, 
             organisation, role, department, location, 
             user_pic)
            VALUES 
            ('{data.get("firstName")}', '{data.get("lastName")}', '{data.get("eMail").lower()}', '{generate_password_hash(data.get("password").strip())}',
            '{data.get("organisation")}', '{data.get("role")}',  '{data.get("department")}', '{data.get("location")}', 
            '{data.get("user_pic")}');
        """

    message, status = db_connector.write_query(query,environment)
    if status == 200:
        return {'message': "User Created Successfully!!"}, status
    else:
        if "email" in message:
            msg = 'User Email Address Already Exists'
        else:
            msg = message
        return {'message': msg}, 409


def authenticate(data,environment):
    query = f"""
            SELECT first_name, last_name, organisation, role, department, password, is_admin, user_pic from audir_users
            where email='{data.get("eMail").lower()}'
            """
    query_data, status = db_connector.read_one_query(query, environment)
    if status == 200:
        if query_data is not None:
            first_name, last_name, organisation, role, department, password, is_admin, user_pic = query_data
            if check_password_hash(password, data.get("password")):
                return {
                    "eMail": data.get("eMail"),
                    "firstname": first_name,
                    "lastName": last_name,
                    "organisation": organisation,
                    "role": role,
                    "department": department,
                    "isAdmin": is_admin,
                    "userProfileImage" : user_pic
                    }, 200
            else:
                return {"message": "Invalid Email or Password"}, 400
        else:
            return {"message": "User Not Registered"}, 400
    else:
        return query_data, status


def list_auditors_auditees(data, environment):
    query = f"""
                SELECT first_name, last_name, email, organisation, role, department
                FROM audir_users
                WHERE role in ('Auditee','Auditor') and organisation = (
                    SELECT organisation
                    FROM audir_users
                    WHERE email = '{data.get("eMail").lower()}'
                    LIMIT 1
                );
                """
    query_data, status = db_connector.read_all_query(query, environment)
    if status == 200:

        columns = ['first_name', 'last_name', 'email', 'organisation', 'role', 'department']
        users = [dict(zip(columns, row)) for row in query_data]

        grouped_data = {"auditors": [], "auditees": []}
        for user in users:
            role = user['role'].lower()  # Convert role to lowercase to match "auditors" and "auditees"

            if role == "auditor":
                grouped_data["auditors"].append(
                    {"Name": f"{user['first_name']} {user['last_name']}", "email": user['email'], "department": user['department'], "organisation": user['organisation']})
            elif role == "auditee":
                grouped_data["auditees"].append(
                    {"Name": f"{user['first_name']} {user['last_name']}", "email": user['email'], "department": user['department'], "organisation": user['organisation']})

        sorted_grouped_data = {"auditors": sorted(grouped_data["auditors"], key=lambda x: x["Name"]), "auditees": sorted(grouped_data["auditees"], key=lambda x: x["Name"])}
        return sorted_grouped_data
    else:
        return "Issue fetching Users"