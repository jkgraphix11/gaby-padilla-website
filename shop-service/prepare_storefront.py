"""Export only the public, manual-catalog shop into the production website package."""
from pathlib import Path
from urllib.parse import urlparse
import json,re,shutil,sys

def export_storefront(root,output):
    root,output=Path(root),Path(output)
    source=root/'tienda';target=output/'tienda'
    catalog=json.loads((source/'catalog.json').read_text())
    if not re.fullmatch(r'[0-9]{10,15}',catalog.get('whatsapp','')): raise ValueError('Invalid WhatsApp number')
    products=[p for p in catalog.get('products',[]) if p.get('state')=='published']
    public_fields={'id','name','name_en','brand','size','size_en','category','price','quantity','state','image','description','description_en'}
    catalog={'currency':'MXN','whatsapp':catalog['whatsapp'],'products':[{k:v for k,v in p.items() if k in public_fields} for p in products]}
    images=set()
    for product in products:
        if product.get('state')!='published':raise ValueError('Unapproved product')
        quantity=product.get('quantity')
        if type(quantity)!=int or quantity<0:raise ValueError('Confirm product quantities')
        if not isinstance(product.get('price'),(int,float)) or product['price']<=0:raise ValueError('Confirm product prices')
        image=product.get('image','');rel=Path(image)
        if not image.startswith('assets/') or '..' in rel.parts or urlparse(image).scheme or not (source/rel).is_file():raise ValueError('Missing or invalid product image')
        images.add(image)
    target.mkdir(parents=True,exist_ok=True)
    for name in ['shop.js','shop.css']:
        shutil.copyfile(source/name,target/name)
    (target/'catalog.json').write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n')
    for name in images|{'assets/serum.svg'}:
        dest=target/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/name,dest)
    html=(source/'index.html').read_text()
    html=html.replace('<head>','<head><meta name="shop-preview" content="disabled"><link rel="canonical" href="https://gabypadillamakeup.com/tienda/">',1)
    html=re.sub(r'content="noindex,nofollow,noarchive"','content="index,follow"',html)
    # Public pages never contain the management/demo toolbar.
    html=re.sub(r'<div class="preview-bar" id="preview-bar".*?</div>','',html,flags=re.S)
    (target/'index.html').write_text(html)
    # The storefront script supports a package with no preview controls.
    js=(target/'shop.js').read_text().replace("document.getElementById('preview-bar').hidden = !preview;", "if(document.getElementById('preview-bar'))document.getElementById('preview-bar').hidden = !preview;").replace("document.getElementById('manage-link').href = `manage.html?preview=1&lang=${lang}`;", "if(document.getElementById('manage-link'))document.getElementById('manage-link').href = `manage.html?preview=1&lang=${lang}`;")
    (target/'shop.js').write_text(js)
    sitemap=output/'sitemap.xml'
    if sitemap.exists():
        text=sitemap.read_text()
        if 'https://gabypadillamakeup.com/tienda/' not in text:text=text.replace('</urlset>','<url><loc>https://gabypadillamakeup.com/tienda/</loc></url></urlset>')
        sitemap.write_text(text)
    print(f'Prepared {len(products)} approved products; management and demo files excluded.')

if __name__=='__main__':export_storefront(sys.argv[1],sys.argv[2])
