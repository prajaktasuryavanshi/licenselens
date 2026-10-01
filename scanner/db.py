import psycopg2
import os

def save_scan(project_name, target_license, results):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO scans (project_name, target_license) VALUES (%s, %s) RETURNING id",
        (project_name, target_license)
    )
    scan_id = cur.fetchone()[0]
    for dep in results:
        cur.execute(
            "INSERT INTO dependencies (scan_id, name, version, license, risk) VALUES (%s, %s, %s, %s, %s)",
            (scan_id, dep["name"], dep["version"], dep["license"], dep["risk"])
        )
    conn.commit()
    cur.close()
    conn.close()
    return scan_id
