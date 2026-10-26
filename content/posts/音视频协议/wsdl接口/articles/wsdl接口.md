---
title: wsdl接口
type: categories
categories: 音视频协议
description: IPC开发
swiper_index: 1
abbrlink: ce15fa91
cover: "../images/封面.png"
date: 2022-09-29 00:00:00
---



# wsdl文档
	WSDL 文档仅仅是一个简单的 XML 文档。
	它包含一系列描述某个 web service 的定义。

## WSDL 文档结构
	WSDL 文档是利用这些主要的元素来描述某个 web service 的：

```
元素				定义
<portType>			web service 执行的操作
<message>			web service 使用的消息
<types>				web service 使用的数据类型
<binding>			web service 使用的通信协议
```

	一个 WSDL 文档的主要结构是类似这样的：

```
<definitions>

<types>
   definition of types........
</types>

<message>
   definition of a message....
</message>

<portType>
   definition of a port.......
</portType>

<binding>
   definition of a binding....
</binding>

</definitions>
```

	WSDL 文档可包含其它的元素，比如 extension 元素，
	以及一个 service 元素，此元素可把若干个 web services 
	的定义组合在一个单一的 WSDL 文档中。

## WSDL 端口
	<portType> 元素是最重要的 WSDL 元素。
	它可描述一个 web service、可被执行的操作，以及相关的消息。
	可以把 <portType> 元素比作传统编程语言中的一个函数库
	（或一个模块、或一个类）

## WSDL 消息
	<message> 元素定义一个操作的数据元素。
	每个消息均由一个或多个部件组成。
	可以把这些部件比作传统编程语言中一个函数调用的参数。
## WSDL types
	<types> 元素定义 web service 使用的数据类型。
	为了最大程度的平台中立性，WSDL 使用 XML Schema 语法来定义数据类型。
## WSDL Bindings
	<binding> 元素为每个端口定义消息格式和协议细节。
## WSDL 实例
	这是某个 WSDL 文档的简化的片段：

```
<message name="getTermRequest">
   <part name="term" type="xs:string"/>
</message>

<message name="getTermResponse">
   <part name="value" type="xs:string"/>
</message>

<portType name="glossaryTerms">
  <operation name="getTerm">
        <input message="getTermRequest"/>
        <output message="getTermResponse"/>
  </operation>
</portType>
```

	在这个例子中，<portType> 元素把 "glossaryTerms" 定义为某个端口的名称，
	把 "getTerm" 定义为某个操作的名称。
	操作 "getTerm" 拥有一个名为 "getTermRequest" 的输入消息，
	以及一个名为 "getTermResponse" 的输出消息。
	<message> 元素可定义每个消息的部件，以及相关联的数据类型。
	对比传统的编程，glossaryTerms 是一个函数库，
	而 "g etTerm" 是带有输入参数 "getTermRequest" 和
	返回参数 getTermResponse 的一个函数。

# WSDL 端口可描述由某个 web service 提供的界面（合法操作）。

## WSDL 端口
	<portType> 元素是最重要的 WSDL 元素。
	它可描述一个 web service、可被执行的操作，以及相关的消息。
	端口定义了指向某个 web service 的连接点。可以把该元素比作传
	统编程语言中的一个函数库（或一个模块、或一个类），而把每个
	操作比作传统编程语言中的一个函数。

## 操作类型
	请求-响应是最普通的操作类型，不过 WSDL 定义了四种类型：

```
类型					定义
One-way				此操作可接受消息，但不会返回响应。
Request-response	此操作可接受一个请求并会返回一个响应
Solicit-response	此操作可发送一个请求，并会等待一个响应。
Notification		此操作可发送一条消息，但不会等待响应。
```
## One-Way 操作
一个 one-way 操作的例子：

```
<message name="newTermValues">
   <part name="term" type="xs:string"/>
   <part name="value" type="xs:string"/>
</message>

<portType name="glossaryTerms">
   <operation name="setTerm">
      <input name="newTerm" message="newTermValues"/>
   </operation>
</portType >
```

	在这个例子中，端口 "glossaryTerms" 定义了一
	个名为 "setTerm" 的 one-way 操作。
	这个 "setTerm" 操作可接受新术语表项目消息的输入，
	这些消息使用一条名为 "newTermValues" 的消息，
	此消息带有输入参数 "term" 和 "value"。
	不过，没有为这个操作定义任何输出。

## Request-Response 操作
	一个 request-response 操作的例子：

