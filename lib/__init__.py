from datetime import date, datetime
import simplejson as json

# Dump object to JSON
def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))

def jsonDump(obj):
  return json.dumps(obj, default = json_serial )

# Get or add new database instance
def getOrAddNew(model,session,**kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance