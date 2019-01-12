from DBop import DataBaseOp

class User(object):
    def __init__(self, user_name: str = None, password: str = None,user_id:str = None):
        self.op = DataBaseOp()
        self.user_name = user_name
        self.password = password
        self.user_id= user_id
        self.friends=['1615743184', '1644395354', '1713926427', '1757353251', '1810632930', '1900887504', '2141791335', '2268291041', '2517869177', '2569274225']
    def login(self):
        if not self.op.login(self.user_name, self.password):
            raise ValueError('Invalid username/password.')

        return

    def whatsnew(self, length=25):
        results = self.op.recent_new_weibo(self.user_name, length)

        real_results = []
        for result in results:
            real_results.append(result.value())

        return real_results