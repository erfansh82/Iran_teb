from kavenegar import *

def send_sms(phone_number,text):
    
    try:
        api = KavenegarAPI('45495679346C594939524A2F63303251796473324F6469704B4B482F68764D344F324E466A6843526866383D')
        # str(phone_number),
        params = {
            'receptor' : '09362815318',
            'message' : str(text)
        }   
        response = api.sms_send(params)
        print(response)
    except APIException as e: 
        print(e)
    except HTTPException as e: 
        print(e)
        return True
