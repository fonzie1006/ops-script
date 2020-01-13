import logging
import random
import json
import sys
import datetime

from github import Github, GithubException
from urllib3.exceptions import ReadTimeoutError


SEARCH_RULES = []
# https://github.com/settings/tokens
TOKEN = ['XXXXXXXXXXXXXXXXXXXXX']
PER_PAGE = 100

RESULT = {}

logger = logging.getLogger(__name__)


# python https://www.jianshu.com/p/5ca8e56081b8

# 生成Github客户端
def new_session():
    token = get_token()
    return Github(token, per_page=PER_PAGE), token


# 随机获取Token
def get_token():
    assert len(TOKEN) > 0, 'TOKEN 不能为空'
    return random.sample(TOKEN, 1)[0]


# 排除某个index,重新随机
def reset_token(token):
    t = TOKEN.remove(token)
    assert len(TOKEN) > 0, 'TOKEN 不能为空'
    return random.sample(t, 1)[0]


# 通过github的搜索语法搜索结果: https://developer.github.com/v3/search/#search-code
def search_by_keyword(keyword, search_page):
    total = 0
    flag = False
    session, token = new_session()
    for i in range(0, len(TOKEN)):
        try:
            response = session.search_code(keyword, sort='indexed', order='desc')
            total = min(response.totalCount, 1000)
            flag = True
            break
        except GithubException as e:
            if 'abuse-rate-limits' in e.data.get('documentation_url'):
                session, token = reset_token(token)
            else:
                logger.exception(e)
            continue
        except ReadTimeoutError:
            continue

    if not flag:
        return None

    # E.G. total = 50，max_page = 1; total = 51, max_page = 2
    # 需要搜索的页数为max_page和task.page中最小的值
    max_page = (total // PER_PAGE) if (not total % PER_PAGE) else (total // PER_PAGE + 1)
    pages = min(max_page, search_page) if search_page else max_page
    page = 0

    while page < pages:
        try:
            page_content = response.get_page(page)
            page += 1
        except GithubException as e:
            if 'abuse-rate-limits' in e.data.get('documentation_url'):
                session, token = reset_token(token)
            else:
                logger.exception(e)
            continue
        except ReadTimeoutError:
            continue

        parse_response(page_content, keyword)


# 分析获取到的结果
def parse_response(response, keyword):
    for r in response:
        repo = r.repository
        t = {
            'sha': r.sha,
            'keyword': keyword,
            'html_url': r.html_url,
            'file_name': r.name,
            'repo_name': repo.name,
            'repo_url': repo.html_url,
            'user_avatar': repo.owner.avatar_url,
            'user_name': repo.owner.login,
            'user_url': repo.owner.html_url
        }
        if not RESULT.get('total', 0):
            RESULT['total'] = 0

        # 存储搜索出来的所有涉及到关键字的文件
        if not RESULT.get('data', False):
            RESULT['data'] = []

        if not RESULT.get('create_time', False):
            RESULT['create_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        RESULT['data'].append(t)
        RESULT['total'] = RESULT['total'] + 1
        RESULT['modify_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 保存搜索结果,可以改成数据库什么的也没啥问题
def save_result(operating):
    d = json.dumps(RESULT, sort_keys=True, indent=2, ensure_ascii=False, separators=(',', ':'))

    if operating == 'print':
        print('打印结果')
        print(d)
    else:
        try:
            with open(operating, 'w') as f:
                f.write(d)
            print('写入文件{}成功...'.format(operating))
        except Exception as e:
            print(e)
            print('写入文件{}失败'.format(operating))


if __name__ == '__main__':
    assert len(sys.argv) == 3, '参数错误, .py <print|file path> "<search>"'

    operating = sys.argv[1]
    search = sys.argv[2]
    if operating != 'print':
        with open(operating, 'w') as f:
            f.write("start...")

    search_by_keyword(search, 0)
    save_result(operating)

