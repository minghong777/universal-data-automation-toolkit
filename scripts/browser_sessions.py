from browser_support import BrowserApp
"""Two independent browser contexts: uploads, errors, clearing and inline downloads.

Run against a local server or an explicitly approved hosted version using
fictional test markers only. Does not save uploaded files to the repository.
"""
from pathlib import Path
from io import BytesIO
import argparse
import base64
import json
import shutil
import zipfile
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8504')
args=parser.parse_args()

def navigate(page,workspace):
    page.get_by_text(workspace,exact=True).first.click()
    page.get_by_role('heading',name=workspace,exact=True).wait_for()
    page.get_by_text('Upload your own files',exact=True).click()
    page.locator('input[type=file]').wait_for(state='attached')

def decoded_csv(page):
    link=page.get_by_role('button',name='Download CSV',exact=True)
    link.wait_for()
    href=link.get_attribute('href')
    assert href.startswith('data:text/csv;base64,'), 'Private outputs must not use server media URLs.'
    return base64.b64decode(href.split(',',1)[1])

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=shutil.which('google-chrome') or shutil.which('chromium'),headless=True,chromium_sandbox=True,args=['--disable-dev-shm-usage'])
    a=browser.new_context();b=browser.new_context();pa=BrowserApp(a.new_page());pb=BrowserApp(b.new_page())
    for page in [pa,pb]:
        page.goto(args.url,wait_until='networkidle')
        page.get_by_role('heading',name='Universal Data Automation Toolkit',exact=True).wait_for()
        navigate(page,'Convert files')
    for page,marker in [(pa,'FICTIONAL_SESSION_A_ONLY'),(pb,'FICTIONAL_SESSION_B_ONLY')]:
        page.locator('input[type=file]').set_input_files({'name':'same.csv','mimeType':'text/csv','buffer':f'id,name\n001,{marker}\n'.encode()})
    adata=decoded_csv(pa);bdata=decoded_csv(pb)
    assert b'SESSION_A_ONLY' in adata and b'SESSION_B_ONLY' not in adata
    assert b'SESSION_B_ONLY' in bdata and b'SESSION_A_ONLY' not in bdata
    # Real downloads must match the bytes visible only in each session's URI.
    for page,expected in [(pa,adata),(pb,bdata)]:
        with page.expect_download() as event:page.get_by_role('button',name='Download CSV',exact=True).click()
        assert Path(event.value.path()).read_bytes()==expected
    pa.get_by_role('button',name='Clear my session',exact=True).click()
    expect(pa.get_by_role('radio',name='Try with sample data',exact=True)).to_be_checked(timeout=30000)
    pa.get_by_text('Upload your own files',exact=True).click()
    pa.get_by_text('Select a supported file above, or choose the sample-data mode.').wait_for()
    assert not pa.get_by_role('button',name='Download CSV',exact=True).count()
    assert decoded_csv(pb)==bdata
    # Replace a valid upload with malformed CSV: previous output must disappear.
    pb.locator('input[type=file]').set_input_files({'name':'same.csv','mimeType':'text/csv','buffer':b'id,name\n1,A,extra\n'})
    pb.get_by_text('CSV rows have different column counts.',exact=False).wait_for()
    assert not pb.get_by_role('button',name='Download CSV',exact=True).count()
    pb.locator('input[type=file]').set_input_files(str(ROOT/'samples/input/unsupported_nested.json'))
    pb.get_by_text('JSON must be a nonempty array of flat objects.',exact=False).wait_for()
    # Organize copies without altering bytes, and invalidate confirmation on options change.
    navigate(pa,'Organize files')
    original=b'fictional original bytes'
    pa.locator('input[type=file]').set_input_files({'name':'example.txt','mimeType':'text/plain','buffer':original})
    pa.get_by_text('I have reviewed these destination filenames',exact=True).click()
    link=pa.get_by_role('button',name='Download organized ZIP',exact=True)
    link.wait_for();href=link.get_attribute('href')
    with zipfile.ZipFile(BytesIO(base64.b64decode(href.split(',',1)[1]))) as z:
        assert z.read('txt/001_client_example.txt')==original
    pa.get_by_role('textbox',name='Add prefix',exact=True).fill('new_')
    pa.get_by_role('textbox',name='Add prefix',exact=True).press('Tab')
    pa.get_by_text('Confirm the current preview to enable the ZIP download.').wait_for()
    assert not pa.get_by_role('button',name='Download organized ZIP',exact=True).count()
    # Removing a PDF clears previews/results; no cached previous document is redisplayed.
    navigate(pa,'Extract PDF')
    pa.locator('input[type=file]').set_input_files(str(ROOT/'samples/input/fictional_invoice.pdf'))
    pa.get_by_role('button',name='Download extracted text',exact=True).wait_for()
    pa.get_by_role('button',name='Remove fictional_invoice.pdf',exact=True).click()
    pa.get_by_text('Select a PDF above, or choose the sample-data mode.').wait_for()
    assert not pa.get_by_role('button',name='Download extracted text',exact=True).count()
    a.close();b.close();browser.close()
report={'two_independent_contexts':True,'same_filename_distinct_outputs':True,
        'inline_downloads_no_media_url':True,'clear_does_not_affect_other_session':True,
        'invalid_upload_removes_previous_result':True,'original_zip_bytes_preserved':True,
        'changed_plan_resets_confirmation':True,'removed_pdf_removes_result':True}
(ROOT/'artifacts').mkdir(exist_ok=True)
(ROOT/'artifacts/browser-session-validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
