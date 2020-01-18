### 说明

制作一个可以满足编译java的镜像,解决微信解码问题,不足之处就是在编译之前需要自己先下载好对应的jdk和maven,主要是觉得国内的网络环境不太友好，加上oracle现在下载JDK需要登录.

### 下载地址
* [maven](https://maven.apache.org/download.cgi)
* [JDK](https://www.oracle.com/technetwork/java/javase/archive-139210.html)
* [dockerhub成品](https://hub.docker.com/r/vperson/build-java)

### 使用方法
解压maven和jdk,Dockerfile中使用的是COPY不是ADD.
然后构建你的镜像:
```shell
docker build -t java-maven .
```

构建成功后可以使用如下命令测试:
```shell
# docker run --rm java-maven java -version
java version "1.8.0_231"
Java(TM) SE Runtime Environment (build 1.8.0_231-b11)
Java HotSpot(TM) 64-Bit Server VM (build 25.231-b11, mixed mode)
```

```shell
# docker run --rm java-maven mvn -version
Apache Maven 3.6.3 (cecedd343002696d0abb50b32b541b8a6ba2883f)
Maven home: /usr/local/maven
Java version: 1.8.0_231, vendor: Oracle Corporation, runtime: /usr/local/java/jre
Default locale: zh_CN, platform encoding: UTF-8
OS name: "linux", version: "4.4.176-1.el7.elrepo.x86_64", arch: "amd64", family: "unix"
```

### 使用Dockerhub镜像
```shell
docker pull vperson/build-java
```
