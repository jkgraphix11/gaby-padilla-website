#!/usr/bin/env python3
"""Add live SEO URLs after the public domain is confirmed.
Usage: python prepare_launch.py https://www.your-verified-domain.com
Safe to rerun to update a verified domain.
"""
from pathlib import Path
from urllib.parse import urlparse
import sys, re, json, xml.etree.ElementTree as ET
site=Path(__file__).resolve().parent
if len(sys.argv)!=2:raise SystemExit('Usage: python prepare_launch.py https://VERIFIED-REAL-DOMAIN')
domain=sys.argv[1].rstrip('/')
p=urlparse(domain)
if p.scheme!='https' or not p.hostname or p.path not in ('','/') or p.query or p.fragment or p.hostname in ('example.com','your-domain.com','localhost'):
 raise SystemExit('Provide the verified public HTTPS domain root.')
pairs={
 'home':{'es-MX':('', 'index.html'),'en':('en/','en/index.html')},
 'bridal':{'es-MX':('novias/','novias/index.html'),'en':('en/bridal/','en/bridal/index.html')},
 'xv':{'es-MX':('xv-anos/','xv-anos/index.html'),'en':('en/quinceanera/','en/quinceanera/index.html')},
}
portrait=domain+'/assets/images/gaby-padilla-portrait-maquillista-tijuana.jpg'
urls={pair:{lang:domain+'/'+rel[0] for lang,rel in langs.items()} for pair,langs in pairs.items()}
for group, langs in pairs.items():
 for locale,(_,name) in langs.items():
  file=site/name;txt=file.read_text(encoding='utf-8')
  txt=re.sub(r'<link[^>]*rel=["\'](?:canonical|alternate)["\'][^>]*>', '',txt)
  txt=re.sub(r'<meta[^>]*(?:property=["\']og:url["\']|property=["\']og:image["\']|name=["\']twitter:image["\'])[^>]*>', '',txt)
  preferred_image=portrait if group=='home' else domain+'/assets/images/gaby-padilla-social-share.jpg'
  tags='\n'+'\n'.join([f'<link rel="canonical" href="{urls[group][locale]}">',f'<link rel="alternate" hreflang="es-MX" href="{urls[group]["es-MX"]}">',f'<link rel="alternate" hreflang="en" href="{urls[group]["en"]}">',f'<link rel="alternate" hreflang="x-default" href="{urls[group]["es-MX"]}">',f'<meta property="og:url" content="{urls[group][locale]}">',f'<meta property="og:image" content="{preferred_image}">',f'<meta name="twitter:image" content="{preferred_image}">'])
  txt=txt.replace('</head>',tags+'\n</head>',1)
  if group=='home':
   match=re.search(r'(<script[^>]*id="local-business-schema"[^>]*>)(.*?)(</script>)',txt,flags=re.DOTALL)
   if not match:raise SystemExit('Missing business schema '+name)
   item=json.loads(match.group(2));item.update({'@id':domain+'/#business','url':domain+'/','logo':domain+'/assets/images/gaby-padilla-logo.png','image':portrait})
  else:
   match=re.search(r'(<script[^>]*id="service-schema"[^>]*>)(.*?)(</script>)',txt,flags=re.DOTALL)
   if not match:raise SystemExit('Missing service schema '+name)
   item=json.loads(match.group(2));item['@id']=urls[group][locale]+'#service';item['url']=urls[group][locale];item['provider']['@id']=domain+'/#business'
  txt=txt[:match.start()]+match.group(1)+json.dumps(item,ensure_ascii=False,separators=(',',':'))+match.group(3)+txt[match.end():]
  if group=='home':
   caption=('Retrato de Gaby Padilla, maquillista en Playas de Tijuana, con brochas de maquillaje' if locale=='es-MX' else 'Portrait of Gaby Padilla, makeup artist in Playas de Tijuana, holding makeup brushes')
   for prop,value in [('og:image:width','975'),('og:image:height','975'),('og:image:alt',caption)]:
    txt=re.sub(r'<meta[^>]*property=["\']'+re.escape(prop)+r'["\'][^>]*>',f'<meta property="{prop}" content="{value}">',txt)
   txt=re.sub(r'<script[^>]*id="primary-image-schema"[^>]*>.*?</script>', '',txt, flags=re.DOTALL)
   txt=re.sub(r'<meta[^>]*name=["\']twitter:image:alt["\'][^>]*>', '',txt)
   txt=re.sub(r'<meta[^>]*property=["\']og:image:type["\'][^>]*>', '',txt)
   image={'@type':'ImageObject','@id':domain+'/#portrait','url':portrait,'contentUrl':portrait,'width':975,'height':975,'caption':caption}
   page={'@context':'https://schema.org','@type':'WebPage','@id':urls[group][locale]+'#webpage','url':urls[group][locale],'inLanguage':locale,'mainEntity':{'@id':domain+'/#business'},'primaryImageOfPage':image}
   txt=txt.replace('</head>','<meta property="og:image:type" content="image/jpeg">\n'+f'<meta name="twitter:image:alt" content="{caption}">\n'+'<script id="primary-image-schema" type="application/ld+json">'+json.dumps(page,ensure_ascii=False,separators=(',',':'))+'</script>\n</head>',1)
  file.write_text(txt,encoding='utf-8')
ET.register_namespace('','http://www.sitemaps.org/schemas/sitemap/0.9')
ET.register_namespace('image','http://www.google.com/schemas/sitemap-image/1.1')
ET.register_namespace('xhtml','http://www.w3.org/1999/xhtml')
ns='http://www.sitemaps.org/schemas/sitemap/0.9';xn='http://www.w3.org/1999/xhtml'
root=ET.Element('{%s}urlset'%ns)
for group,langs in urls.items():
 for locale,target in langs.items():
  node=ET.SubElement(root,'{%s}url'%ns)
  ET.SubElement(node,'{%s}loc'%ns).text=target
  if group=='home':
   image_node=ET.SubElement(node,'{http://www.google.com/schemas/sitemap-image/1.1}image')
   ET.SubElement(image_node,'{http://www.google.com/schemas/sitemap-image/1.1}loc').text=portrait
  for language,href in [('es-MX',langs['es-MX']),('en',langs['en']),('x-default',langs['es-MX'])]:
   ET.SubElement(node,'{%s}link'%xn,{'rel':'alternate','hreflang':language,'href':href})
ET.indent(root,space='  ')
ET.ElementTree(root).write(site/'sitemap.xml',encoding='utf-8',xml_declaration=True)
(site/'robots.txt').write_text('User-agent: *\nAllow: /\n\nSitemap: '+domain+'/sitemap.xml\n',encoding='utf-8')
config=site/'seo_config.json';data=json.loads(config.read_text(encoding='utf-8'));data['production_domain']=domain;config.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('SEO ready for',len(urls)*2,'pages at',domain)
