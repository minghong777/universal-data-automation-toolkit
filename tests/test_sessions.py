from io import BytesIO
import base64
import re
import ast
from pathlib import Path
import pytest
import pandas as pd
from toolkit.downloads import download_markup
from toolkit.session import session_epoch,clear_session,pdf_result,PDF_CACHE
from toolkit.safety import ValidationError,MAX_TOTAL


def test_pdf_cache_is_owned_by_supplied_session():
    a={};b={}
    factory=lambda:pd.DataFrame({'private':['TEST_A']})
    first=pdf_result(a,'same-filename',factory)
    other=pdf_result(b,'same-filename',factory)
    assert first is not other
    first.iloc[0,0]='CHANGED'
    assert other.iloc[0,0]=='TEST_A'
    assert pdf_result(a,'same-filename',factory) is first
    clear_session(a)
    assert PDF_CACHE not in a and PDF_CACHE in b
    assert session_epoch(a)!=session_epoch(b)


def test_failed_replacement_cannot_leave_previous_pdf_cached():
    state={};pdf_result(state,'a',lambda:'old document')
    def bad():raise ValidationError('bad document')
    with pytest.raises(ValidationError):pdf_result(state,'b',bad)
    assert PDF_CACHE not in state


def test_clear_rotates_widgets_and_removes_only_own_state():
    a={'workspace':'Convert files','upload_private':b'private','another_result':'x'}
    b={'upload_private':b'other'};old=session_epoch(a)
    clear_session(a)
    assert set(a)=={'workspace','_toolkit_epoch'}
    assert session_epoch(a)!=old
    assert b['upload_private']==b'other'


def test_inline_download_has_no_server_media_link_and_exact_bytes():
    a=download_markup('Download CSV',b'id\nCLIENT_A\n','same.csv','text/csv')
    b=download_markup('Download CSV',b'id\nCLIENT_B\n','same.csv','text/csv')
    href=re.search(r'href="([^"]+)"',a).group(1)
    assert href.startswith('data:text/csv;base64,')
    assert base64.b64decode(href.split(',',1)[1])==b'id\nCLIENT_A\n'
    assert a!=b and '/media/' not in a


def test_download_label_escaped_and_paths_rejected():
    html=download_markup('<script>alert(1)</script>',b'x','x.txt','text/plain')
    assert '<script>' not in html
    with pytest.raises(ValidationError):download_markup('x',b'x','../secret','text/plain')
    with pytest.raises(ValidationError):download_markup('x',b'x','x.txt','text/html')
    with pytest.raises(ValidationError):download_markup('x',b'x'*(MAX_TOTAL+1),'x.txt','text/plain')


def test_app_has_no_shared_cache_or_media_download_calls():
    app=(Path(__file__).resolve().parents[1]/'app.py').read_text()
    tree=ast.parse(app)
    calls={node.func.attr for node in ast.walk(tree) if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute)}
    assert not calls & {'cache_data','cache_resource','download_button','image'}
