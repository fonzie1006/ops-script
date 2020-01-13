

### email_ldap_ram.py

[源代码](/python/api/email_ldap_ram.py)

#### 依赖包
```shell
pip install aliyun-python-sdk-ram
```

#### 如何使用

你可以选择在[email_ldap_ram.py](/python/api/email_ldap_ram.py)中修改以下的变量:
```python
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
```

```shell
aliyunRequest = AliyunRequest(AccessKey, AccessSecret, Region)
xiaomaildap = XiaomaiLDAP(MYSQL_HOST, MYSQL_UER, MYSQL_PASSWORD, MYSQL_PORT, MYSQL_DB)
openldap = OpenLDAP(LDAP_HOST, LDAP_ADMIN, LDAP_PASS, LDAP_DOMAIN)
email_client = EMail(SMTP, SMTP_USERNAME, SMTP_PASSWORD, SMTP_POSTFIX)
```
