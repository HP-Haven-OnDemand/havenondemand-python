import requests
import json
import httplib
import time

proxyDict = {
#				  "http"  : http_proxy,
 #				 "https" : https_proxy,
  #				"ftp"   : ftp_proxy
				}



class HODException(Exception):
    def __init__(self, rjson, code):
		  # Call the base class constructor with the parameters it needs
		  if "detail" in rjson:
		  	Exception.__init__(self, "Response code {} - Error {} - {} \n Details: {}".format(code,rjson["error"],rjson["reason"], rjson["detail"]))
		  else:
		  	Exception.__init__(self, "Response code {} - Error {} - {} ]n Details: {} ".format(code,rjson["error"],rjson["reason"],rjson))

		  # Now for your custom code...


class DocumentException(Exception):
	pass

class HODClient:
	root=""
	version= None
	apiversiondefault = None
	apikey= None
	proxy= None

	def __init__(self,apikey,apiversiondefault=1,version=1,proxy={}):
		if apikey=='http://api.havenondemand.com' or apikey=='http://api.havenondemand.com/' or apikey=='https://api.havenondemand.com' or apikey=='https://api.havenondemand.com/':
			raise DeprecationWarning("Using an outdated wrapper constructor method. No need to include API URL.Include as such:\n client = HODClient(API_KEY)")
		self.root="https://api.havenondemand.com"
		self.version=version
		self.apiversiondefault=apiversiondefault
		self.apikey=apikey
		self.proxy=proxy


	def createIndex(self,name,flavor="standard",index_fields="",parametric_fields=""):
		indexdata={"index":name,"flavor":flavor,"index_fields":index_fields,"parametric_fields":parametric_fields}
		r=self.post("createtextindex",indexdata)
		result=r.json()
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
		r=self.post("deletetextindex",indexdata).json()
		print "confirming"
		indexdata["confirm"]=r["confirm"]
		r=self.post("deletetextindex",indexdata).json()

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
   # print response
    #print "ERROR"

		if response.status_code == 429:
			print "Throttled, Sleeping 2 seconds"
			print response.text
			time.sleep(2)
			print "Resuming"
			return self.post(handler,data,files)
		elif response.status_code != 200:
			raise HODException(response,response.status_code)
		if async:
			return HODAsyncResponse(response,self)
		return HODResponse(response,self)




	def postasync(self,handler,data={},files={},**args):
		data["apikey"]=self.apikey
		url = "%s/%s/api/async/%s/v%s" % (self.root,self.version,handler,self.apiversiondefault)
		return requests.post(url,data=data, proxies=proxyDict)

	def getAsyncResult(self,jobid):
		data={}
		data["apikey"]=self.apikey
		url = "%s/%s/%s/%s" % (self.root,self.version,"job/status",jobid)
		return self.callAPI(url,data=data,async=False)


class HODResponse(object):

	def __init__(self,response,client):
		self.response=response
		self.client=client

	def json(self):
		return self.response.json()



class HODAsyncResponse(HODResponse):

	def __init__(self,response,client):

		super(HODAsyncResponse,self).__init__(response,client)
		self.jobID=self.response.json()["jobID"]

	def getResult(self):
		return self.client.getAsyncResult(self.jobID)



class Index:

	client= None
	name=""
	def __init__(self,client,name):
		self.client=client
		self.name=name
		self.docs=[]

	def size(self):
		return len(self.docs)

	def pushDoc(self, doc):
		self.docs.append(doc)

	def pushDocs(self,docs):
		self.docs=self.docs+docs

	def commit(self, async=False):
		docs={'documents':self.docs}
		data={'json':json.dumps(docs),'index':self.name }
		r=self.client.post("addtotextindex",data=data,files={'fake':''},async=async)
		self.docs=[]
		return r

	def addDoc(self,doc,async=False):
		return self.addDocs([doc],async=async)

	def addDocs(self,docs,async=False):
		docs={'document':docs}
		data={'json':json.dumps(docs), 'index':self.name}
		r=self.client.post("addtotextindex",data=data,files={'fake':''},async=async)
		return r

	def delete(self):
		self.client.deleteIndex(self.name)
