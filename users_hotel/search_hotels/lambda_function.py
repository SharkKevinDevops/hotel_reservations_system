import json
import pymysql
import os

# lambda_handler function
def lambda_handler(event, context):
    # Kết nối với cơ sở dữ liệu MySQL
    try:
        conn = pymysql.connect(
            host = os.environ['RDS_HOST'],
            user = os.environ['RDS_USER'],
            password = os.environ['RDS_PASSWORD'],
            db = 'hotel_reservations'
        )
        
        # Lấy tham số location từ query string
        location = event.get('queryStringParameters', {}).get('location', '')
        
        # Kiểm tra tham số location 
        if not location:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing required parameter: location'}),
                'headers': {'Content-Type': 'application/json'}
            }
            
        # Thực thi câu truy vấn để tìm kiếm khách sạn theo location
        with conn.cursor() as cur:
            cur.execute(
                "SELECT h.id, h.name, h.location, h.image_url, r.type, r.price "
                "FROM hotels h JOIN rooms r ON h.id = r.hotel_id "
                "WHERE h.location LIKE %s AND r.availability_status = 'available'",
                (f"%{location}%",)
            )
            results = [{'id': r[0], 'name': r[1], 'location': r[2], 'image_url': r[3], 'type': r[4], 'price': float(r[5])} for r in cur.fetchall()]
            
        # Nếu không có kết quả nào
        if not results:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No available rooms found for the given location'}),
                'headers': {'Content-Type': 'application/json'}
            }
        # Đóng cơ sở dữ liệu
        conn.close()
        
        # Trả về kết quả
        return {
            'statusCode': 200,
            'body': json.dumps(results),
            'headers': {'Content-Type': 'application/json'}
        }
        
    except pymysql.MySQLError as e:
        # Xử lý lỗi cơ sở dữ liệu
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Database error: {str(e)}"}),
            'headers': {'Content-Type': 'application/json'}
        }
    
    except Exception as e:
        # Xử lý lỗi chung
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f"Unexpected error: {str(e)}"}),
            'headers': {'Content-Type': 'application/json'}
        }

# {
#   "queryStringParameters": {
#     "location": "Dalat"
#   }
# }


# GET
# https://lgtfvb5re1.execute-api.ap-southeast-1.amazonaws.com/dev/users/hotels?location=Phu%20Quoc
# https://lgtfvb5re1.execute-api.ap-southeast-1.amazonaws.com/dev/users/hotels?location=Dalat
