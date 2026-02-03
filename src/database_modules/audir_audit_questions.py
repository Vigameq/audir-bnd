from src.helpers import db_connector


TABLE_NAME = "audir_audit_questions"


def _ensure_table(environment):
    query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            audit_id INTEGER NOT NULL,
            template TEXT,
            template_type TEXT,
            original_question TEXT,
            question TEXT,
            action TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
    """
    db_connector.write_query(query, environment)


def list_overrides(data, environment):
    _ensure_table(environment)
    audit_id = data.get("audit_id")
    query = f"""
        SELECT id, audit_id, template, template_type, original_question, question, action, created_by, created_at, updated_at
        FROM {TABLE_NAME}
        WHERE audit_id = '{audit_id}'
        ORDER BY updated_at ASC, id ASC;
    """
    rows, status = db_connector.read_all_query(query, environment)
    if status != 200:
        return {"message": rows}, 409

    columns = [
        "id",
        "audit_id",
        "template",
        "template_type",
        "original_question",
        "question",
        "action",
        "created_by",
        "created_at",
        "updated_at"
    ]
    return [dict(zip(columns, row)) for row in rows], 200


def add_override(data, environment):
    _ensure_table(environment)
    audit_id = data.get("audit_id")
    template = data.get("template")
    template_type = data.get("template_type")
    original_question = data.get("original_question")
    question = data.get("question")
    action = (data.get("action") or "add").lower()
    created_by = data.get("created_by")

    query = f"""
        INSERT INTO {TABLE_NAME} (
            audit_id,
            template,
            template_type,
            original_question,
            question,
            action,
            created_by
        ) VALUES (
            '{audit_id}',
            '{template}',
            '{template_type}',
            '{original_question}',
            '{question}',
            '{action}',
            '{created_by}'
        ) RETURNING id;
    """
    row, status = db_connector.read_one_query(query, environment)
    if status != 200:
        return {"message": row}, 409
    return {"message": "Audit question updated", "id": row[0]}, 200


def update_override(data, environment):
    _ensure_table(environment)
    override_id = data.get("id")
    if not override_id:
        return {"message": "Missing override id"}, 400

    question = data.get("question")
    template = data.get("template")
    template_type = data.get("template_type")
    original_question = data.get("original_question")
    action = (data.get("action") or "edit").lower()

    query = f"""
        UPDATE {TABLE_NAME}
        SET question = '{question}',
            template = '{template}',
            template_type = '{template_type}',
            original_question = '{original_question}',
            action = '{action}',
            updated_at = NOW()
        WHERE id = '{override_id}';
    """
    result, status = db_connector.write_query(query, environment)
    if status != 200:
        return {"message": result}, 409
    return {"message": "Audit question updated", "id": override_id}, 200


def delete_override(data, environment):
    _ensure_table(environment)
    override_id = data.get("id")
    if not override_id:
        return {"message": "Missing override id"}, 400
    query = f"DELETE FROM {TABLE_NAME} WHERE id = '{override_id}';"
    result, status = db_connector.write_query(query, environment)
    if status != 200:
        return {"message": result}, 409
    return {"message": "Audit question deleted"}, 200
