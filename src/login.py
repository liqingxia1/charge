
import requests

class alogin():
    def __init__(self):
        pass
    def userLogin(self, user_name, password):
        # 发送登录请求
        r = requests.post('http://www.cloudsim.ml:8082/upms/login',
                          data={'userNo': user_name, 'userPwd': password, 'projectCode': 'charge'})
        print("cookies:",r.cookies)
        print("code::",r.status_code)

        # 判断登录是否成功，并返回cookie，或错误
        try:
            if r.status_code == 200:
                ticket = r.cookies['ticket']
                userName = r.cookies['userName']
                userNo = r.cookies['userNo']
                locale = 'zh_CN'
                cookie = {'userName': userName, 'userNo': userNo, 'ticket': ticket, 'locale': locale}
                print('**********************  登录成功  **********************')
                return cookie
            elif r.status_code >= 400 and r.status_code <= 500:
                print('**********************  参数错误！ 登录失败  **********************')
                raise ValueError
            else:
                print('**********************  连接服务器错误！ 登录失败  **********************')
                return None
        except Exception:
            print('**********************  出现异常！ 登录失败  **********************')
            return None
from socket import *