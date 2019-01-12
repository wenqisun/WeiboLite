from weibo import Weibo
from typing import List
from GstoreConnector import GstoreConnector
import json
import ast
user_db = "weibo"
weibo_db = "weibo_test"


class UserError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class DataBaseOp(object):
    def __init__(self, server_ip='192.168.150.130', server_port=9000, admin="root", password="123456"):
        '''
        initialize a data base operator.
        :param server_ip: ip of server, defualt as "127.0.0.1"
        :param server_port: port of server, default as 9000
        :param admin: administer of the server, default as "root"
        :param password: password of the server, default as "123456"
        '''
        self.Gconn = GstoreConnector(server_ip, server_port)
        ret = self.Gconn.build("weibo", "data/weibo/weibo.nt", admin, password)
        self.admin = admin
        self.password = password

    def login(self, user_name: str = "Jing_Mini_Shop", password: str = "123456") -> bool:
        '''
        login method.
        :param user_name: username
        :param password: password of that user
        :return: True or False
        '''

        sparql_query = '''
        select ?uid ?password 
        where
        {
        ?uid <http://localhost:2020/vocab/user_name> '%s'.
        ?uid <http://localhost:2020/vocab/password> ?password.
        }
        ''' % user_name
        print(sparql_query)
        self.Gconn.load(user_db, self.admin, self.password)
        result = self.Gconn.query(self.admin, self.password, user_db, sparql_query)
        print(result)
        json_out = json.loads(result)
        self.Gconn.unload(user_db, self.admin, self.password)
        if json_out["StatusCode"] == 0:
            if json_out["results"]["bindings"] and json_out["results"]["bindings"][0] and \
                    json_out['results']['bindings'][0]["password"]["value"] == password:
                return True
            else:
                return False
        else:
            raise (UserError((json_out["StatusMsg"])))

    def register(self, user_name: str = "Jing_Mini_Shop_01", password: str = "123456", email: str = "123_1@456.com", userid: str = "245214419001") -> bool:
        '''
        reg method, process the reg and return whether reg is succeed.
        :param user_name:
        :param password:
        :param email:
        :param userid:
        :return: True or False
        '''

        sparql_query = '''
        select ?uid
        where
        {
        ?uid <http://localhost:2020/vocab/user_name> "%s".
        }
        ''' % user_name
        print(sparql_query)
        self.Gconn.load(user_db, self.admin, self.password)
        result_query = self.Gconn.query(self.admin, self.password, user_db, sparql_query)
        print(result_query)
        json_out = json.loads(result_query)
        if json_out["StatusCode"] == 0:
            if json_out["results"]['bindings']:
                raise UserError("name existed")
        else:
            raise UserError(json_out["StatusMsg"])

        user_id = "http://localhost:2020/user/" + userid
        sparql_insert = '''
        insert data
        {
        <%s> <http://localhost:2020/vocab/user_uid> "%s".
        <%s> <http://localhost:2020/vocab/user_name> "%s".
        <%s> <http://localhost:2020/vocab/email> "%s".
        <%s> <http://localhost:2020/vocab/password> "%s".
        }
        ''' % (user_id, userid, user_id, user_name, user_id, email, user_id, password)
        print(sparql_insert)
        result_insert = self.Gconn.query(self.admin, self.password, user_db, sparql_insert)
        print(result_insert)
        json_out = json.loads(result_insert)
        self.Gconn.unload(user_db, self.admin, self.password)
        if json_out["StatusCode"] == 402:
            return True
        else:
            raise UserError(json_out["StatusMsg"])

    def recent_my_weibo(self, user_name: str, length: int = 25) -> List[Weibo]:
        '''
        get recent new weibo of a user's friends.
        :param user_name:
        :param length: numbers of weibo
        :return: list[ type(class Weibo) ]
        '''

        sparql_check = "select  ?o  where { <http://localhost:2020/weibo/"+user_name+"> ?p ?o . }"
        print(sparql_check)
        self.Gconn.load(user_db, self.admin, self.password)
        result_check = self.Gconn.query(self.admin, self.password, user_db, sparql_check)
        return result_check

    def recent_new_weibo(self, user_name: str, length: int = 25) -> List[Weibo]:
        '''
        get recent new weibo of a user's friends.
        :param user_name:
        :param length: numbers of weibo
        :return: list[ type(class Weibo) ]
        '''

        sparql_check =  "select ?o  where {?s ?p ?o . FILTER regex(?o, 'userrelation #"+user_name+"')}"
        print(sparql_check)
        self.Gconn.load(user_db, self.admin, self.password)
        result_check = self.Gconn.query(self.admin, self.password, user_db, sparql_check)
        user_friends = ast.literal_eval(result_check)
        a=user_friends['results']['bindings']
        friends=[]
        prelen = len("userrelation #"+user_name+".")
        print(prelen)
        for tmp in a:
            friends.append(tmp['o']['value'][prelen:])
        print(friends)
        for userid in friends:
            sparql_check_weiboid = "select ?s  where {?s <http://localhost:2020/vocab/weibo_uid> ?o . FILTER regex(?o, '" + userid + "')}"
            tmp1 = self.Gconn.query(self.admin, self.password, user_db, sparql_check_weiboid)
            weibo_id = ast.literal_eval(tmp1)
            print(weibo_id)

        result_check2 = []
        '''
        for userid in friends:
            sparql_check_weibo = "select  ?o  where { <http://localhost:2020/weibo/" + userid + "> ?p ?o . }"
            tmp2 = self.Gconn.query(self.admin, self.password, user_db, sparql_check_weibo)
            weibo_dict = ast.literal_eval(tmp2)
            result_check2.append(weibo_dict)
        '''
        return result_check2

    def fans(self, user_name: str, length: int = 25) -> List[str]:
        '''
        return the fans' user_name of a user.
        :param user_name: the user's user_name
        :param length: max length of fans list
        :return: a list of str, str is the user_names of the user's fans
        '''
        sparql_check = '''
        select ?username  
        where
        {
        ?idr <username> "%s". 
        ?idl <follow> ?idr.
        ?idl <username> ?username 
        }
        ''' % user_name
        self.Gconn.load(user_db, self.admin, self.password)
        result_check = self.Gconn.query(self.admin, self.password, user_db, sparql_check)
        json_check = json.loads(result_check)
        if json_check["StatusCode"] == 0:
            resultlist = json_check["results"]["bindings"]
            if len(resultlist) > length:
                resultlist = resultlist[0:length]
            valuelist = [result["username"]["value"] for result in resultlist]
            return valuelist
        else:
            raise UserError(json_check["StatusMsg"])

    def follows(self, user_name: str, length: int = 25) -> List[str]:
        '''
        return the follow list of a user.
        :param user_name: the user's user_name
        :param length: max length of follows list
        :return: a list of str, str is the user_names of the user's follows
        '''

        sparql_check = '''
        select ?username  
        where
        {
        ?id <username> "%s". 
        ?id <follow> ?id2.
        ?id2 <username> ?username 
        }
        ''' % user_name
        self.Gconn.load(user_db, self.admin, self.password)
        result_check = self.Gconn.query(self.admin, self.password, user_db, sparql_check)
        json_check = json.loads(result_check)
        if json_check["StatusCode"] == 0:
            resultlist = json_check["results"]["bindings"]
            if len(resultlist) > length:
                resultlist = resultlist[0:length]
            valuelist = [result["username"]["value"] for result in resultlist]
            return valuelist
        else:
            raise UserError(json_check["StatusMsg"])

    def add_follow(self, user_name: str, follow_name: str) -> bool:
        '''
        add a new follows.(关注)
        :param user_name: current user
        :param follow_name: the follow's user_name
        :return: whether this progress is success.
        '''

        sparql_check = '''
        select ?idl ?idr 
        where
        {
        ?idl <username> "%s".
        ?idr <username> "%s".
        }
        ''' % (user_name, follow_name)
        self.Gconn.load(user_db, self.admin, self.password)
        result_check = self.Gconn.query(self.admin, self.password, user_db, sparql_check)
        json_check = json.loads(result_check)
        self.Gconn.unload(user_db, self.admin, self.password)
        if json_check["StatusCode"] == 0:
            if json_check["results"]["bindings"]:
                idl = json_check['results']['bindings'][0]["idl"]["value"]
                idr = json_check["results"]["bindings"][0]["idr"]["value"]
            else:
                raise UserError("there is no such username")
        else:
            raise UserError(json_check["StatusMsg"])
        sparql_insert = '''
        insert data
        {
        <%s> <follow> <%s>.
        }
        ''' % (idl, idr)
        self.Gconn.load(user_db, self.admin, self.password)
        result_insert = self.Gconn.query(self.admin, self.password, user_db, sparql_insert)
        self.Gconn.unload(user_db, self.admin, self.password)
        self.Gconn.checkpoint(user_db, self.admin, self.password)
        json_insert = json.loads(result_insert)
        if json_insert["StatusCode"] == 402:
            return True
        else:
            raise UserError(json_insert["StatusMsg"])

    def delete_follow(self, user_name: str, follow_name: str) -> bool:
        '''
        delete a follows.
        :param user_name: current user
        :param follow_name: the follow's user_name
        :return: whether this progress is success.
        '''

        sparql_check = '''
        select ?idl ?idr 
        where
        {
        ?idl <username> "%s".
        ?idr <username> "%s".
        ?idl <follow> ?idr
        }
        ''' % (user_name, follow_name)
        self.Gconn.load(user_db, self.admin, self.password)
        result_check = self.Gconn.query(self.admin, self.password, user_db, sparql_check)
        json_check = json.loads(result_check)
        self.Gconn.unload(user_db, self.admin, self.password)
        if json_check["StatusCode"] == 0:
            if json_check["results"]["bindings"]:
                idl = json_check['results']['bindings'][0]["idl"]["value"]
                idr = json_check["results"]["bindings"][0]["idr"]["value"]
            else:
                raise UserError("there is no such follow")
        else:
            raise UserError(json_check["StatusMsg"])
        sparql_delete = '''
        delete data
        {
        <%s> <follow> <%s>.
        }
        ''' % (idl, idr)
        self.Gconn.load(user_db, self.admin, self.password)
        result_delete = self.Gconn.query(self.admin, self.password, user_db, sparql_delete)
        self.Gconn.unload(user_db, self.admin, self.password)
        self.Gconn.checkpoint(user_db, self.admin, self.password)
        json_delete = json.loads(result_delete)
        if json_delete["StatusCode"] == 402:
            return True
        else:
            raise UserError(json_delete["StatusMsg"])

    def new_weibo(self, weibo: Weibo) -> bool:
        '''
        sent a new Weibo
        :param weibo: a Weibo object
        :return: whether the Weibo sent successfully
        '''
        value = weibo.value()
        weibo_id = value['owner'] + '_' + str(value['sent_time'])
        weibo_owner = value['owner']
        weibo_time = value['sent_time']
        weibo_context = value['context']
        if value['comments']:
            weibo_comments = str(value['comments'])
        else:
            weibo_comments = ''

        sparql_check = '''
        select ?id 
        where
        {
        ?id <username> "%s".
        }
        ''' % weibo_owner
        self.Gconn.load(user_db, self.admin, self.password)
        result_check = self.Gconn.query(self.admin, self.password, user_db, sparql_check)
        json_check = json.loads(result_check)
        self.Gconn.unload(user_db, self.admin, self.password)
        if json_check["StatusCode"] == 0:
            if json_check["results"]["bindings"]:
                owner_id = json_check["results"]["bindings"][0]["id"]["value"]
            else:
                raise UserError("there is no such username")
        else:
            raise UserError(json_check["StatusMsg"])

        sparql_insert = '''
        insert data
        {
        <%s> <owner> <%s>.
        <%s> <context> "%s".
        <%s> <comments> "%s".
        <%s> <time> "%d".
        }''' % (weibo_id, owner_id, weibo_id, weibo_context, weibo_id, weibo_comments, weibo_id, weibo_time)
        print(sparql_insert)
        self.Gconn.load(user_db, self.admin, self.password)
        result_insert = self.Gconn.query(self.admin, self.password, user_db, sparql_insert)
        self.Gconn.unload(user_db, self.admin, self.password)
        self.Gconn.checkpoint(user_db, self.admin, self.password)
        json_insert = json.loads(result_insert)
        if json_insert["StatusCode"] == 402:
            return True
        else:
            raise UserError(json_insert["StatusMsg"])
