from browser_support import BrowserApp
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
import shutil
import argparse
parser=argparse.ArgumentParser(description="Validate fictional portfolio workflows in a real browser.")
parser.add_argument("--uploads",action="store_true",help="Test real uploads against a trusted local upload-enabled server.")
parser.add_argument('--url',default='http://127.0.0.1:8501',help='Local Streamlit test server URL.')
parser.add_argument('--screenshots-dir',default='docs/screenshots',help='Screenshot output directory relative to the project.')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
capture_dir=root/args.screenshots_dir
capture_dir.mkdir(parents=True,exist_ok=True)
(root/'artifacts').mkdir(parents=True,exist_ok=True)
results=[]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,chromium_sandbox=True,args=['--disable-dev-shm-usage'])
    page=BrowserApp(browser.new_page(viewport={'width':1440,'height':1500},device_scale_factor=1))
    page.goto(args.url,wait_until='networkidle')
    page.get_by_role('heading',name='Universal Data Automation Toolkit',exact=True).wait_for()
    page.screenshot(path=str(capture_dir/'01-overview.png'),full_page=True)
    workflows=[('Clean & merge',['sales_january.csv','sales_february.xlsx'],'02-clean-merge.png'),('Convert files',['customers.json'],'03-convert.png'),('Extract PDF',['fictional_invoice.pdf'],'04-pdf.png'),('Organize files',['sales_january.csv','customers.json'],'05-organizer.png')]
    for name,files,screenshot in workflows:
        page.get_by_text(name,exact=True).first.click()
        page.get_by_role('heading',name=name,exact=True).wait_for()
        if args.uploads:
            print('Uploading',name,flush=True)
            page.get_by_text('Upload your own files',exact=True).click()
            page.locator('input[type=file]').set_input_files([str(root/'samples/input'/f) for f in files])
        else:
            print('Checking fictional samples:',name,flush=True)
            assert not page.locator('input[type=file]').count()
        page.wait_for_timeout(1200)
        page.locator('[data-testid="stDataFrame"]').last.wait_for()
        assert page.locator('[data-testid="stException"]').count()==0
        assert page.locator('[data-testid="stAlert"]').filter(has_text='could not complete').count()==0
        if name=='Clean & merge':
            assert page.locator('[data-testid="stMetricValue"]').nth(1).inner_text()=='4'
            page.get_by_role('button',name='Download CSV',exact=True).first.wait_for()
            with page.expect_download() as event:page.get_by_role('button',name='Download CSV',exact=True).first.click()
            download=event.value;download.save_as(str(root/'artifacts/browser_cleaned.csv'))
            assert 'Alice Chen' in (root/'artifacts/browser_cleaned.csv').read_text()
        if name=='Organize files':
            page.get_by_text('I have reviewed these destination filenames',exact=True).click()
            with page.expect_download() as event:page.get_by_role('button',name='Download organized ZIP').click()
            event.value.save_as(str(root/'artifacts/browser_organized.zip'))
        page.evaluate("document.querySelector('[data-testid=stMain]').scrollTo(0,0)")
        page.wait_for_timeout(200)
        page.screenshot(path=str(capture_dir/screenshot),full_page=True)
        results.append({'workflow':name,'real_upload':args.uploads,'screenshot':screenshot})
    page.get_by_text('Extract PDF',exact=True).first.click()
    page.get_by_role('heading',name='Extract PDF',exact=True).wait_for()
    if args.uploads:
        page.get_by_text('Upload your own files',exact=True).click()
        page.locator('input[type=file]').set_input_files(str(root/'samples/input/scanned_invoice.pdf'))
    else:
        page.get_by_role('combobox').click()
        page.get_by_text('scanned_invoice.pdf',exact=True).last.click()
    page.get_by_text('Page 1: no text layer found.',exact=False).wait_for()
    page.screenshot(path=str(capture_dir/'06-ocr-warning.png'),full_page=True)
    results.append({'scanned_pdf_warning':True})
    browser.close()
report='browser-upload-validation.json' if args.uploads else 'browser-validation.json'
(root/'artifacts'/report).write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
