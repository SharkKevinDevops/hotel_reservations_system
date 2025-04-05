import json
import pymysql
import os
import boto3

# Tạo sns client
sns = boto3.client('sns')

# function xử lý cho lambda
def lambda_handler(event, context):
    # Kết nối đến cơ sở dữ liệu MySQL
    conn = pymysql.connect(
        host = os.environ['RDS_HOST'],
        user = os.environ['RDS_USER'],
        password = os.environ['RDS_PASSWORD'],
        db = 'hotel_reservations'
    )
    
    try:
        # Parse body từ event
        raw_body  = event.get("body", "{}")
        try:
            body = json.loads(raw_body) if isinstance(raw_body, str) else raw_body
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON format in request body'}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        #  Kiểm tra Booking ID để xác nhận thanh toán
        booking_id = body.get('booking_id')
        if not booking_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required field: booking_id'}),
                'headers': {'Content-Type': 'application/json'}
            }
        
        # Kiểm tra định dạng booking_id
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
            if not cur.fetchone():
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Booking ID {booking_id} does not exist'}),
                    'headers': {'Content-Type': 'application/json'}
                }
            # Cập nhật trạng thái thanh toán
            cur.execute("UPDATE bookings SET payment_status = 'completed' WHERE id = %s", (booking_id,))
        
        # commit transaction
        conn.commit()
        
        # Gửi thông báo SNS
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
            Message=f"Payment completed for booking id:{booking_id}"
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Payment completed'}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    finally:
        conn.close()
        
        
# Missing fields:
# {
#   "body": "{}"
# }


# Invalid JSON format in request body:
# {
#   "body": "{\"booking_id\": 99999}"
# }


# Success:
# {
#   "body": "{\"booking_id\": 1}"
# }

#  Database Connection Failure (Simulated):
# {
#   "body": "{\"booking_id\": 1}"
# }
