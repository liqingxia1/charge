import re
import requests
import json
import time
import websocket


class simcarCorrect():
    hd = {'Accept': 'application/json, text/javascript, */*; q=0.01',
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
          'X-Requested-With': 'XMLHttpRequest'}

    # 获取校正列表， 并筛选数据
    def getSimcarList(self,cookie,mcc):
        self.cookie = cookie
        self.mcc = mcc
        available_simcar = []
        country_available_simcar = []
        now_time = int(time.time())
        # 校验列表
        calibration = requests.get('http://www.cloudsim.ml:8090/recharge/simcards?pageNumber=1&pageSize=200&operatorId=&imsi=&type=Calibration&iccid=&operatorName=&mcc=&page=1&rows=10',headers=simcarCorrect.hd, cookies=self.cookie)

        try:
            # 将获取到的json数据转换为python数据
            simlistJson = json.loads(calibration.text)
            print(calibration.text)
            print("==============================")
            # 获取返回数据中的sim卡数据
            data = simlistJson['data']
            rows = data['rows']
           # print('*********** 获取到的数据列表 ***********\n',rows)
        except BaseException as e:
            return -1
        # 判断sim卡状态是否为可矫正的状态
        for item in rows:
            lst = item
            remediableSimcar = lst['simCard']
            basic_account = lst['basicAccount']    # 基础账户过期时间
            exchangesList = lst['exchangesList']   # 兑换账户过期时间
            resourcesList = lst['resourcesList']   # 资源账户过期时间
            bf_day = -2
            af_day = 2

            # 将当前系统时间转换为年、月、日
            now_time_y = int(time.strftime('%Y', time.localtime(now_time)))
            now_time_m = int(time.strftime('%m', time.localtime(now_time)))
            now_time_d = int(time.strftime('%d', time.localtime(now_time)))

            # 判断是否存在基本账户信息
            if basic_account != None:
                if basic_account['expiresTime'] != None:
                    # 应获取到的时间戳尾数多3个0，故除以1000
                    basic = int(basic_account['expiresTime']) / 1000

                    # 判断兑换账户是否为空，并将年、月、日，分别赋值
                    if exchangesList != None:
                        exchanges_list=exchangesList[0]
                        exchanges = int(exchanges_list['expiresTime']) / 1000
                        exchanges_y = int(time.strftime('%Y', time.localtime(exchanges)))
                        exchanges_m = int(time.strftime('%m', time.localtime(exchanges)))
                        exchanges_d = int(time.strftime('%d', time.localtime(exchanges)))

                    # 判断基本账户是否为空，并将年、月、日，分别赋值
                    if resourcesList != None:
                        resources_list=resourcesList[0]
                        resources = int(resources_list['expiresTime']) / 1000
                        resources_y = int(time.strftime('%Y', time.localtime(resources)))
                        resources_m = int(time.strftime('%m', time.localtime(resources)))
                        resources_d = int(time.strftime('%d', time.localtime(resources)))

                    # 判断sim卡资源，是否可校正
                    if remediableSimcar['activate'] == True and remediableSimcar['inSimpool'] == True and  remediableSimcar['disabled'] == False and remediableSimcar['inUsed'] == False and remediableSimcar['broken'] == False:
                        # 基础账户对比当前时间是否过期
                        if basic >= now_time:
                            if exchangesList != None:
                                # 根据系统时间，仅查询一定时间范围内的sim卡
                                bf_ex = exchanges_d - now_time_d >= bf_day and exchanges_d - now_time_d <=0
                                af_ex = exchanges_d - now_time_d <= af_day and exchanges_d - now_time_d >= 0
                                # 年份相同时
                                if exchanges_y == now_time_y :
                                    # 月份相同时
                                    if exchanges_m == now_time_m:
                                        # 根据设置的前后时间 对比数据
                                        if bf_ex or af_ex:
                                            available_simcar.append(lst['basicAccount'].copy())
                                    # 资源套餐月份比系统月份多一个月时，判断系统日期是否是月底并且资源套餐为月初
                                    elif exchanges_m - now_time_m == 1:
                                        if now_time_d >= 28 and exchanges_d < 2:
                                            available_simcar.append(lst['basicAccount'].copy())
                            # 与上面雷同，暂未优化
                            if resourcesList != None:
                                bf_sx = resources_d - now_time_d >= bf_day and resources_d - now_time_d <=0
                                af_sx = resources_d - now_time_d <= af_day and resources_d - now_time_d >= 0
                                if resources_y == now_time_y :
                                    if resources_m == now_time_m:
                                        if bf_sx or af_sx:
                                            available_simcar.append(lst['basicAccount'].copy())
                                    elif resources_m - now_time_m == 1:
                                        if now_time_d >= 28 and resources_d < 2:
                                            available_simcar.append(lst['basicAccount'].copy())

        # # 根据当前国家mcc，筛选sim卡列表
        for item in available_simcar:
            if item['mcc'] == self.mcc:
                country_available_simcar.append(item)
        return country_available_simcar


    # 开启rtu模式，下发sim卡到用户
    def rtuBindSimCard(self,cookie,simcList,userId):
        print(simcList)

        succeedListId = 0
        succeedDic = {}
        succeedList = []
        failureListId = 0
        failureDic = {}
        failureList = []

        for simcarData in simcList:
            data = {'iccid': simcarData['iccid'], 'imsi': simcarData['imsi'],
                    'operatorId': simcarData['operatorId'], 'operatorName': simcarData['operatorName'],
                    'userId': userId}
            # 下发分卡请求
            bindsimCard = requests.post('http://www.cloudsim.ml:8090/bindSimCard', data=data, headers=simcarCorrect.hd,
                                        cookies=cookie)
            bindsimcard = json.loads(bindsimCard.text)
            print('操作sim卡：', simcarData['imsi'])
            if bindsimcard['msg'] == '用户不存在或用户未登录':
                print(' 操作结果：%s', (bindsimcard['msg']))
                break
            elif bindsimcard['msg'] == '分卡成功':
                print('操作结果：', bindsimcard['msg'])
                # 等待鉴权
                time.sleep(60)

                # 获取校正短信列表
                sms_list = simcarCorrect.getSmsList(self, cookie, simcarData['mcc'], simcarData['operatorId'])
                for sms in sms_list:
                    # 调用websocket接口，发送短信
                    print('#####当前操作短信：',sms)
                    code,msg = simcarCorrect.socketConnect(self,simcarData['imsi'],userId,sms)

                    # 将查询成功的添加到列表
                    if code == 0:
                        succeedDic['id'] = succeedListId
                        succeedDic['imsi'] = simcarData['imsi']
                        succeedDic['msg'] = msg
                        succeedDic['templateName'] = sms['templateName']
                        succeedList.append(succeedDic.copy())
                        succeedListId += 1
                    # 将查询失败的添加到列表
                    elif msg == '长时间鉴权未过':
                        failureDic['id'] = failureListId
                        failureDic['imsi'] = simcarData['imsi']
                        failureDic['msg'] = msg
                        failureDic['templateName'] = sms['templateName']
                        failureList.append(failureDic.copy())
                        failureListId += 1
                        simcarCorrect.unBindSimCard(self, cookie, simcarData['imsi'], simcarData['iccid'])
                        break
                    else :
                        failureDic['id'] = failureListId
                        failureDic['imsi'] = simcarData['imsi']
                        failureDic['msg'] = msg
                        failureDic['templateName'] = sms['templateName']
                        failureList.append(failureDic.copy())
                        failureListId += 1

                # 调用解绑 还卡接口
                simcarCorrect.unBindSimCard(self,cookie,simcarData['imsi'],simcarData['iccid'])
            elif '已经分到了' in bindsimcard['msg'] :
                print(bindsimcard['msg'])
                regex_start = re.compile("\d{15}")
                imsi = regex_start.findall(bindsimcard['msg'])
                # 调用还卡接口
                simcarCorrect.revuimSimCard(self, cookie, imsi, userId)
            elif '该卡已被下发' in bindsimcard['msg']:
                print(bindsimcard['msg'])
                # 调用解绑 还卡接口
                simcarCorrect.unBindSimCard(self, cookie, simcarData['imsi'], simcarData['iccid'])
            else:
                print('操作结果：', bindsimcard['msg'])

        # 输出操作成功的sim卡
        if succeedList:
            print("=========================== 华丽丽的分割线 =============================")
            print('已成功操作的sim卡：', len(succeedList))
            for i in succeedList:
                print(i)

        # 输出操作失败的sim卡
        if failureList:
            print("=========================== 华丽丽的分割线 =============================")
            print('操作失败的sim卡：', len(failureList))
            for i in failureList:
                print(i)


    # 建立websocket连接，发送短信
    def socketConnect(self,imsi,userId,sms):
        if sms['targetNumber'] != None:
            data = "method=sms&userId="+userId+"&sendNumber="+sms['targetNumber']+"&sendContent="+sms['requestExpression']+"&disableLists=aaa&serialNumber=0&receiptType=0&taskId=fe896ae260f44874b4602db329222c3&imsi=" + imsi
        else :
            data = "method=ussd&userId="+ userId+"&ussdCode="+sms['requestExpression']+"&disableLists=aaa&serialNumber=0&receiptType=1&taskId=52001e9d299a43439902f1152e2c1cae&imsi="+imsi
        ws = websocket.create_connection('ws://13.228.189.229:18089')
        cont = 0
        while 1:
            ws.send(data)
            rsp_code = ws.recv()
            print("code:", rsp_code)
            if rsp_code == '0':
                time.sleep(5)
                try :
                    ws.settimeout(60.0)
                    rsp_msg = ws.recv()
                    ws.settimeout(5.0)
                except websocket.WebSocketTimeoutException as e:
                    print('************************ 无法收到短信回复 ************************')
                    ws.close()
                    code = -1
                    msg = "无法收到短信回复"
                    return code, msg
                # a = ws.recv_data()
                print("code:%s,msg:%s"%(rsp_code,rsp_msg))
                ws.close()
                code = 0
                msg = rsp_msg
                return code, msg
            elif rsp_code == '-1':
                cont = cont + 1
                if cont <4:
                    time.sleep(2)
                else:
                    ws.close()
                    print('************************ 长时间鉴权未过 ************************')
                    code = -1
                    msg = '长时间鉴权未过'
                    return code, msg
            else :
                ws.close()
                print("************************************************")
                code = -1
                msg = '其他异常'
                return code, msg

    # 获取校正的短信模板，传入值
    # country_id:国家，operator_id:运营商 为空时查询全部
    def getSmsList(self, cookie, country_id, operator_id):
        msg_list = []
        msg_dic = {}
        # 根据国家与运营商，获取短信模板
        url = "http://www.cloudsim.ml:8090/queryTemplateList?pageIndex=1&pageSize=30&countryId="+country_id+"&operatorId="+operator_id+"&templateType=4&validState=&templateName=&page=1&rows=10&sort=optDate&order=asc"
        revise_msg = requests.get(url, headers=simcarCorrect.hd, cookies=cookie)
        # print(revise_msg.text)
        msg_list_json = json.loads(revise_msg.text)
        for msg_rows in msg_list_json['rows']:
            msg_dic['targetNumber'] = msg_rows['targetNumber']
            msg_dic['requestExpression'] = msg_rows['requestExpression']
            msg_dic['templateName'] = msg_rows['templateName']
            msg_list.append(msg_dic.copy())
        print("=================================")
        for i in msg_list:
            print(i)
        return msg_list


    # 执行还卡操作
    def revuimSimCard(self,cookie, imsi, userId):
        print('======================还卡操作========================')
        data = {}
        data['userId'] = userId
        data['imsi'] = imsi
        # 调用还卡接口
        revuim = requests.post('http://www.cloudsim.ml:8081/ass/user_revuim', data=data, headers=simcarCorrect.hd,
                                    cookies=cookie)
        msg = json.loads(revuim.text)
        print(msg['msg'])
        if msg['msg'] =='成功':
            time.sleep(3)
        else:
            print("************************ 还卡失败 ************************")

    # 执行解绑操作
    def unBindSimCard(self,cookie, imsi, iccid):
        print('======================解绑 还卡操作========================')
        data = {}
        data['iccid'] = iccid
        data['imsi'] = imsi
        # 调用还卡接口
        revuim = requests.post('http://www.cloudsim.ml:8090/unBindSimCard', data=data, headers=simcarCorrect.hd,
                                    cookies=cookie)
        msg = json.loads(revuim.text)
        print(msg['msg'])
        if msg['msg'] =='还卡成功':
            time.sleep(3)
        else:
            print("************************解绑 还卡失败 ************************")








