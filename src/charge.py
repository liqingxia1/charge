from src.login import alogin
from src.simcarCorrect import simcarCorrect

class charge():
    session = None
    def correct(self):
        ######################
        # web_login_user:web登录时用户； web_password:web登录时加密的密码，当前为123456；
        # end_user:终端的用户名
        ######################
        web_login_user = "yanghongyan"
        web_password = "e10adc3949ba59abbe56e057f20f883e"
        end_user='yanghongyan'
        mcc = '456'

        session = alogin.userLogin(self, web_login_user, web_password)
        simcarList = simcarCorrect.getSimcarList(self, session, mcc)
        if simcarList != -1:
            print('**************** simcars获取成功 *****************')
            simcarCorrect.rtuBindSimCard(self,session,simcarList,end_user)
        else:
            print('**************** simcars获取异常 *****************')


if __name__ == '__main__':
    cg = charge()
    cg.correct()
