from src.database_modules import audir_user, audir_template, audir_audit


def get_planning_items(data, environment):
    try:
        user_data = audir_user.list_auditors_auditees(data,environment)
        template_data = audir_template.list_templates(data, environment)
        parent_audit_data = audir_audit.list_parent_audits(data, environment)

        return {"users": user_data, "templates": template_data, "parent_audits": parent_audit_data}, 200
    except Exception as e:
        return {'message': str(e)}, 409

def validate_audit_plan(audit_plan_data, environment, data):
    try:
        user_data = audir_user.list_auditors_auditees(data, environment)
        auditees = [user['email'] for user in user_data['auditees']]
        auditors = [user['email'] for user in user_data['auditors']]


        template_data = audir_template.list_templates(data, environment)
        template_name = [template['name'] for template in template_data]

        parent_audit_data = audir_audit.list_parent_audits(data, environment)
        parent_audit_title = [parent_audit['title'] for parent_audit in parent_audit_data]
        new_parent = [parent['AuditTitle'] for parent in audit_plan_data]
        parent_audit_title.extend(new_parent)

        detailed_failure_report = {}
        for row in audit_plan_data:
            row_data = []
            if row['LinkAudit'] != None and row['LinkAudit'] not in parent_audit_title:
                row_data.append("Invalid Parent Audit")

            if row['Template'] not in template_name:
                row_data.append("Invalid Template")

            if row['FunctionTemplate'] not in template_name:
                row_data.append("Invalid FunctionTemplate")

            if audir_audit.check_duplicate_audit(row['AuditTitle'], environment):
                row_data.append("Duplicate AuditTitle")

            uploaded_auditors = [auditor.strip() for auditor in row['Auditors'].split(',')]
            if not all(element in auditors for element in uploaded_auditors):
                row_data.append("Invalid Auditors")

            uploaded_auditees = [auditee.strip() for auditee in row['Auditees'].split(',')]
            if not all(element in auditees for element in uploaded_auditees):
                row_data.append("Invalid Auditees")

            if len(row_data) != 0:
                detailed_failure_report[row['AuditTitle']] = row_data

        if len(detailed_failure_report) == 0:
            response_data = {"status": "success"}
        else:
            response_data = {"status": "failure", "details": detailed_failure_report}

        return response_data, 200
    except Exception as e:
        return {'message': str(e)}, 409
