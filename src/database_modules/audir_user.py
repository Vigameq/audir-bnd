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

def list_users(data, environment):
    query = f"""
                SELECT first_name, last_name, email, organisation, role, department, location, is_admin
                FROM audir_users
                WHERE organisation = (
                    SELECT organisation
                    FROM audir_users
                    WHERE email = '{data.get("eMail").lower()}'
                    LIMIT 1
                );
                """
    query_data, status = db_connector.read_all_query(query, environment)
    if status == 200:
        columns = ['first_name', 'last_name', 'email', 'organisation', 'role', 'department', 'location', 'is_admin']
        users = [dict(zip(columns, row)) for row in query_data]
        return sorted(users, key=lambda x: (x['first_name'], x['last_name'], x['email']))
    return "Issue fetching Users"


def update_user(data, environment):
    email = (data.get('email') or data.get('eMail') or '').lower()
    if not email:
        return {'message': 'Email is required'}, 400
    fields = []
    if data.get('firstName') is not None:
        fields.append(f"first_name='{data.get('firstName')}'")
    if data.get('lastName') is not None:
        fields.append(f"last_name='{data.get('lastName')}'")
    if data.get('role') is not None:
        fields.append(f"role='{data.get('role')}'")
    if data.get('department') is not None:
        fields.append(f"department='{data.get('department')}'")
    if data.get('location') is not None:
        fields.append(f"location='{data.get('location')}'")
    if not fields:
        return {'message': 'No fields to update'}, 400
    requester = (data.get('requester_email') or '').lower()
    org_filter = ''
    if requester:
        org_filter = f" AND organisation = (SELECT organisation FROM audir_users WHERE email = '{requester}' LIMIT 1)"
    query = f"""
            UPDATE audir_users
            SET {', '.join(fields)}
            WHERE email = '{email}'{org_filter};
        """
    message, status = db_connector.write_query(query, environment)
    if status == 200:
        return {'message': 'User Updated Successfully'}, status
    return {'message': message}, 409


def update_password(data, environment):
    email = (data.get('email') or data.get('eMail') or '').lower()
    if not email:
        return {'message': 'Email is required'}, 400
    new_password = data.get('password')
    if not new_password:
        return {'message': 'Password is required'}, 400
    old_password = data.get('oldPassword')
    if old_password:
        query = f"""
                SELECT password FROM audir_users
                WHERE email = '{email}'
                """
        query_data, status = db_connector.read_one_query(query, environment)
        if status != 200 or query_data is None:
            return {'message': 'User not found'}, 400
        stored_password = query_data[0]
        if not check_password_hash(stored_password, old_password):
            return {'message': 'Old password mismatch'}, 400
    update_query = f"""
            UPDATE audir_users
            SET password = '{generate_password_hash(new_password.strip())}'
            WHERE email = '{email}';
        """
    message, status = db_connector.write_query(update_query, environment)
    if status == 200:
        return {'message': 'Password Updated Successfully'}, status
    return {'message': message}, 409


def delete_user(data, environment):
    email = (data.get('email') or data.get('eMail') or '').lower()
    if not email:
        return {'message': 'Email is required'}, 400
    requester = (data.get('requester_email') or '').lower()
    org_filter = ''
    if requester:
        org_filter = f" AND organisation = (SELECT organisation FROM audir_users WHERE email = '{requester}' LIMIT 1)"
    query = f"""
            DELETE FROM audir_users
            WHERE email = '{email}'{org_filter};
        """
    message, status = db_connector.write_query(query, environment)
    if status == 200:
        return {'message': 'User Deleted Successfully'}, status
    return {'message': message}, 409
