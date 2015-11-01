**Note 1:** use `iod` [branch](https://github.com/HP-Haven-OnDemand/iod-python/tree/iod) for older compatibility syntax.

**Note 2:** compatible with Python 2.X

# Python Client Library for Haven OnDemand
Official Python client library to help with calling Haven OnDemand APIs [http://havenondemand.com](http://havenondemand.com).

## What is Haven OnDemand?
Haven OnDemand is a set of over 70 APIs for handling all sorts of unstructured data. Here are just some of our APIs' capabilities:
* Speech to text
* OCR
* Text extraction
* Indexing documents
* Smart search
* Language identification
* Concept extraction
* Sentiment analysis
* Web crawlers
* Machine learning

For a full list of all the APIs and to try them out, check out https://www.havenondemand.com/developer/apis


### Installation
To install
```
pip install havenondemand
```
To install the latest version from this github repo:
```
pip install git+https://github.com/HP-Haven-OnDemand/havenondemand-python
```


### Importing

```
from havenondemand.hodindex import HODClient
```

###Initializing the client

```
client = HODClient("http://api.havenondemand.com/",
                            "myapikey")
```

All that is needed to initialize the client is an apikey and the url of the API.

**Proxies**
```
http_proxy  = "ip:port"
proxyDict = {  "http"  : http_proxy }
client = HODClient("http://api.havenondemand.com/",
                            "myapikey",proxy=proxyDict)
```

The `proxy` parameter takes a dictionary of proxy urls. It will only use the one for the protocol chosen in the api url , *http* or *https*

### Sending requests

```
r=client.post(handler,{'param1':'value1','param2':'value2'})
r=client.post('analyzesentiment',{'text':'I like cats'})
```
The client's *post* method takes the API path that you're sending your request to as well as an object containing the parameters you want to send to the api. You do not need to send your API key each time as the client will handle that automatically.

###Posting files

```python
r=client.post('ocrdocument',files={'file':open('myimg.jpg','rb')})
```
Sending files is just as easy.

```python
r=client.post('ocrdocument',{'mode':'photo'},files={'file':open('myimg.jpg','rb')})
r=client.post('ocrdocument',data={'mode':'photo'},files={'file':open('myimg.jpg','rb')})
```
Any extra parameters should be added in the same way as regular calls, or in the data parameter.

###Parsing the output

```python
myjson=r.json()
```

The object returned is a response object from the python [requests library](http://docs.python-requests.org/en/latest/) and can easily be turned to json.

```python
docs=myjson["documents"]
for doc in docs:
    #do stuff
```

###Indexing

**Creating an index**

```

client.createIndex('myindex')

```

An Index object can easily be created

**Fetching indexes/an index**

```python
index = client.getIndex('myindex')
```
The getIndex call will return an hodindex Index object but will not check for existence.

```python
indexes = client.listIndexes()
indexex.get('myindex',client.createIndex('myindex'))
```

Here we first check the list of our indexes and return a newly created index if the index does not already exist

**Deleting an index**

```python
index.delete()
client.deleteIndex('myindex')
```
An index can be deleted in two equivalent ways

**Indexing documents**

```python
doc1={'reference':'doc1','title':'title1','content':'this is my content'}
doc2={'reference':'doc2','title':'title2','content':'this is another content'}
```
Documents can be created as regular python objects

```
index.addDoc(doc1)
index.addDocs([doc1,doc2])
```
They can be added directly one at a time or in a batch.

```
for doc in docs:
  index.pushDoc(doc)
index.commit()
```

An alternative to *addDocs* and easy way to keep batch documents is to use the pushDoc method, the index will keep in memory a list of the documents it needs to index.

```
if index.countDocs()>10:
  index.commit()
```

It makes it easy to batch together groups of documents.



### Asynchronous request

For each call the Async parameter can be set to true to send an asynchronous request.

```
r=client.post('analyzesentiment',{'text':'I like cats'},async=True)
print r.json()

r=index.commit(async=True)
```
