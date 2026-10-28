import json, secrets, tempfile, threading, unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from http.server import ThreadingHTTPServer
from server import Handler,Store

class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.token=secrets.token_urlsafe(40)
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler);cls.server.store=Store(Path(cls.temp.name)/'db.sqlite');cls.server.token=cls.token
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start();cls.base='http://127.0.0.1:'+str(cls.server.server_port)
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.thread.join();cls.temp.cleanup()
    def call(self,path,data=None,auth=False):
        headers={'Content-Type':'application/json'}
        if auth:headers['Authorization']='Bearer '+self.token
        request=Request(self.base+path,headers=headers,data=json.dumps(data).encode() if data is not None else None)
        try:r=urlopen(request)
        except HTTPError as e:r=e
        return r.status,r.read(),r.headers
    def test_static_shop_and_assets(self):
        for path in ['/tienda/?preview=1','/tienda/shop.js','/tienda/demo-catalog.json','/tienda/assets/serum.svg']:
            self.assertEqual(self.call(path)[0],200)
    def test_auth_and_persistent_publish(self):
        self.assertEqual(self.call('/api/products')[0],401)
        p=dict(name='HTTP test',brand='Example',size='30 ml',description='Test only',price=350,quantity=2,category='skincare',image='assets/serum.svg')
        status,raw,headers=self.call('/api/products',p,True);self.assertEqual(status,201);draft=json.loads(raw)
        self.assertEqual(json.loads(self.call('/api/catalog')[1])['products'],[])
        path='/api/products/'+draft['id']+'/publish'
        self.assertEqual(self.call(path,{'revision':1},True)[0],403)
        self.assertEqual(self.call(path,{'revision':1,'approved':True},True)[0],200)
        status,raw,headers=self.call('/api/catalog');self.assertEqual(status,200);self.assertEqual(json.loads(raw)['products'][0]['quantity'],2)
        self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertEqual(self.call(path,{'revision':1,'approved':True},True)[0],409)
    def test_database_not_web_accessible(self):
        self.assertEqual(self.call('/shop-data/catalog.sqlite3')[0],404)

if __name__=='__main__':unittest.main()
