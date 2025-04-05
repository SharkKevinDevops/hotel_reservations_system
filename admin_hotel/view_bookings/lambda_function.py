import json
import pymysql
import os

def lambda_handler(event, context):
    try:
        conn = pymysql.connect(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            db='hotel_reservations',
            cursorclass=pymysql.cursors.DictCursor  # Trả kết quả dạng dict
        )

        with conn.cursor() as cur:
            cur.execute("SELECT * FROM bookings")
            results = cur.fetchall()

        return {
            'statusCode': 200,
            'body': json.dumps(results, default=str),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }

    finally:
        if 'conn' in locals():
            conn.close()
