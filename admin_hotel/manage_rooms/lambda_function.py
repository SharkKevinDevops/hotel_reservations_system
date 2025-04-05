import json
import pymysql
import os

# function lambda_handler
def lambda_handler(event, context):
    # thử kết nối đến RDS
    try:
        conn = pymysql.connect(
            host=os.environ['RDS_HOST'],
            user=os.environ['RDS_USER'],
            password=os.environ['RDS_PASSWORD'],
            db = 'hotel_reservations'
        )
        
        action = event.get('httpMethod')
        body = json.loads(event.get('body')) if event.get('body') else {}
        
        with conn.cursor() as cur:
            if action == 'POST':
                # Thêm các trường yêu cầu
                required = ['hotel_id', 'type', 'price', 'availability_status']
                missing = [k for k in required if k not in body]
                
                # Nếu missing
                if missing:
                    return {
                            'statusCode': 400,
                            'body': json.dumps({'error': f'Missing required fields: {", ".join(missing)}'}),
                            'headers': {'Content-Type': 'application/json'}
                        }
                # Thực thi insert
                cur.execute(
                        "INSERT INTO rooms (hotel_id, type, price, availability_status) VALUES (%s, %s, %s, %s)",
                        (body['hotel_id'], body['type'], body['price'], body['availability_status'])
                    )
                conn.commit()
                return {
                        'statusCode': 200,
                        'body': json.dumps({'message': 'Room added', 'id': cur.lastrowid}),
                        'headers': {'Content-Type': 'application/json'}
                    }
                
            # Nếu action là PUT thì cập nhật thông tin phòng
            elif action == 'PUT':
                # Kiểm tra các trường yêu cầu
                if 'id' not in body or 'availability_status' not in body:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Missing room id or availability_status'}),
                        'headers': {'Content-Type': 'application/json'}
                    }
                # thực thi cập nhật
                cur.execute(
                    "UPDATE rooms SET availability_status = %s WHERE id = %s",
                    (body['availability_status'], body['id'])
                )
                conn.commit()
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Availability updated'}),
                    'headers': {'Content-Type': 'application/json'}
                }

    
    
            # Nếu action là Delete thì xóa phòng theo id
            elif action == 'DELETE':
                # Kiểm tra id
                if 'id' not in body:
                    return {
                        'statusCode': 400,
                        'body': json.dumps({'error': 'Missing room id'}),
                        'headers': {'Content-Type': 'application/json'}
                    }

                cur.execute("DELETE FROM rooms WHERE id = %s", (body['id'],))
                conn.commit()
                return {
                    'statusCode': 200,
                    'body': json.dumps({'message': 'Room deleted'}),
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
            
            
# Test
# POST

# {
#   "hotel_id": 1,
#   "type": "Deluxe",
#   "price": 120,
#   "availability_status": "available"
# }


# PUT
# {
#   "id": 5,
#   "availability_status": "booked"
# }


# DELETE

# {
#     "id": 5
# }