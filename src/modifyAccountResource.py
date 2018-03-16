import requests
from django.core.serializers import json


class modifyAccountResource():
    hd = {'Accept': 'application/json, text/javascript, */*; q=0.01',
          'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0',
          'X-Requested-With': 'XMLHttpRequest'}

    # 修改基本账户信息
    def modifyBasicAccount(self, cookie,data):
        url = "http://www.cloudsim.ml:8090/modifyBasicAccount"
        iccid = data['iccid']
        imsi = data['imsi']
        operatorName = data['operatorName']
        mcc = data['mcc']
        operatorId = data['operatorId']
        mainBalance = data['mainBalance']
        expiresTime = data['expiresTime']
        r = requests.post(url,cookies=cookie,header = modifyAccountResource.hd ,data={'iccid': iccid, 'imsi': imsi,'operatorName':operatorName,
                                'mcc': mcc, 'operatorId':operatorId, 'mainBalance':mainBalance, 'expiresTime':expiresTime,
                                    'oldBasicStr':'{"id":null,"iccid":"8986011785112933841","imsi":"460012018633614","mcc":"460","operatorId":"46001","operatorName":"中国联通","mainBalance":1.9,"expiresTime":1522512000000,"planId":null,"lastUpdateTime":null}'})
        r.text()
        result = json.loads(r.text)
        print('操作结果：', result['msg'])

        ##
        # id:
        # iccid: 8986011785112933841
        # imsi: 460012018633614
        # accountId:
        # operatorName: 中国联通
        # mcc: 460
        # operatorId: 46001
        # mainBalance: 1.9
        # expiresTime: 1522512000000
        # oldBasicStr: {"id": null, "iccid": "8986011785112933841", "imsi": "460012018633614", "mcc": "460",
        #               "operatorId": "46001", "operatorName": "中国联通", "mainBalance": 1.9, "expiresTime": 1522512000000,
        #               "planId": null, "lastUpdateTime": null}
        ##

    # 修改兑换账户信息
    def modifyExchangeAccount(self,cookie,data):
        url = "http://www.cloudsim.ml:8090/modifyExchangeAccount"
        sourceType = data['sourceType']
        exchangesList = data['exchangesList']
        iccid = data['iccid']
        oldExchangeList = data['oldExchangeList']

        r = requests.post(url,cookies=cookie,header = modifyAccountResource.hd ,data={'iccid': iccid, 'sourceType': sourceType,'exchangesList':exchangesList,
                                'oldExchangeList': oldExchangeList})
        r.text()
        result = json.loads(r.text)
        print('操作结果：', result['msg'])

        ##
        # sourceType: 1
        # exchangesList: [{"iccid": "8986011785112933841", "source": 1, "canDel": true, "balance": "0.1",
        #                  "expiresTime": 1521043200000}]
        # iccid: 8986011785112933841
        # oldExchangeList: null
        ##


    # 修改资源账户信息
    def modifyResourceList(self,cookie,data):
        url = "http://www.cloudsim.ml:8090/modifyResourceList"
        resourcesList = data['resourcesList']
        iccid = data['iccid']
        oldResourceList = data['oldResourceList']

        r = requests.post(url,cookies=cookie,header = modifyAccountResource.hd ,data={'iccid': iccid, 'resourcesList': resourcesList,'oldResourceList':oldResourceList,})
        r.text()
        result = json.loads(r.text)
        print('操作结果：', result['msg'])
        #
        # # 新增
        # resourcesList: [
        #     {"id": "", "iccid": "8986011785112933841", "resourceCode": "2018022801462202011", "resourceId": 401,
        #      "unit": 2, "totalAmount": 1617.78, "usedAmount": 0, "expiresTime": 1522512000000, "startingTime": "",
        #      "endingTime": "", "lastUpdateTime": null},
        #     {"iccid": "8986011785112933841", "resourceId": "401", "unit": "2", "canDel": true, "totalAmount": "10",
        #      "expiresTime": 1521043200000}]
        # iccid: 8986011785112933841
        # oldResourceList: [
        #     {"id": "", "iccid": "8986011785112933841", "resourceCode": "2018022801462202011", "resourceId": 401,
        #      "unit": 2, "totalAmount": 1617.78, "usedAmount": 0, "expiresTime": 1522512000000, "startingTime": "",
        #      "endingTime": "", "lastUpdateTime": null}]
        # ####

        ## 删除
        # resourcesList: [
        #     {"id": "", "iccid": "8986011785112933841", "resourceCode": "2018022801462202011", "resourceId": 401,
        #      "unit": 2, "totalAmount": 1617.78, "usedAmount": 0, "expiresTime": 1522512000000, "startingTime": "",
        #      "endingTime": "", "lastUpdateTime": null}]
        # iccid: 8986011785112933841
        # oldResourceList: [
        #     {"id": "", "iccid": "8986011785112933841", "resourceCode": "2018022801462202011", "resourceId": 401,
        #      "unit": 2, "totalAmount": 1617.78, "usedAmount": 0, "expiresTime": 1522512000000, "startingTime": "",
        #      "endingTime": "", "lastUpdateTime": null},
        #     {"iccid": "8986011785112933841", "resourceId": "401", "unit": "2", "canDel": true, "totalAmount": "10",
        #      "expiresTime": 1521043200000}]
        ##
