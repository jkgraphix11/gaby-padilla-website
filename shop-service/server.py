#!/usr/bin/env python3
"""Local catalog pilot. Serve over HTTPS behind authentication infrastructure before public use."""
import argparse, base64, binascii, hashlib, hmac, io, json, os, re, secrets, sqlite3, time
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[1]
WEBSITE = ROOT/'website' if (ROOT/'website').is_dir() else ROOT
CATEGORIES = {'skincare','makeup'}
MAX_BODY = 8 * 1024 * 1024

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl): return None

class CatalogError(Exception):
    def __init__(self, message, status=400): self.message, self.status = message, status

class Store:
    def __init__(self, path, website=WEBSITE):
        self.path, self.website = Path(path), Path(website)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS products (id TEXT PRIMARY KEY, draft TEXT NOT NULL, live TEXT, state TEXT NOT NULL, revision INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS audit (id INTEGER PRIMARY KEY, product_id TEXT, operation TEXT, revision INTEGER, created INTEGER)')
    @contextmanager
    def db(self):
        db=sqlite3.connect(self.path,timeout=10)
        db.row_factory=sqlite3.Row
        try: yield db; db.commit()
        except: db.rollback(); raise
        finally: db.close()
    def event(self, db, pid, operation, revision):
        db.execute('INSERT INTO audit(product_id,operation,revision,created) VALUES(?,?,?,?)',(pid,operation,revision,int(time.time())))
    def catalog(self):
        with self.db() as db:
            rows=db.execute("SELECT * FROM products WHERE state='published' ORDER BY rowid DESC").fetchall()
        return {'currency':'MXN','whatsapp':'526643867831','products':[{**json.loads(r['live']),'id':r['id'],'state':'published'} for r in rows if r['live']]}
    def listing(self):
        with self.db() as db: rows=db.execute('SELECT * FROM products ORDER BY rowid DESC').fetchall()
        return {'products':[{**json.loads(r['live'] or r['draft']),'id':r['id'],'state':r['state'],'revision':r['revision'],'hasDraft':r['draft']!=r['live']} for r in rows]}
    def get(self,pid):
        with self.db() as db: r=db.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
        if not r: raise CatalogError('Producto no encontrado.',404)
        return {'draft':{**json.loads(r['draft']),'id':pid},'live':json.loads(r['live']) if r['live'] else None,'state':r['state'],'revision':r['revision']}
    def validate(self,data):
        result={}
        for field,limit in [('name',140),('brand',80),('size',100),('description',1600)]:
            s=data.get(field)
            if not isinstance(s,str) or not s.strip() or len(s)>limit: raise CatalogError('Revisa el campo '+field+'.')
            result[field]=s.strip()
        for field in ['name_en','description_en']:
            if field in data:
                if not isinstance(data[field],str) or len(data[field])>1600: raise CatalogError('Traducción no válida.')
                result[field]=data[field].strip()
        price,qty=data.get('price'),data.get('quantity')
        if isinstance(price,bool) or not isinstance(price,(int,float)) or not 0<price<=1000000: raise CatalogError('Precio no válido.')
        if isinstance(qty,bool) or not isinstance(qty,int) or not 0<=qty<=9999: raise CatalogError('La cantidad debe ser un número entero entre 0 y 9999.')
        if data.get('category') not in CATEGORIES: raise CatalogError('Categoría no válida.')
        result.update(price=round(price,2),quantity=qty,category=data['category'])
        image=data.get('image','')
        if not isinstance(image,str): raise CatalogError('Imagen no válida.')
        refs=data.get('openaiFileIdRefs')
        if refs is not None:
            if not isinstance(refs,list) or len(refs)!=1 or not isinstance(refs[0],dict): raise CatalogError('Adjunta exactamente una foto para esta ficha.')
            link=refs[0].get('download_link','');url=urlparse(link)
            if url.scheme!='https' or url.hostname!='files.oaiusercontent.com' or url.port not in (None,443) or url.username or url.password: raise CatalogError('El archivo debe venir del adjunto de ChatGPT.')
            try:
                with build_opener(NoRedirect).open(Request(link,headers={'User-Agent':'GabyCatalog/1.0'}),timeout=8) as response:
                    mime=response.headers.get_content_type()
                    if mime not in {'image/jpeg','image/png','image/webp'}: raise CatalogError('Adjunta una foto JPG, PNG o WebP.')
                    raw=response.read(5*1024*1024+1)
                    if len(raw)>5*1024*1024: raise CatalogError('La foto debe pesar menos de 5 MB.')
                    image='data:'+mime+';base64,'+base64.b64encode(raw).decode()
            except CatalogError: raise
            except Exception: raise CatalogError('No se pudo descargar la foto. Vuelve a adjuntarla e intenta de nuevo.')
        if image.startswith('data:'):
            match=re.fullmatch(r'data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/=\r\n]+)',image)
            if not match: raise CatalogError('Formato de imagen no válido.')
            try:
                raw=base64.b64decode(match[2],validate=True)
                if len(raw)>5*1024*1024: raise CatalogError('La foto debe pesar menos de 5 MB.')
                from PIL import Image,ImageOps
                im=Image.open(io.BytesIO(raw)); im.verify()
                im=Image.open(io.BytesIO(raw)); im=ImageOps.exif_transpose(im).convert('RGB'); im.thumbnail((1600,1600))
                buffer=io.BytesIO(); im.save(buffer,format='JPEG',quality=90); clean=buffer.getvalue()
            except CatalogError: raise
            except Exception: raise CatalogError('No se pudo leer la imagen JPG, PNG o WebP.')
            name=hashlib.sha256(clean).hexdigest()+'.jpg'
            originals=self.path.parent/'originals'; originals.mkdir(parents=True,exist_ok=True)
            (originals/(hashlib.sha256(raw).hexdigest()+'.original')).write_bytes(raw)
            folder=self.website/'tienda'/'uploads'; folder.mkdir(parents=True,exist_ok=True)
            (folder/name).write_bytes(clean)
            image='/tienda/uploads/'+name
        if not isinstance(image,str) or not re.fullmatch(r'(assets/[a-z0-9-]+\.(?:svg|jpg|jpeg|webp|png)|/tienda/uploads/[a-f0-9]{64}\.jpg)',image): raise CatalogError('Añade una foto válida del producto.')
        if image.startswith('/tienda/uploads/') and not (self.website/image.lstrip('/')).is_file(): raise CatalogError('Imagen no encontrada.')
        if image.startswith('assets/') and not (self.website/'tienda'/image).is_file(): raise CatalogError('Imagen no encontrada.')
        result['image']=image
        return result
    def draft(self,data,pid=None):
        draft=self.validate(data)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            if pid:
                row=db.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
                if not row: raise CatalogError('Producto no encontrado.',404)
                if data.get('revision')!=row['revision']: raise CatalogError('El producto cambió. Abre la versión actual y vuelve a revisar.',409)
                revision=row['revision']+1
                db.execute('UPDATE products SET draft=?,revision=? WHERE id=?',(json.dumps(draft,ensure_ascii=False),revision,pid))
            else:
                pid=secrets.token_hex(10);revision=1
                db.execute('INSERT INTO products VALUES(?,?,NULL,?,?)',(pid,json.dumps(draft,ensure_ascii=False),'draft',revision))
            self.event(db,pid,'draft',revision)
        return {'id':pid,'revision':revision,'state':'draft','preview_url':'/tienda/manage.html'}
    def action(self,pid,operation,data):
        if data.get('approved') is not True: raise CatalogError('Se requiere aprobación explícita de esta versión.',403)
        with self.db() as db:
            db.execute('BEGIN IMMEDIATE')
            row=db.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
            if not row: raise CatalogError('Producto no encontrado.',404)
            if data.get('revision')!=row['revision']: raise CatalogError('El producto cambió. Revisa la nueva versión antes de aprobar.',409)
            revision=row['revision']+1
            if operation=='publish':
                db.execute("UPDATE products SET live=draft,state='published',revision=? WHERE id=?",(revision,pid))
            elif operation=='hide': db.execute("UPDATE products SET state='hidden',revision=? WHERE id=?",(revision,pid))
            elif operation=='sold-out':
                draft=json.loads(row['draft']);draft['quantity']=0
                live=json.loads(row['live']) if row['live'] else None
                if live: live['quantity']=0
                db.execute('UPDATE products SET draft=?,live=?,revision=? WHERE id=?',(json.dumps(draft,ensure_ascii=False),json.dumps(live,ensure_ascii=False) if live else None,revision,pid))
            else: raise CatalogError('Acción no disponible.',404)
            self.event(db,pid,operation,revision)
        return {'id':pid,'revision':revision,'operation':operation,'product_url':'/tienda/#'+pid}

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(args[2].store.website),**kwargs)
    def translate_path(self,path):
        resolved=Path(super().translate_path(path))
        relative=resolved.relative_to(self.server.store.website)
        if any(part.startswith('.') for part in relative.parts) or (relative.parts and relative.parts[0] in {'shop-data','shop-service'}):
            return str(self.server.store.website/'__not_a_public_file__')
        return str(resolved)
    def log_message(self,fmt,*args): pass
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','strict-origin-when-cross-origin');super().end_headers()
    def send_json(self,data,status=200):
        body=json.dumps(data,ensure_ascii=False,allow_nan=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def auth(self):
        expected='Bearer '+self.server.token
        if not hmac.compare_digest(self.headers.get('Authorization',''),expected): raise CatalogError('Acceso no autorizado.',401)
        # Auth is never accepted in URLs, cookies, or request bodies. No CORS headers.
    def api(self):
        try:
            path=urlparse(self.path).path
            if self.command=='GET' and path=='/api/catalog': self.send_json(self.server.store.catalog());return
            self.auth()
            parts=path.strip('/').split('/')
            if self.command=='GET':
                if path=='/api/products': self.send_json(self.server.store.listing());return
                if len(parts)==3 and parts[:2]==['api','products']: self.send_json(self.server.store.get(parts[2]));return
            if self.command=='POST':
                if 'application/json' not in self.headers.get('Content-Type',''): raise CatalogError('Usa JSON.',415)
                try: size=int(self.headers.get('Content-Length','0'))
                except ValueError: raise CatalogError('Solicitud no válida.')
                if not 0<size<=MAX_BODY: raise CatalogError('Solicitud demasiado grande o vacía.',413)
                try: data=json.loads(self.rfile.read(size))
                except (ValueError,UnicodeDecodeError): raise CatalogError('JSON no válido.')
                if not isinstance(data,dict): raise CatalogError('Se requiere un objeto JSON.')
                if path=='/api/products': self.send_json(self.server.store.draft(data),201);return
                if len(parts)==3 and parts[:2]==['api','products']: self.send_json(self.server.store.draft(data,parts[2]));return
                if len(parts)==4 and parts[:2]==['api','products']: self.send_json(self.server.store.action(parts[2],parts[3],data));return
            raise CatalogError('Ruta no encontrada.',404)
        except CatalogError as e: self.send_json({'error':e.message},e.status)
        except Exception: self.send_json({'error':'Error interno. No se confirmó el cambio.'},500)
    def do_GET(self):
        if urlparse(self.path).path.startswith('/api/'): self.api()
        else: super().do_GET()
    def do_POST(self): self.api()

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=8765);parser.add_argument('--database',default=str(ROOT/'shop-data'/'catalog.sqlite3'));args=parser.parse_args()
    token=os.environ.get('GABY_SHOP_TOKEN')
    if not token or len(token)<32: parser.error('Set GABY_SHOP_TOKEN to a private random value of at least 32 characters.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler);server.store=Store(args.database);server.token=token
    print(f'Local: http://127.0.0.1:{args.port}/tienda/?preview=1',flush=True)
    server.serve_forever()
if __name__=='__main__': main()
