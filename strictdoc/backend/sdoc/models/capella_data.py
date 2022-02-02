import json
import xml.sax.saxutils as saxutils

class CapellaData:
	def __init__(self, uuid, name, long_name, doc_url):
		self.uuid = uuid
		self.name = name
		self.long_name = long_name
		self.doc_url = doc_url

	@staticmethod
	def encode_req(creq, cdocpath):	
		# TODO: maybe a json format is the better solution
		#return str(creq.uuid) + ";" + str(creq.long_name) + ";" + str(creq.name) + ";" + cdocpath    
		cd = CapellaData(creq.uuid, creq.name, creq.long_name, cdocpath)
		out = json.dumps(cd.__dict__)
		return CapellaData.escape(out)
		

	@staticmethod
	def decode_req(json_in):
		if not isinstance(json_in, str):
			raise ValueError("input must be a string")
		if json_in != "":
			jsin = CapellaData.unescape(json_in)
			jss = json.loads(jsin)
			return CapellaData(**jss)
		else:
			return None

	@staticmethod
	def encode_allocs(creq, ignore_req=False):
		# TODO: maybe a json format is the better solution
		# https://pythonexamples.org/convert-python-class-object-to-json/        
		clst = []
		for alloc in creq.requirements:		
			docpath = get_capella_xhtmldoc_path(alloc.uuid)
			if hasattr(alloc,"long_name") and not ignore_req:
				# if the capella object has a long_name it is very likely an imported requirement!
				cd = CapellaData(alloc.uuid, alloc.name, alloc.long_name, docpath)
			else:
				cd = CapellaData(alloc.uuid, alloc.name, None, docpath)
			clst.append(cd)
		out = json.dumps([ob.__dict__ for ob in clst])
		return CapellaData.escape(out)
		
	
	@staticmethod
	def decode_allocs(json_in):
		if not isinstance(json_in, str):
			raise ValueError("input must be a string")
		if json_in != "":
			jsin = CapellaData.unescape(json_in)
			jss = json.loads(jsin)
			out = []
			for js in jss:
				 out.append(CapellaData(**js))
			return out
		else:
			return []


	escape_table = {
			"&": "&amp;",
			'"': "&quot;",
			"'": "&apos;",
			">": "&gt;",
			"<": "&lt;",
			}
	unescape_table = {v:k for k, v in escape_table.items()}

	@staticmethod
	def escape(text):
		return saxutils.escape(text, CapellaData.escape_table)
	@staticmethod
	def unescape(text):
		return saxutils.unescape(text, CapellaData.unescape_table)