---
title: soap协议
type: categories
categories: 音视频协议
description: IPC开发
swiper_index: 1
abbrlink: 91d9ae79
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
---

# SOAP 构建模块
	1、一条 SOAP 消息就是一个普通的 XML 文档，包含下列元素：
	2、必需的 Envelope 元素，可把此 XML 文档标识为一条 SOAP 消息
	3、可选的 Header 元素，包含头部信息
	4、必需的 Body 元素，包含所有的调用和响应信息
	5、可选的 Fault 元素，提供有关在处理此消息所发生错误的信息
	所有以上的元素均被声明于针对 SOAP 封装的默认命名空间中
	http://www.w3.org/2001/12/soap-envelope
	以及针对 SOAP 编码和数据类型的默认命名空间：
	http://www.w3.org/2001/12/soap-encoding
# 语法规则
	这里是一些重要的语法规则：
	1、SOAP 消息必须用 XML 来编码
	2、SOAP 消息必须使用 SOAP Envelope 命名空间
	3、SOAP 消息必须使用 SOAP Encoding 命名空间
	4、SOAP 消息不能包含 DTD 引用
	5、SOAP 消息不能包含 XML 处理指令

#	SOAP 消息的基本结构

```
<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

<soap:Header>
  ...
  ...
</soap:Header>

<soap:Body>
  ...
  ...
  <soap:Fault>
    ...
    ...
  </soap:Fault>
</soap:Body>

</soap:Envelope>
```
# 强制使用的 SOAP 的 Envelope 元素是 SOAP 消息的根元素。

## SOAP Envelope 元素
	必需的 SOAP 的 Envelope 元素是 SOAP 消息的根元素。
	它可把 XML 文档定义为 SOAP 消息。

	请注意 xmlns:soap 命名空间的使用。它的值应当始终是：
	http://www.w3.org/2001/12/soap-envelope
	并且它可把封装定义为 SOAP 封装：

```
<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">
  ...
  Message information goes here
  ...
</soap:Envelope>
```
## xmlns:soap 命名空间
	SOAP 消息必须拥有与命名空间 "http://www.w3.org/2001/12/soap-envelope" 
	相关联的一个 Envelope 元素。
	如果使用了不同的命名空间，应用程序会发生错误，并抛弃此消息。