```
<message name="getTermRequest">
   <part name="term" type="xs:string"/>
</message>

<message name="getTermResponse">
   <part name="value" type="xs:string"/>
</message>

<portType name="glossaryTerms">
  <operation name="getTerm">
    <input message="getTermRequest"/>
    <output message="getTermResponse"/>
  </operation>
</portType>
```

	在这个例子中，端口 "glossaryTerms" 定义了一个
	名为 "getTerm" 的 request-response 操作。
	"getTerm" 操作会请求一个名为 "getTermRequest" 的输入消息，
	此消息带有一个名为 "term" 的参数，并将返回一个
	名为 "getTermResponse" 的输出消息，
	此消息带有一个名为 "value" 的参数。

## 绑定到 SOAP
	一个 请求 - 响应 操作的例子：

```
<message name="getTermRequest">
   <part name="term" type="xs:string" />
</message>

<message name="getTermResponse">
   <part name="value" type="xs:string" />
</message>

<portType name="glossaryTerms">
  <operation name="getTerm">
      <input message="getTermRequest" />
      <output message="getTermResponse" />
  </operation>
</portType>

<binding type="glossaryTerms" name="b1">
<soap:binding style="document"
transport="http://schemas.xmlsoap.org/soap/http" />
  <operation>
    <soap:operation
     soapAction="http://example.com/getTerm" />
    <input>
      <soap:body use="literal" />
    </input>
    <output>
      <soap:body use="literal" />
    </output>
  </operation>
</binding>
```

### binding 元素有两个属性 - name 属性和 type 属性
	name 属性定义 binding 的名称，而 type 属性指向用于 binding 的端口，
	在这个例子中是 "glossaryTerms" 端口。
### soap:binding 元素有两个属性 - style 属性和 transport 属性。
	style 属性可取值 "rpc" 或 "document"。在这个例子中我们使用 document。
	transport 属性定义了要使用的 SOAP 协议。在这个例子中我们使用 HTTP。
### operation 元素定义了每个端口提供的操作符。
	对于每个操作，相应的 SOAP 行为都需要被定义。
	同时您必须如何对输入和输出进行编码。在这个例子中我们使用了 "literal"。

# w3c工作草案 
```
<wsdl:definitions name="nmtoken"? targetNamespace="uri">

    <import namespace="uri" location="uri"/> *
	
    <wsdl:documentation .... /> ?

    <wsdl:types> ?
        <wsdl:documentation .... /> ?
        <xsd:schema .... /> *
    </wsdl:types>

    <wsdl:message name="ncname"> *
        <wsdl:documentation .... /> ?
        <part name="ncname" element="qname"? type="qname"?/> *
    </wsdl:message>

    <wsdl:portType name="ncname"> *
        <wsdl:documentation .... /> ?
        <wsdl:operation name="ncname"> *
            <wsdl:documentation .... /> ?
            <wsdl:input message="qname"> ?
                <wsdl:documentation .... /> ?
            </wsdl:input>
            <wsdl:output message="qname"> ?
                <wsdl:documentation .... /> ?
            </wsdl:output>
            <wsdl:fault name="ncname" message="qname"> *
                <wsdl:documentation .... /> ?
            </wsdl:fault>
        </wsdl:operation>
    </wsdl:portType>

    <wsdl:serviceType name="ncname"> *
        <wsdl:portType name="qname"/> +
    </wsdl:serviceType>

    <wsdl:binding name="ncname" type="qname"> *
        <wsdl:documentation .... /> ?
        <-- binding details --> *
        <wsdl:operation name="ncname"> *
            <wsdl:documentation .... /> ?
            <-- binding details --> *
            <wsdl:input> ?
                <wsdl:documentation .... /> ?
                <-- binding details -->
            </wsdl:input>
            <wsdl:output> ?
                <wsdl:documentation .... /> ?
                <-- binding details --> *
            </wsdl:output>
            <wsdl:fault name="ncname"> *
                <wsdl:documentation .... /> ?
                <-- binding details --> *
            </wsdl:fault>
        </wsdl:operation>
    </wsdl:binding>

    <wsdl:service name="ncname" serviceType="qname"> *
        <wsdl:documentation .... /> ?
        <wsdl:port name="ncname" binding="qname"> *
            <wsdl:documentation .... /> ?
            <-- address details -->
        </wsdl:port>
    </wsdl:service>

</wsdl:definitions>
```
