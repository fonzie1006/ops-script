import json
import time
import pymysql
from ldap3 import Connection
from ldap3 import MODIFY_ADD, MODIFY_REPLACE
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from email.mime.multipart import MIMEMultipart
from aliyunsdkcore import client
from aliyunsdkram.request.v20150501.CreateUserRequest import CreateUserRequest
from aliyunsdkram.request.v20150501.ListUsersRequest import ListUsersRequest
from aliyunsdkram.request.v20150501.GetUserRequest import GetUserRequest
from aliyunsdkram.request.v20150501.UpdateLoginProfileRequest import UpdateLoginProfileRequest
from aliyunsdkram.request.v20150501.CreateLoginProfileRequest import CreateLoginProfileRequest
from aliyunsdkram.request.v20150501.ListGroupsRequest import ListGroupsRequest
from aliyunsdkram.request.v20150501.GetGroupRequest import GetGroupRequest
from aliyunsdkram.request.v20150501.AddUserToGroupRequest import AddUserToGroupRequest
from aliyunsdkram.request.v20150501.DeleteUserRequest import DeleteUserRequest
from aliyunsdkram.request.v20150501.RemoveUserFromGroupRequest import RemoveUserFromGroupRequest
from aliyunsdkram.request.v20150501.ListGroupsForUserRequest import ListGroupsForUserRequest

AccessKey = ''
AccessSecret = ''
Region = 'cn-hangzhou'

MYSQL_HOST = ''
MYSQL_UER = ''
MYSQL_PASSWORD = ''
MYSQL_PORT = 3306
MYSQL_DB = ''

LDAP_HOST = '10.0.0.8'
LDAP_ADMIN = 'cn=admin,dc=xxxx,dc=com'
LDAP_PASS = ''
LDAP_DOMAIN = 'ou=users,dc=xxxxx,dc=com'

SMTP = 'smtp.exmail.qq.com'
SMTP_USERNAME = ''
SMTP_PASSWORD = ''
SMTP_POSTFIX = 'NoReply'

departments = {
    '商务部': 'business',
    '人力资源部': 'HR',
    '市场部': 'market',
    '运营部': 'operation',
    '研发/服务端': 'R&D/server',
    '研发/web': 'R&D/web',
    '研发/IOS': 'R&D/IOS',
    '研发/Android': 'R&D/Android',
    '研发/测试': 'R&D/test',
    '产品部/产品': 'PROD/product',
    '产品部/设计': 'PROD/Design',
    '财务部': 'finance',
    '福利宝': 'rich',
}


