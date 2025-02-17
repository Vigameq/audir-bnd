from src.helpers import db_connector


def create_audit(data, environment):

    query = f"""
        INSERT INTO audir_audit (
            link_audit,
            audit_title,
            functions,
            template,
            function_template,
            start_date,
            end_date,
            auditors,
            auditees,
            city,
            country,
            audit_scope,
            audit_type,
            email
        )
        VALUES ( 
             '{data.get("link_audit")}',
             '{data.get("audit_title")}',
             '{data.get("functions")}',
             '{data.get("template")}',
             '{data.get("function_template")}',
             '{data.get("start_date")}',
             '{data.get("end_date")}',
             '{",".join([auditor.lower() for auditor in data.get("auditors")])}',
             '{", ".join([auditee.lower() for auditee in data.get("auditees")])}',
             '{data.get("city")}',
             '{data.get("country")}',
             '{data.get("audit_scope")}',
             '{data.get("audit_type")}',
             '{data.get("eMail").lower()}'
        );
        """

    result, status = db_connector.write_query(query, environment)

    if status == 200:
        return {'message': "Audit Planned Successfully"}, status
    else:
        return {'message': result}, 409

def create_audit_bulk(bulk_data, email, environment):

    query = f"""
        INSERT INTO audir_audit (
            link_audit,
            audit_title,
            functions,
            template,
            function_template,
            start_date,
            end_date,
            auditors,
            auditees,
            city,
            country,
            audit_scope,
            audit_type,
            email
        )
        VALUES ( 
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s,
             %s
        );
        """

    params = [(str(data.get("LinkAudit")),
             data.get("AuditTitle"),
             data.get("Functions"),
             data.get("Template"),
             data.get("FunctionTemplate"),
             data.get("StartDate"),
             data.get("EndDate"),
             data.get("Auditors").lower(),
             data.get("Auditees").lower(),
             data.get("City"),
             data.get("Country"),
             data.get("AuditScope"),
             data.get("AuditType"),
             email.lower()) for data in bulk_data]

    result, status = db_connector.bulk_write_query(query, params, environment)

    if status == 200:
        return {'message': "Audit Planned Successfully"}, status
    else:
        return {'message': result}, 409
def list_parent_audits(data, environment):
    query = f"""
                SELECT id, audit_title, email
                FROM audir_audit a1
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM audir_audit a2
                    WHERE a2.link_audit = a1.audit_title
                ) AND a1.email IN (
                    SELECT email
                    FROM "audir_users"
                    WHERE organisation = (
                        SELECT organisation
                        FROM "audir_users"
                        WHERE email = '{data.get("eMail").lower()}'
                        LIMIT 1
                    )
                ) AND a1.link_audit='None';
                """
    query_data, status = db_connector.read_all_query(query, environment)
    if status == 200:

        columns = ['id', 'title', 'email']
        parent_audits = [dict(zip(columns, row)) for row in query_data]

        grouped_data = []
        for audit in parent_audits:
            grouped_data.append(
            {"id": audit['id'], "title": audit['title'], "email": audit['email']})

        sorted_grouped_data = sorted(grouped_data, key=lambda x: x["title"])
        return sorted_grouped_data
    else:
        return "Issue fetching Parent Audits"


def check_duplicate_audit(audit_title, environment):
    query = f"SELECT EXISTS(SELECT 1 FROM audir_audit WHERE audit_title = '{audit_title}')"
    query_data, status = db_connector.read_one_query(query, environment)
    return query_data[0]
