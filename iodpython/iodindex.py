import requests
import json
import httplib
import time

proxyDict = { 
#              "http"  : http_proxy, 
 #             "https" : https_proxy, 
  #            "ftp"   : ftp_proxy
            }



class IODException(Exception):
    def __init__(self, rjson, code):
        # Call the base class constructor with the parameters it needs
        if "detail" in rjson:
        	Exception.__init__(self, "Response code {} - Error {} - {} \n Details: {}".format(code,rjson["error"],rjson["reason"], rjson["detail"]))
        else:
        	Exception.__init__(self, "Response code {} - Error {} - {} ]n Details: {} ".format(code,rjson["error"],rjson["reason"],rjson))

        # Now for your custom code...


class DocumentException(Exception):
	pass

class IODClient:
	root=""
	version= None
	apiversiondefault = None
	apikey= None
	proxy= None
	
	def __init__(self,url,apikey,version=1,apiversiondefault=1,proxy={}):
		if url.endswith("/"):
			url=url[:len(url)-1]
		self.root=url
		self.version=version
		self.apiversiondefault=1
		self.apikey=apikey
		self.proxy=proxy


	def createIndex(self,name,flavor="standard",index_fields="",parametric_fields=""):
		indexdata={"index":name,"flavor":flavor,"index_fields":index_fields,"parametric_fields":parametric_fields}
		r=self.post("createtextindex",indexdata)
		print r.text
		result=json.loads(r.text)
		print result
		try:
			return Index(self,result["index"])
		except:
			raise Exception(result["actions"]["detail"])


	def parseIndex(self,obj):
		return Index(self,obj["index"])

	def hasIndex(self,name):
		r=self.post('listindex',{'type':type, 'flavor':flavor }).text
		for i in json.loads(r)["index"]:
			if name.lower()==i["index"].lower():
				return True
		return False

	def getIndex(self,name):
		return Index(self,name)	

	def deleteIndex(self,name):
		indexdata={"index":name}
		r=self.post("deletetextindex",indexdata).text
		print "confirming"
		indexdata["confirm"]=json.loads(r)["confirm"]
		r=self.post("deletetextindex",indexdata).text

	def listIndexes(self,type="",flavor="standard"):
		result={}
		r=self.post('listindex',{'type':type, 'flavor':flavor }).text
		for index in json.loads(r)["index"]:

			result[index["index"]]=self.parseIndex(index)
		return result

	def post(self,handler,data={},files={},async=False, **args):
		data["apikey"]=self.apikey
		syncstr="sync"
		if async:
			syncstr="async"

		url = "%s/%s/api/%s/%s/v%s" % (self.root,self.version,syncstr,handler,self.apiversiondefault)

		return self.callAPI(url,data,files,async)



	def callAPI(self,url,data={},files={},async=False):
		response= requests.post(url,data=data, files=files, proxies=proxyDict)
		if response.status_code == 429:
			print "Throttled, Sleeping 2 seconds"
			print response.text
			time.sleep(2)
			print "Resuming"
			return self.post(handler,data,files)
		elif response.status_code != 200:
			raise IODException(response.json(),response.status_code)
		if async:
			return IODAsyncResponse(response,self)
		return IODResponse(response,self)




	def postasync(self,handler,data={},files={},**args):
		data["apikey"]=self.apikey
		url = "%s/%s/api/async/%s/v%s" % (self.root,self.version,handler,self.apiversiondefault)
		return requests.post(url,data=data, proxies=proxyDict)

	def getAsyncResult(self,jobid):
		data={}
		data["apikey"]=self.apikey
		url = "%s/%s/%s/%s" % (self.root,self.version,"job/status",jobid)
		return self.callAPI(url,data=data,async=False)


class IODResponse(object):

	def __init__(self,response,client):
		self.response=response
		self.client=client

	def json(self):
		return self.response.json()
		


class IODAsyncResponse(IODResponse):

	def __init__(self,response,client):

		super(IODAsyncResponse,self).__init__(response,client)
		self.jobID=self.response.json()["jobID"]

	def getResult(self):
		return self.client.getAsyncResult(self.jobID)



class Index:

	docs=[];
	client= None
	name=""
	def __init__(self,client,name):
		self.client=client
		self.name=name

	def size(self):
		return len(self.docs)

	def pushDoc(self, doc):
		self.docs.append(doc)

	def commit(self, async=False):
		docs={'documents':self.docs}
		data={'json':json.dumps(docs),'index':self.name }		
		r=self.client.post("addtotextindex",data=data,files={'fake':''},async=async)
		self.docs=[]
		return r

	def addDoc(self,doc):
		return self.addDocs([doc])

	def addDocs(self,docs):
		docs={'document':docs}
		data={'json':json.dumps(docs), 'index':self.name}
		r=self.client.post("addtotextindex",data=data,files={'fake':''},)
		return r

	def delete(self):
		self.client.deleteIndex(self.name)



