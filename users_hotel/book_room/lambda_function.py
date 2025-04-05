import json
import pymysql
import os
import boto3
from datetime import datetime


# Tạo sns client
sns = boto3.client('sns')

# function xử lý cho lambda
def lambda_handler(event, context):
    conn = None
    
    try:
        # Parse body từ event
        body = json.loads(event['body'])
        
        # Kiểm tra các field cần thiết
        required_fields = ['user_id', 'room_id', 'check_in', 'check_out']
        
        for field in required_fields:
            if field not in body:
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'Missing required field: {field}'}),
                    'headers': {'Content-Type': 'application/json'}
                }

        # Lấy thông tin từ body
        user_id = int(body['user_id'])
        room_id = int(body['room_id'])
        check_in = body['check_in']
        check_out = body['check_out']
        
        # Kiểm tra định dạng ngày tháng
        try:
            datetime.strptime(check_in, '%Y-%m-%d')
            datetime.strptime(check_out, '%Y-%m-%d')
        except ValueError:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid date format. Use YYYY-MM-DD.'}),
                'headers': {'Content-Type': 'application/json'}
            }
            
        # Kết nối đến cơ sở dữ liệu MySQL
        conn = pymysql.connect(
            host = os.environ['RDS_HOST'],
            user = os.environ['RDS_USER'],
            password = os.environ['RDS_PASSWORD'],
            db = 'hotel_reservations'
        )
        
        with conn.cursor() as cur:
            # Chèn bảng ghi đặt phòng mới
            cur.execute(
                "INSERT INTO bookings (user_id, room_id, check_in_date, check_out_date, payment_status) "
                "VALUE (%s, %s, %s, %s, 'pending')", 
                (user_id, room_id, check_in, check_out)
            )
            
            # Lấy ID của booking vừa tạo
            booking_id = cur.lastrowid
            
            # Câp nhật trạng thái phòng sang booked
            cur.execute(
                "UPDATE rooms SET availability_status = 'booked' WHERE id = %s", 
                (room_id,)
            )
            
        # commit thay đổi
        conn.commit()
        
        # gửi thông báo đến SNS
        sns.publish(
            TopicArn = os.environ['SNS_TOPIC_ARN'],
            Message = f"Booking inititated for room {room_id}. Awaiting payment."
        )
        
        # Trả về phản hồi thành công
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Booking initiated successfully with booking ID: {}'.format(booking_id)}),
            'headers': {'Content-Type': 'application/json'}
        }
        
    except pymysql.MySQLError as e:
        # Xử lý lỗi MySQL
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }

    finally:
        # Đảm bảo đóng kết nối
        if conn:
            conn.close()



# POST test api
# {
#     "user_id": 1,
#     "room_id": 101,
#     "check_in": "2025-05-01",
#     "check_out": "2025-05-10"
# }


# Missing fields:
#     {
#     "user_id": 1,
#     "room_id": 101
# }

# Ngày tháng không hợp lệ:
# {
#     "user_id": 1,
#     "room_id": 101,
#     "check_in": "2025-05-01",
#     "check_out": "2025-13-10"
# }


# Lỗi cơ sở dữ liệu trong database:
# {
#     "user_id": 1,
#     "room_id": 9999,
#     "check_in": "2025-05-01",
#     "check_out": "2025-05-10"
# }