class AliyunRequest:
    def __init__(self, key, secret, region):
        self.key = key
        self.secret = secret
        self.region = region
        self.client = client.AcsClient(self.key, self.secret, self.region)

    # 查看所有用户
    def list_ram_user(self):
        r = ListUsersRequest()
        r.set_accept_format('json')
        is_truncated = True
        users = []

        while is_truncated:
            response = json.loads(self.client.do_action_with_exception(r))
            is_truncated = response['IsTruncated']

            user = response['Users']['User']
            users += user

        return users

    # 创建用户
    def create_ram_user(self, name, user, password, group, phone, email):
        r = CreateUserRequest()
        r.set_accept_format('json')
        r.set_DisplayName(name)
        r.set_UserName(user)
        r.set_MobilePhone(phone)
        r.set_Email(email)
        r.set_Comments(name)
        user_info = self.get_ram_user(user)
        if not user_info.get('User', {}).get('UserName', "") == user:

            flag = False
            try:
                response = json.loads(self.client.do_action_with_exception(r))
                response['User']['CreateDate']
                response['User']['UserName']
                flag = True
                print(user + ' 初始化成功')
            except Exception as e:
                print(e)
                return flag

            flag = self.create_ram_login_profile(user, password)
            if not flag:
                print('创建用户Web登录配置失败')
                return flag
            print(user + ' 开启用户web登录权限')

        if group:
            flag = self.add_ram_user_to_group(user, group)
            print('添加用户: {}({}) To 组: {}'.format(user, name, group))

        return flag

    # 获取用户信息
    def get_ram_user(self, username):
        r = GetUserRequest()
        r.set_accept_format('json')
        r.set_UserName(username)
        content = {}
        try:
            content = json.loads(self.client.do_action_with_exception(r))
        except Exception as e:
            print(e)
            print('用户: {}不存在'.format(username))

        return content

    # 更新用户信息
    def update_ram_login_profile(self, user, password):
        request = UpdateLoginProfileRequest()
        request.set_accept_format('json')
        request.set_MFABindRequired(False)
        request.set_PasswordResetRequired(False)
        request.set_Password(password)
        request.set_UserName(user)

        flag = False

        try:
            json.loads(self.client.do_action_with_exception(request))
            flag = True
        except Exception as e:
            print(e)

        return flag

    def create_ram_login_profile(self, user, password):
        request = CreateLoginProfileRequest()
        request.set_accept_format('json')
        request.set_UserName(user)
        request.set_Password(password)
        request.set_PasswordResetRequired(False)
        request.set_MFABindRequired(False)

        flag = False
        try:
            response = json.loads(self.client.do_action_with_exception(request))
            response['LoginProfile']['UserName']
            flag = True
        except Exception as e:
            print(e)

        return flag

    def list_ram_group(self):
        request = ListGroupsRequest()
        request.set_accept_format('json')

        content = []
        is_truncated = True

        while is_truncated:
            response = json.loads(self.client.do_action_with_exception(request))
            content += response['Groups']['Group']
            is_truncated = response['IsTruncated']
            request.set_Marker('Marker')

        return content

    def get_ram_group(self, group):
        request = GetGroupRequest()
        request.set_accept_format('json')
        request.set_GroupName(group)

        response = json.loads(self.client.do_action_with_exception(request))
        return response['Group']

    def add_ram_user_to_group(self, user, group):
        user_exist_group = self.user_exist_group(user, group)
        if user_exist_group:
            return True

        request = AddUserToGroupRequest()
        request.set_accept_format('json')
        request.set_UserName(user)
        request.set_GroupName(group)

        flag = False
        try:
            json.loads(self.client.do_action_with_exception(request))
            flag = True
        except Exception as e:
            print(e)
        return flag

    def user_exist_group(self, user, group):
        request = ListGroupsForUserRequest()
        request.set_accept_format('json')
        request.set_UserName(user)

        response = json.loads(self.client.do_action_with_exception(request))
        groups = response['Groups']['Group']
        flag = False

        for g in groups:
            if g['GroupName'] == group:
                flag = True
                return flag
        return flag

    def delete_ram_user(self, user):
        groups = self.list_group_ram_for_user(user)
        if len(groups) > 0:
            for g in groups:
                group = g['GroupName']
                self.remove_user_from_group(user, group)

        request = DeleteUserRequest()
        request.set_accept_format('json')
        request.set_UserName(user)

        try:
            self.client.do_action_with_exception(request)
            print('用户: {} 删除成功'.format(user))
        except Exception as e:
            print(e)
            print('用户: {} 删除失败'.format(user))

    def remove_user_from_group(self, user, group):
        request = RemoveUserFromGroupRequest()
        request.set_accept_format('json')
        request.set_GroupName(group)
        request.set_UserName(user)

        try:
            self.client.do_action_with_exception(request)
            print('用户: {} 从 {} 组中删除: 成功'.format(user, group))
        except Exception as e:
            print(e)
            print('用户: {} 从 {} 组中删除: 失败'.format(user, group))

    def list_group_ram_for_user(self, user):
        request = ListGroupsForUserRequest()
        request.set_accept_format('json')
        request.set_UserName(user)

        content = []

        response = json.loads(self.client.do_action_with_exception(request))
        content += response['Groups']['Group']

        return content


