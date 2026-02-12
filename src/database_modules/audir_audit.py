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


def list_all_audits(data, environment):
    email = (data.get("eMail") or "").lower()
    if not email:
        return {"message": "Email is required"}, 400

    query = f"""
                SELECT
                    id,
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
                    audit_status,
                    email
                FROM audir_audit
                WHERE email IN (
                    SELECT email
                    FROM audir_users
                    WHERE organisation = (
                        SELECT organisation
                        FROM audir_users
                        WHERE email = '{email}'
                        LIMIT 1
                    )
                );
                """
    rows, status = db_connector.read_all_query(query, environment)
    if status != 200:
        return {"message": rows}, status

    columns = [
        'id',
        'link_audit',
        'audit_title',
        'functions',
        'template',
        'function_template',
        'start_date',
        'end_date',
        'auditors',
        'auditees',
        'city',
        'country',
        'audit_scope',
        'audit_type',
        'audit_status',
        'email'
    ]
    audit_data = [dict(zip(columns, row)) for row in rows]
    return {"audit_data": audit_data}, 200

def initiate_audit(data, environment):
    audit_id = data.get("audit_id")
    if not audit_id:
        return {"message": "audit_id is required"}, 400

    query = f"""
        UPDATE audir_audit
        SET audit_status = 'inprogress'
        WHERE id = '{audit_id}'
        RETURNING id, audit_status;
    """
    row, status = db_connector.read_one_query(query, environment)
    if status != 200 or not row:
        return {"message": "Audit not found or unable to initiate"}, 409

    return {"message": "Audit initiated successfully", "audit_id": row[0], "audit_status": row[1]}, 200


def check_duplicate_audit(audit_title, environment):
    query = f"SELECT EXISTS(SELECT 1 FROM audir_audit WHERE audit_title = '{audit_title}')"
    query_data, status = db_connector.read_one_query(query, environment)
    return query_data[0]


from datetime import datetime
import calendar


def _parse_date(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(str(value), fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def dashboard_summary(data, environment):
    email = data.get('eMail')
    date_filter = data.get('start_date_filter') or {}
    from_date = date_filter.get('from')
    to_date = date_filter.get('to')
    date_clause = ''
    if from_date and to_date:
        date_clause = f" AND start_date::date >= '{from_date}' AND start_date::date <= '{to_date}'"
    query = f"""
                SELECT audit_status, start_date, end_date, auditors, auditees
                FROM audir_audit
                WHERE email IN (
                    SELECT email
                    FROM audir_users
                    WHERE organisation = (
                        SELECT organisation
                        FROM audir_users
                        WHERE email = '{email.lower()}'
                        LIMIT 1
                    )
                ){date_clause};
                """
    rows, status = db_connector.read_all_query(query, environment)
    if status != 200:
        return {"message": rows}, status

    user_query = f"""
                SELECT first_name, last_name, email
                FROM audir_users
                WHERE organisation = (
                    SELECT organisation
                    FROM audir_users
                    WHERE email = '{email.lower()}'
                    LIMIT 1
                );
                """
    user_rows, user_status = db_connector.read_all_query(user_query, environment)
    email_to_name = {}
    if user_status == 200:
        for first, last, user_email in user_rows:
            email_to_name[user_email.lower()] = f"{first} {last}".strip()

    total = len(rows)
    status_counts = {"created": 0, "inprogress": 0, "submitted": 0, "completed": 0}
    overdue = 0
    now = datetime.utcnow()
    monthly_counts = {i: 0 for i in range(1, 13)}
    auditor_stats = {}
    auditee_stats = {}

    for status_value, start_date, end_date, auditors, auditees in rows:
        status_key = str(status_value or '').lower()
        if status_key in status_counts:
            status_counts[status_key] += 1
        start_dt = _parse_date(start_date)
        end_dt = _parse_date(end_date)
        if start_dt and start_dt.year == now.year:
            monthly_counts[start_dt.month] += 1
        if end_dt and status_key not in ('completed', 'submitted') and end_dt < now:
            overdue += 1
        auditors_list = []
        if auditors:
            auditors_list = [item.strip().lower() for item in str(auditors).split(',') if item.strip()]
        for auditor_email in auditors_list:
            if auditor_email not in auditor_stats:
                auditor_stats[auditor_email] = {"audits": 0, "completed": 0}
            auditor_stats[auditor_email]["audits"] += 1
            if status_key in ('submitted', 'completed'):
                auditor_stats[auditor_email]["completed"] += 1

        auditees_list = []
        if auditees:
            auditees_list = [item.strip().lower() for item in str(auditees).split(',') if item.strip()]
        for auditee_email in auditees_list:
            if auditee_email not in auditee_stats:
                auditee_stats[auditee_email] = {"audits": 0, "completed": 0}
            auditee_stats[auditee_email]["audits"] += 1
            if status_key in ('submitted', 'completed'):
                auditee_stats[auditee_email]["completed"] += 1

    completed_total = status_counts["submitted"] + status_counts["completed"]
    completion_rate = round((completed_total / total) * 100) if total else 0

    monthly = [
        {"month": calendar.month_abbr[month], "count": monthly_counts[month]}
        for month in range(1, 13)
    ]

    auditor_list = []
    for auditor_email, stats in auditor_stats.items():
        completion = round((stats["completed"] / stats["audits"]) * 100) if stats["audits"] else 0
        auditor_list.append({
            "name": email_to_name.get(auditor_email, auditor_email),
            "audits": stats["audits"],
            "completion": completion
        })
    auditor_list = sorted(auditor_list, key=lambda x: x["audits"], reverse=True)[:6]

    auditee_list = []
    for auditee_email, stats in auditee_stats.items():
        completion = round((stats["completed"] / stats["audits"]) * 100) if stats["audits"] else 0
        auditee_list.append({
            "name": email_to_name.get(auditee_email, auditee_email),
            "audits": stats["audits"],
            "completion": completion
        })
    auditee_list = sorted(auditee_list, key=lambda x: x["audits"], reverse=True)[:6]

    return {
        "metrics": {
            "total_audits": total,
            "in_progress": status_counts["inprogress"],
            "overdue": overdue,
            "completion_rate": completion_rate
        },
        "status_breakdown": [
            {"label": "Created", "count": status_counts["created"]},
            {"label": "In Progress", "count": status_counts["inprogress"]},
            {"label": "Submitted", "count": status_counts["submitted"]},
            {"label": "Completed", "count": status_counts["completed"]},
            {"label": "Overdue", "count": overdue}
        ],
        "monthly": monthly,
        "auditors": auditor_list,
        "auditees": auditee_list
    }, 200
