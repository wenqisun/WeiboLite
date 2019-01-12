from flask import Flask,render_template,request
import GstoreConnector
import json
import ast
import sys
import user
from DBop import DataBaseOp

app = Flask(__name__)
u = user.User()
op = DataBaseOp()
sys.path.append('../src')


@app.route('/')
def index():
    u.user_id="1775467263"
    op = DataBaseOp()
    user_name = "3708696074833794"
    results = op.recent_my_weibo(user_name)
    '''
    real_results = []
    for result in results:
        real_results.append(result.value())

    context = {
        'whatsnew': real_results,
        'user_name': user_name
    }
    '''
    print(results)
    print("11111111111111111111")
    weibo_dict = ast.literal_eval(results)
    print(weibo_dict)
    print(weibo_dict['results']['bindings'][4]['o']['value'])
    return render_template('index.html')


@app.route('/new')
def whatsnew():
    '''
    context:
        whatsnew: list: [
            {   owner: 微博作者,
                contexts: 微博内容,
                comments: 评论，list，暂先不实现
            },
            ... ]
        user_name: 用户名
    '''

    # user_name = "1775467263"
    u_id=u.user_name
    results = op.recent_new_weibo(u_id)
    print(results)
    print("2222222222222")
    '''
    if request.method == "GET":
        op = DataBaseOp(True)
        user_name="<http://localhost:2020/weibo/3708696074833794>"
        results = op.recent_new_weibo(user_name)

        real_results = []
        for result in results:
            real_results.append(result.value())

        context = {
            'whatsnew': real_results,
            'user_name': user_name
        }
    '''
    return render_template('index.html')


@app.route('/login')
def login():
    result = op.login()
    print(result)
    return render_template('index.html')


@app.route('/register')
def register():
    result = op.register()
    print(result)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
