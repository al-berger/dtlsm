"""******************************************************************
*    Module:            modules
*    
*    File name:        dtl.py
*
*    Created:        2015-12-15 16:01:26
*
*    Abstract:        Data utilities
*
*    Author:            Albert Berger [ alberger@gmail.com ].
*        
*******************************************************************"""

__lastedited__ = "2015-12-19 23:42:58"


class Jsonator:
    '''Convert native and user objects to and from JSON format.'''    
    class JsonBytesWrapper:
        def __init__(self, s, name):
            self.s = s
            self.clsname = name

    def __init__(self, fromModules=None):
        self.classes = {}
        if fromModules:
            import inspect, importlib
            for modname in fromModules:
                mod = importlib.import_module( modname )
                for cl in inspect.getmembers(mod, inspect.isclass):
                    if cl[1].__module__ != modname:
                        continue
                    if cl[0] in self.classes:
                        raise IKException( ErrorCode.objectAlreadyExists, cl[0])
                    self.classes[cl[0]] = cl[1]

    def tojson(self, obj):
        '''Hook for json.dump()'''
        onam = obj.__class__.__name__ 
        m = { 'clsname': onam }

        if onam in ("bytes", "bytearray"):
            import base64
            s = base64.b85encode( obj ).decode("ascii")
            o = Jsonator.JsonBytesWrapper( s, onam )
            return o

        m.update(obj.__dict__)
        return m
    
    def fromjson( self, obj):
        '''Hook for json.load()'''
        if 'clsname' in obj:
            cls = obj['clsname']
            del obj['clsname']
            if cls in ("bytes", "bytearray"):
                import base64
                if cls == "bytes":
                    b = base64.b85decode( obj.s.encode("ascii") )
                else:
                    b = bytesarray( base64.b85decode( obj.s.encode("ascii") ) )
                return b
            elif cls in globals():
                constructor = globals()[cls]
            elif cls in self.classes:
                constructor = self.classes[cls]
            else:
                raise IKException(ErrorCode.objectNotExists, cls)
            try:
                instance = constructor()
            except Exception as e:
                print("Cannot instantiate class {0} : {1}".format( cls, e) )
                s = input("Press any key...")
                sys.exit( -1 )
            instance.__dict__ = obj
            return instance
        
        return obj            