class XiaomaiLDAP(object):
    def __init__(self, host, user, password, port, db):
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.db = db

        self.con = pymysql.connect(self.host, self.user, self.password, self.db, self.port, charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)

    def user_is_exist(self, user):
        """
        判断用户是否存在
        """
        sql = 'SELECT * FROM xm_admin WHERE account="%s"' % user
        cur = self.con.cursor()
        try:
            cur.execute(sql)
            row = cur.fetchone()
        except Exception as e:
            print(e)
        finally:
            cur.close()

        flag = False
        if row and row.get('account', False) == user:
            flag = True

        return flag

    def list(self):
        cur = self.con.cursor()
        sql = """SELECT * FROM xm_admin;"""
        try:
            cur.execute(sql)
            rows = cur.fetchall()
        except Exception as e:
            print(e)
            print('查询失败')
        finally:
            cur.close()

        for row in rows:
            for k, v in row.items():
                print(str(k) + ':', str(v) + ' ', end='')
            print()

    def query_user(self, user):
        """
        判断用户是否存在
        """
        sql = 'SELECT * FROM xm_admin WHERE account="%s"' % user
        cur = self.con.cursor()

        row = {}
        try:
            cur.execute(sql)
            row = cur.fetchone()
        except Exception as e:
            print(e)
        finally:
            cur.close()

        cur.close()
        return row

    def add_user(self, user, name, password, phone, mail, employee_number, department):
        if self.user_is_exist(user):
            print("用户: {} 已经存在".format(user))
            return
        sql = """INSERT INTO xm_admin values('%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', null ,now(), now());""" % (
            str(time.time()).split(".")[0], user, name, password, phone, mail, employee_number, departments[department]
        )

        cur = self.con.cursor()
        try:
            cur.execute(sql)
            self.con.commit()
            print("添加用户: {} 成功".format(user))
        except Exception as e:
            print(e)
            self.con.rollback()
            print("添加用户: {} 失败".format(user))
        finally:
            cur.close()

    def del_user(self, user):
        sql = "DELETE FROM xm_admin WHERE account='%s'" % user
        cur = self.con.cursor()
        if self.user_is_exist(user):
            try:
                cur.execute(sql)
                self.con.commit()
                print('删除用户: {} 成功'.format(user))
            except Exception as e:
                print(e)
                self.con.rollback()
                print('删除用户: {} 失败'.format(user))
            finally:
                cur.close()

        else:
            print('用户{}不存在 {} 数据库中'.format(user, self.db))

    def update_user(self, user, name, oldpassword, newpassword, phone, mail, employee_number, department):
        if self.user_is_exist(user):
            add = ['account=' + user]
            if newpassword and oldpassword:
                u = self.query_user(user)
                if oldpassword == u['password']:
                    add.append('password=' + newpassword)
                else:
                    print('旧密码存在错误')
                    return

            if name:
                add.append('name=' + name)

            if phone:
                add.append('phone=' + phone)

            if mail:
                add.append('mail=' + mail)

            if employee_number:
                add.append('employee_number=' + employee_number)

            if department:
                add.append('department=' + departments[department])

            add = ",".join(add)

            sql = """UPDATE xm_admin SET {} WHERE account="{}";""".format(add, user)
            cur = self.con.cursor()
            try:
                row = cur.execute(sql)
                self.con.commit()
                if row > 1:
                    info = self.query_user(user)
                    print("xiaomaiLDAP用户信息:")
                    for k, v in info.iteritems():
                        print(k, v)
                    print('{}用户信息更新成功'.format(user))
            except Exception as e:
                print(e)
                print('{} 用户信息更新失败'.format(user))
            finally:
                cur.close()
        else:
            print('用户名: {} 不存在'.format(user))


class OpenLDAP(object):
    def __init__(self, host, admin, password, domain):
        self.host = host
        self.admin = admin
        self.password = password
        self.domain = domain

        self.con = Connection(host, admin, password, auto_bind=True)

    def user_is_exist(self, user):
        """
        判断用户是否存在OpenLDAP中
        """
        found = self.con.search('uid=' + user + ',' + self.domain, '(objectClass=person)', attributes=['cn', 'sn'])
        flag = False
        if found:
            print('用户: {} 已经存在OpenLDAP: {}'.format(user, self.host))
            flag = True

        return flag

    def query_user(self, user):
        """
        判断用户是否存在OpenLDAP中
        """
        found = self.con.search('uid=' + user + ',' + self.domain, '(objectClass=person)',
                                attributes=['uid', 'sn', 'entryUUID', 'userPassword', 'mail', 'mobile',
                                            'employeeNumber',
                                            'departmentNumber'])
        content = {}
        if found:
            print('用户: {} 已经存在OpenLDAP: {}'.format(user, self.host))
            for entry in self.con.entries:
                content['uid'] = entry['uid']
                content['sn'] = entry['sn']
                content['userPassword'] = entry['userPassword'].value.decode(),
                content['mail'] = entry['mail'].value,
                content['mobile'] = entry['mobile']
                content['employeeNumber'] = entry['employeeNumber']
                content['departmentNumber'] = entry['departmentNumber']
            return content

        return content

    def add_user(self, user, name, password, phone, mail, employee_number, department):
        added = self.con.add('uid=' + user + ',' + self.domain, 'inetOrgPerson',
                             {'userPassword': password, 'sn': name, 'cn': user, 'mail': mail})
        if added:
            self.con.modify('uid=' + user + ',' + self.domain, {'objectClass': [(MODIFY_ADD, ['person'])]})
            self.update_user(user, name, password, password, phone, mail, employee_number, department)
            print('OpenLDAP 添加用户: {} 成功'.format(user))
        else:
            print('OpenLDAP 添加用户: {} 失败'.format(user))

    def del_user(self, user):
        if self.user_is_exist(user):
            self.con.delete('uid=' + user + ',' + self.domain)
            print('用户: {} 已经从OpenLDAP中删除'.format(user))
        else:
            print('用户: {} 不存在于OpenLDAP'.format(user))

    def list_user(self):
        con = self.con
        con.search(self.domain, '(objectClass=person)',
                   attributes=['uid', 'sn', 'entryUUID', 'userPassword', 'mail', 'mobile', 'employeeNumber',
                               'departmentNumber'])
        for idx, entry in enumerate(con.entries):
            print('#ID:{} 用户名: {} - 中文名: {} - 密码: {} - 邮箱: {} - 手机: {} - 工号: {} - 部门: {}'.format(idx, entry['uid'],
                                                                                                 entry['sn'],
                                                                                                 entry['userPassword'],
                                                                                                 entry['mail'],
                                                                                                 entry['mobile'], entry[
                                                                                                     'employeeNumber'],
                                                                                                 entry[
                                                                                                     'departmentNumber']))

    def update_user(self, user, name, oldpassword, newpassword, phone, mail, employee_number, department):
        if newpassword and oldpassword:
            found = self.con.search('uid=' + user + ',' + self.domain, '(userPassword=' + oldpassword + ')',
                                    attributes=['cn', 'sn'])
            if found:
                self.con.modify('uid=' + user + ',' + self.domain, {'userPassword': [(MODIFY_REPLACE, [newpassword])]})
                print('用户: {} 密码更新成功'.format(user))
            else:
                print('用户名: {} 不存在'.format(user))
                return

        if name:
            self.con.modify('uid=' + user + ',' + self.domain, {'sn': [(MODIFY_REPLACE, [name])]})
            print('用户: {} 中文名更新成功'.format(user))

        if mail:
            self.con.modify('uid=' + user + ',' + self.domain, {'mail': [(MODIFY_REPLACE, [mail])]})
            print('用户: {} 邮箱信息更新成功'.format(user))

        if phone:
            self.con.modify('uid=' + user + ',' + self.domain, {'mobile': [(MODIFY_REPLACE, [phone])]})
            print('用户: {} 手机号码更新成功'.format(user))

        if employee_number:
            self.con.modify('uid=' + user + ',' + self.domain,
                            {'employeeNumber': [(MODIFY_REPLACE, [employee_number])]})
            print('用户: {} 编号信息更新成功'.format(user))

        if department:
            self.con.modify('uid=' + user + ',' + self.domain,
                            {'departmentNumber': [(MODIFY_REPLACE, ["%s" % str(departments[department])])]})
            print('用户: {} 部门信息更新成功'.format(user))


class EMail(object):
    def __init__(self, smtp, username, password, postfix, ssl=True, port=465):
        self.smtp = smtp
        self.username = username
        self.password = password
        self.postfix = postfix
        self.port = port
        self.smtp_ssl = ssl

        if ssl:
            self.server = smtplib.SMTP_SSL(host=smtp, port=self.port)
        else:
            self.server = smtplib.SMTP(host=smtp, port=self.port)

        self.server.login(self.username, self.password)

    def _format_email_addr(self, s):
        name, addr = parseaddr(s)
        return formataddr(Header(name, 'utf-8').encode(), addr)

    def send_text(self, text, subject, from_name, to_addr_list):
        msg = MIMEMultipart()
        msg.attach(MIMEText(text, 'plain', 'utf-8'))
        msg['From'] = 'fangqi'
        msg['To'] = ';'.join(to_addr_list)
        msg['Subject'] = Header(subject, 'utf-8').encode()

        return self._send(from_name, to_addr_list, msg)

    def send_html(self, html, subject, from_name, to_addr_list):
        msg = MIMEMultipart()
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        msg['From'] = 'fangqi'
        msg['To'] = ';'.join(to_addr_list)
        msg['Subject'] = Header(subject, 'utf-8').encode()

        return self._send(from_name, to_addr_list, msg)

    def _send(self, from_name, to_addr_list, msg):
        try:
            self.server.sendmail(from_name, to_addr_list, msg.as_string())
            print('邮件发送成功:')
            print('目标邮箱: \n%s' % '\n'.join(to_addr_list))
            return True
        except Exception as e:
            print(e)
            print('邮件发送失败')

        return False


# aliyunRequest = AliyunRequest(AccessKey, AccessSecret, Region)
# xiaomaildap = XiaomaiLDAP(MYSQL_HOST, MYSQL_UER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB)
# openldap = OpenLDAP(LDAP_HOST, LDAP_ADMIN, LDAP_PASS, LDAP_DOMAIN)
# email_client = EMail(SMTP, SMTP_USERNAME, SMTP_PASSWORD, SMTP_POSTFIX)

if __name__ == '__main__':
    pass

