import json,tempfile,unittest
from pathlib import Path
from prepare_storefront import export_storefront

class ProductionExportTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'source';self.out=Path(self.temp.name)/'public'
        shop=self.root/'tienda';(shop/'assets').mkdir(parents=True)
        for name in ['shop.js','shop.css','manage.js','manage.html','instagram-catalog.json','private-notes.txt']:(shop/name).write_text('private fixture' if name.startswith('private') else '')
        (shop/'assets/serum.svg').write_text('<svg/>')
        (shop/'index.html').write_text('<html><head><meta name="robots" content="noindex,nofollow,noarchive"></head><body><div class="preview-bar" id="preview-bar"><a id="manage-link">Admin</a></div></body></html>')
        self.product=dict(id='test',name='Test product',brand='Test',description='Verified description',price=500,quantity=1,category='skincare',state='published',image='assets/serum.svg')
        self.write_catalog()
    def tearDown(self):self.temp.cleanup()
    def write_catalog(self):
        (self.root/'tienda/catalog.json').write_text(json.dumps(dict(currency='MXN',whatsapp='526643867831',products=[self.product])))
    def test_public_export_excludes_management_and_demo_files(self):
        export_storefront(self.root,self.out)
        shop=self.out/'tienda';self.assertTrue((shop/'catalog.json').exists())
        for name in ['manage.js','manage.html','instagram-catalog.json','private-notes.txt']:self.assertFalse((shop/name).exists(),name)
        html=(shop/'index.html').read_text();self.assertNotIn('id="manage-link"',html);self.assertNotIn('noindex',html);self.assertIn('shop-preview" content="disabled',html)
    def test_unapproved_or_unconfirmed_inventory_cannot_be_exported(self):
        for patch in [{'quantity':None},{'quantity':-1},{'image':'../private.txt'}]:
            with self.subTest(patch=patch):
                original=self.product.copy();self.product.update(patch);self.write_catalog()
                with self.assertRaises(ValueError):export_storefront(self.root,self.out)
                self.product=original

    def test_hidden_products_and_private_fields_are_not_public(self):
        self.product['private_note']='do not export'
        hidden={**self.product,'id':'hidden','state':'hidden'}
        draft={**self.product,'id':'draft','state':'draft'}
        path=self.root/'tienda/catalog.json'
        path.write_text(json.dumps(dict(currency='MXN',whatsapp='526643867831',products=[self.product,hidden,draft])))
        export_storefront(self.root,self.out)
        public=json.loads((self.out/'tienda/catalog.json').read_text())['products']
        self.assertEqual(len(public),1);self.assertEqual(public[0]['id'],'test');self.assertNotIn('private_note',public[0])

if __name__=='__main__':unittest.main()