![](https://img-blog.csdnimg.cn/5817bb45938c48408a1212733f0d2939.png)
![](https://img-blog.csdnimg.cn/dd85b1ac04f244ba815b95d4e74ce8f2.png)			

	否则可能导致命名空间无法解析导致错误

## encodingStyle 属性
	SOAP 的 encodingStyle 属性用于定义在文档中使用的数据类型。
	此属性可出现在任何SOAP元素中，并会被应用到元素的内容及元素的所有子元素上。
	SOAP 消息没有默认的编码方式。

语法

```
soap:encodingStyle="URI"
实例
<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">
...
Message information goes here
...
</soap:Envelope>
```
## 可选的 SOAP Header 元素包含头部信息。

		SOAP Header 元素
	可选的SOAP Header元素可包含有关 SOAP 消息的应用程序专用信
	息（比如认证、支付等）。如果 Header 元素被提供，则它必须是 Envelope 
	元素的第一个子元素。

```
注释：所有 Header 元素的直接子元素必须是合格的命名空间。

<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

<soap:Header>
<m:Trans
xmlns:m="http://www.w3school.com.cn/transaction/"
soap:mustUnderstand="1">234</m:Trans>
</soap:Header>

...
...

</soap:Envelope>
```

	上面的例子包含了一个带有一个 "Trans" 元素的头部，它的值是 234，
	此元素的 "mustUnderstand" 属性的值是 "1"。

	SOAP 在默认的命名空间中 ("http://www.w3.org/2001/12/soap-envelope") 定义了三个属性。
	这三个属性是：actor、mustUnderstand 以及encodingStyle。
	这些被定义在SOAP头部的属性定义了容器如何对SOAP消息进行处理。

![](https://img-blog.csdnimg.cn/c2507fcd67ef414692e15ed3d2e80102.png)

## actor 属性
	通过沿着消息路径经过不同的端点，SOAP 消息可从某个发送者传播到某个接收者。
	并非 SOAP 消息的所有部分均打算传送到 SOAP 消息的最终端点，不过，
	另一个方面，也许打算传送给消息路径上的一个或多个端点。
	SOAP的actor 属性可被用于将 Header 元素寻址到一个特定的端点。

	soap 消息在发往最终目标的途中可能会经过许多中间节点，这些中间节点既能接收又能转发soap消息。
	并不是soap消息的所有部分都发给最终目标节点，其中一 		部分可能由消息路径中的中间节点进行处理。
	actor属性就是用来指定soap报头条目所定向的节点。它所属的命名空间 为"http://www.w3.org/2001/12/soap-envelope"，
	在使用时必须使用命名空间对其进行限定。actor属性值的类 型为anyURI，它指定了一个soap节点所扮演的角色。
	省略actor属性的报头条目隐含地定向到最终soap接收者，属性值为空等效于完全省略该属 性。
	如果报头条目中的soap actor与某个soap节点的角色匹配(没有actor属性时，与最终接收者匹配)，
	就认为这个报头条目定向到这个soap节点上。 在 soap消息处理过程中，soap节点起到一个或多个actor的作用，
	其中每一个都通过URI指出。每一个soap节点都必须完 成"http://www.w3.org/2001/12/soap-envelope/actor/next"
	所指定的actor的作用，并且可以完成 其他0个或多个actor的作用。
```
语法
soap:actor="URI" 
实例
<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

<soap:Header>
<m:Trans
xmlns:m="http://www.w3school.com.cn/transaction/"
soap:actor="http://www.w3school.com.cn/appml/">
234
</m:Trans>
</soap:Header>

...
...

</soap:Envelope>
```
## mustUnderstand 属性
	SOAP 的 mustUnderstand 属性可用于标识标题项对于要对其进行处理的接收者来说是强制的还是可选的。

	假如您向 Header 元素的某个子元素添加了 "mustUnderstand="1"，
	则它可指示处理此头部的接收者必须认可此元素。
	假如此接收者无法认可此元素，则在处理此头部时必须失效。

```
语法
soap:mustUnderstand="0|1"
实例
<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

<soap:Header>
<m:Trans
xmlns:m="http://www.w3school.com.cn/transaction/"
soap:mustUnderstand="1">
234
</m:Trans>
</soap:Header>

...
...

</soap:Envelope>
```
	之前工作曾遇到这个问题：
![](https://img-blog.csdnimg.cn/bdc737f10b284dd783f7ebd0a8dcc19d.png)
	
	不过这里主要是空间名字不正确。

## SOAP Body 元素
		必需的 SOAP Body 元素可包含打算传送到消息最终端点的
	实际 SOAP 消息。

	SOAP Body 元素的直接子元素可以是合格的命名空间。
	SOAP 在默认的命名空间中("http://www.w3.org/2001/12/soap-envelope")
	定义了 Body 元素内部的一个元素。即 SOAP 的 Fault 元素，
	用于指示错误消息。

```
<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

<soap:Body>
   <m:GetPrice xmlns:m="http://www.w3school.com.cn/prices">
      <m:Item>Apples</m:Item>
   </m:GetPrice>
</soap:Body>

</soap:Envelope>
```

	上面的例子请求苹果的价格。请注意，
	上面的 m:GetPrice 和 Item 元素是应用程序专用的元素。
	它们并不是 SOAP 标准的一部分。

	而一个 SOAP 响应应该类似这样：

```
<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

<soap:Body>
   <m:GetPriceResponse xmlns:m="http://www.w3school.com.cn/prices">
      <m:Price>1.90</m:Price>
   </m:GetPriceResponse>
</soap:Body>

</soap:Envelope>
```
## SOAP Fault 元素
	可选的 SOAP Fault 元素用于指示错误消息。

	如果已提供了 Fault 元素，则它必须是 Body 元素的子元素。
	在一条 SOAP 消息中，Fault 元素只能出现一次。

SOAP 的 Fault 元素拥有下列子元素：

```
子元素	   		    	描述
<faultcode>  			供识别故障的代码
<faultstring>			可供人阅读的有关故障的说明
<faultactor>			有关是谁引发故障的信息
<detail>				存留涉及 Body 元素的应用程序专用错误信息

```
## SOAP Fault 代码
	在下面定义的 faultcode 值必须用于描述错误时的 faultcode 元素中：

```
错误														描述
VersionMismatch			SOAP Envelope 元素的无效命名空间被发现
MustUnderstand			Header 元素的一个直接子元素（带有设置为 "1" 的 mustUnderstand 属性）无法被理解。
Client					消息被不正确地构成，或包含了不正确的信息。
Server					服务器有问题，因此无法处理进行下去。
```
# SOAP HTTP Binding
## HTTP 协议
	HTTP 在 TCP/IP 之上进行通信。
	HTTP 客户机使用 TCP 连接到 HTTP 服务器。
	在建立连接之后，客户机可向服务器发送 HTTP 请求消息：

```
POST /item HTTP/1.1
Host: 189.123.345.239
Content-Type: text/plain
Content-Length: 200
```

	随后服务器会处理此请求，然后向客户机发送一个 HTTP 响应。
	此响应包含了可指示请求状态的状态代码：

```
200 OK
Content-Type: text/plain
Content-Length: 200
```

	在上面的例子中，服务器返回了一个 200 的状态代码。
	这是 HTTP 的标准成功代码。

	假如服务器无法对请求进行解码，
	它可能会返回类似这样的信息：

```
400 Bad Request
Content-Length: 0
```

	SOAP HTTP Binding
	SOAP 方法指的是遵守 SOAP 编码规则的 HTTP 请求/响应。

	HTTP + XML = SOAP

	SOAP 请求可能是 HTTP POST 或 HTTP GET 请求。

	HTTP POST 请求规定至少两个 HTTP 头：Content-Type 和
	 Content-Length。

## Content-Type
	SOAP 的请求和响应的 Content-Type 头可定义消息的 MIME 类型，
	以及用于请求或响应的 XML 主体的字符编码（可选）。

语法

```
Content-Type: MIMEType; charset=character-encoding 
```

例子

```
POST /item HTTP/1.1
Content-Type: application/soap+xml; charset=utf-8
```

## Content-Length
	SOAP 的请求和响应的 Content-Length 头规定请求或响应主体的字节数。

语法

```
Content-Length: bytes 
```

例子

```
POST /item HTTP/1.1
Content-Type: application/soap+xml; charset=utf-8
Content-Length: 250
```
# 一个 SOAP 实例
	在下面的例子中，一个 GetStockPrice 请求被发送到了服务器。
	此请求有一个 StockName 参数，而在响应中则会返回一个 Price 参数。	
	此功能的命名空间被定义在此地址中： "http://www.example.org/stock"

```
SOAP 请求：
POST /InStock HTTP/1.1
Host: www.example.org
Content-Type: application/soap+xml; charset=utf-8
Content-Length: nnn

<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

  <soap:Body xmlns:m="http://www.example.org/stock">
    <m:GetStockPrice>
      <m:StockName>IBM</m:StockName>
    </m:GetStockPrice>
  </soap:Body>
  
</soap:Envelope>
```

```
SOAP 响应：
HTTP/1.1 200 OK
Content-Type: application/soap+xml; charset=utf-8
Content-Length: nnn

<?xml version="1.0"?>
<soap:Envelope
xmlns:soap="http://www.w3.org/2001/12/soap-envelope"
soap:encodingStyle="http://www.w3.org/2001/12/soap-encoding">

  <soap:Body xmlns:m="http://www.example.org/stock">
    <m:GetStockPriceResponse>
      <m:Price>34.5</m:Price>
    </m:GetStockPriceResponse>
  </soap:Body>
  
</soap:Envelope>
```




`目前onvif代码主流生成方式gsoap`  
也有自己写的、还有的是sdk方式。  
本篇完结