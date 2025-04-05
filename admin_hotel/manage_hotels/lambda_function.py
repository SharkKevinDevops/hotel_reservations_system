import json
import pymysql
import os

def lambda_handler(event, context):
    try:
        conn = pymysql.connect(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            db='hotel_reservations'
        )

        action = event.get('httpMethod')
        body = json.loads(event.get('body') or '{}')

        with conn.cursor() as cur:
            if action == 'POST':
                required_fields = ['name', 'location', 'description', 'image_url']
                missing = [f for f in required_fields if f not in body]
                if missing:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': f"Missing fields: {', '.join(missing)}"}),
                        'headers': {'Content-Type': 'application/json'}
                    }

                cur.execute(
                    "INSERT INTO hotels (name, location, description, image_url) VALUES (%s, %s, %s, %s)",
                    (body['name'], body['location'], body['description'], body['image_url'])
                )
                conn.commit()
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Hotel added', 'id': cur.lastrowid}),
                    'headers': {'Content-Type': 'application/json'}
                }

            elif action == 'DELETE':
                if 'id' not in body:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Missing hotel id'}),
                        'headers': {'Content-Type': 'application/json'}
                    }

                # Xóa các phòng liên quan trong bảng rooms
                cur.execute("DELETE FROM rooms WHERE hotel_id = %s", (body['id'],))
                conn.commit()

                # Xóa khách sạn
                cur.execute("DELETE FROM hotels WHERE id = %s", (body['id'],))
                conn.commit()
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Hotel and related rooms deleted'}),
                    'headers': {'Content-Type': 'application/json'}
                }


            else:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid HTTP method'}),
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


# POST
# {
#   "name": "Palm Resort",
#   "location": "Miami Beach, FL",
#   "description": "A luxury beachfront resort with spa and pool.",
#   "image_url": "https://example.com/images/palm-resort.jpg"
# }


# DELETE
# {
#   "id": 5
# }
