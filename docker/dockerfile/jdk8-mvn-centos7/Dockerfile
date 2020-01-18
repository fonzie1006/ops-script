FROM centos:7.7.1908

RUN yum makecache && yum install -y wget && rm -rf /etc/yum.repos.d/*.repo && \
wget -O /etc/yum.repos.d/CentOS-Base.repo http://mirrors.aliyun.com/repo/Centos-7.repo && \
wget -O /etc/yum.repos.d/epel.repo http://mirrors.aliyun.com/repo/epel-7.repo && \
yum makecache && \
yum install -y net-tools nmap-ncat telnet net-tools jq curl openssl wget openssl-devel kde-l10n-Chinese glibc-common && \
yum clean all && \
rm -rf /var/cache/yum && \
rm -rf /anaconda-post.log && \
localedef -c -f UTF-8 -i zh_CN zh_CN.utf8 && \
rm -rf /etc/localtime && \
ln -s /usr/share/zoneinfo/Asia/Shanghai /etc/localtime


COPY apache-maven-3.6.3 /usr/local/maven
COPY jdk1.8.0_231 /usr/local/java
COPY local_policy.jar /usr/local/java/jre/lib/security
COPY US_export_policy.jar /usr/local/java/jre/lib/security

ENV LC_ALL zh_CN.utf8
ENV JAVA_HOME /usr/local/java
ENV JRE_HOME ${JAVA_HOME}/jre
ENV CLASSPATH .:${JAVA_HOME}/lib:${JRE_HOME}/lib
ENV PATH ${JAVA_HOME}/bin:$PATH
ENV M2_HOME /usr/local/maven
ENV PATH $PATH:$M2_HOME/bin

CMD ["java", "-version"]
