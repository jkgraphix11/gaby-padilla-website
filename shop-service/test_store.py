import base64, io, json, tempfile, unittest
from pathlib import Path
from server import Store,CatalogError

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.store=Store(Path(self.temp.name)/'catalog.db')
        self.product=dict(name='Crema de prueba',brand='Marca',size='50 ml',description='Descripción verificada.',price=350,quantity=2,category='skincare',image='assets/cream.svg')
    def tearDown(self): self.temp.cleanup()
    def create(self): return self.store.draft(self.product)
    def publish(self,pid,rev): return self.store.action(pid,'publish',{'revision':rev,'approved':True})
    def test_draft_is_private_and_publish_requires_approval(self):
        p=self.create();self.assertEqual(self.store.catalog()['products'],[])
        with self.assertRaises(CatalogError) as e:self.store.action(p['id'],'publish',{'revision':1})
        self.assertEqual(e.exception.status,403);self.publish(p['id'],1);self.assertEqual(self.store.catalog()['products'][0]['quantity'],2)
    def test_edit_does_not_change_live_listing(self):
        p=self.create();self.publish(p['id'],1)
        self.store.draft({**self.product,'price':500,'revision':2},p['id'])
        self.assertEqual(self.store.catalog()['products'][0]['price'],350)
        self.publish(p['id'],3);self.assertEqual(self.store.catalog()['products'][0]['price'],500)
    def test_stale_approval_rejected(self):
        p=self.create();self.store.draft({**self.product,'quantity':1,'revision':1},p['id'])
        with self.assertRaises(CatalogError) as e:self.publish(p['id'],1)
        self.assertEqual(e.exception.status,409);self.assertEqual(self.store.catalog()['products'],[])
    def test_sold_out_hide_and_restock_same_product(self):
        p=self.create();self.publish(p['id'],1)
        self.store.action(p['id'],'sold-out',{'revision':2,'approved':True})
        self.assertEqual(self.store.catalog()['products'][0]['quantity'],0)
        self.store.action(p['id'],'hide',{'revision':3,'approved':True});self.assertEqual(self.store.catalog()['products'],[])
        self.store.draft({**self.product,'quantity':1,'revision':4},p['id']);self.publish(p['id'],5)
        self.assertEqual(self.store.catalog()['products'][0]['id'],p['id']);self.assertEqual(self.store.catalog()['products'][0]['quantity'],1)
    def test_invalid_inventory_and_remote_images_rejected(self):
        for patch in [{'quantity':-1},{'quantity':1.5},{'quantity':True},{'price':float('nan')},{'price':-10},{'image':'https://evil.example/image.jpg'},{'image':12},{'image':'assets/../../config.json'},{'openaiFileIdRefs':[{'download_link':'http://127.0.0.1/private'}]}]:
            with self.subTest(patch=patch):
                with self.assertRaises(CatalogError):self.store.draft({**self.product,**patch})
    def test_sold_out_does_not_publish_pending_copy(self):
        p=self.create();self.publish(p['id'],1)
        self.store.draft({**self.product,'description':'New pending text','revision':2},p['id'])
        self.store.action(p['id'],'sold-out',{'revision':3,'approved':True})
        self.assertEqual(self.store.catalog()['products'][0]['description'],self.product['description'])
        self.assertEqual(self.store.get(p['id'])['draft']['quantity'],0)
    def test_persists_across_process_connections(self):
        p=self.create();self.publish(p['id'],1)
        other=Store(self.store.path);self.assertEqual(other.catalog()['products'][0]['name'],self.product['name'])
    def test_optional_size_can_be_omitted_blank_or_null_and_published(self):
        for value in [None, '', '   ', 'missing']:
            with self.subTest(value=value):
                product={**self.product,'size':value}
                if value=='missing': product.pop('size')
                draft=self.store.draft(product)
                self.publish(draft['id'],1)
                self.assertEqual(self.store.get(draft['id'])['live']['size'],'')
        for invalid in [42, [], 'x'*101]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(CatalogError): self.store.draft({**self.product,'size':invalid})
    def test_clean_upload(self):
        from PIL import Image
        root=Path(self.temp.name)/'site';(root/'tienda').mkdir(parents=True)
        store=Store(Path(self.temp.name)/'photo.db',root);buffer=io.BytesIO();Image.new('RGB',(100,100),'white').save(buffer,format='PNG')
        p=store.draft({**self.product,'image':'data:image/png;base64,'+base64.b64encode(buffer.getvalue()).decode()})
        path=store.get(p['id'])['draft']['image'];self.assertTrue((root/path.lstrip('/')).is_file());self.assertTrue(path.endswith('.jpg'))

if __name__=='__main__':unittest.main(verbosity=2)
