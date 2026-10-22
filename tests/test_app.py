from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

APP=Path(__file__).resolve().parents[1]/'app.py'
WORKFLOWS=['Clean & merge','Convert files','Extract PDF','Organize files']
SAMPLE='Try with sample data'
UPLOAD='Upload your own files'

def source(app):
    return next(widget for widget in app.radio if widget.label=='Choose your data')

def load(page):
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    app.sidebar.radio[0].set_value(page).run()
    return app

@pytest.mark.parametrize('page',['Overview',*WORKFLOWS])
def test_workspaces_and_fictional_demo(page):
    app=load(page)
    assert not app.exception and not app.error
    if page!='Overview':
        assert source(app).value==SAMPLE
        assert len(app.dataframe)>0
        if page=='Clean & merge':assert app.metric[1].value=='4'
        if page=='Organize files':
            app.checkbox[-1].check().run()
            assert not app.exception and not app.error

@pytest.mark.parametrize('page',WORKFLOWS)
def test_both_modes_available_by_default(page,monkeypatch):
    monkeypatch.delenv('TOOLKIT_ALLOW_UPLOADS',raising=False)
    app=load(page)
    source(app).set_value(UPLOAD).run()
    assert len(app.get('file_uploader'))==1
    assert not app.exception and not app.error
    source(app).set_value(SAMPLE).run()
    assert not app.get('file_uploader')
    assert len(app.dataframe)>0


def test_admin_can_disable_uploads(monkeypatch):
    monkeypatch.setenv('TOOLKIT_ALLOW_UPLOADS','false')
    app=load('Convert files')
    assert source(app).options==[SAMPLE]
    assert not app.get('file_uploader')


def test_scanned_pdf_is_demonstrable_without_upload():
    app=load('Extract PDF')
    app.selectbox[0].set_value('scanned_invoice.pdf').run()
    assert any('OCR' in w.value for w in app.warning)
    assert not app.exception and not app.error


def test_independent_streamlit_sessions_and_clear():
    a=load('Extract PDF');b=load('Extract PDF')
    a_epoch=a.session_state['_toolkit_epoch'];b_epoch=b.session_state['_toolkit_epoch']
    assert a_epoch!=b_epoch
    b.selectbox[0].set_value('scanned_invoice.pdf').run()
    assert not a.warning
    assert any('OCR' in w.value for w in b.warning)
    assert a.session_state['_toolkit_pdf_cache']['fingerprint']!=b.session_state['_toolkit_pdf_cache']['fingerprint']
    a.sidebar.button[0].click().run()
    assert a.session_state['_toolkit_epoch']!=a_epoch
    assert b.session_state['_toolkit_epoch']==b_epoch
    assert any('OCR' in w.value for w in b.warning)


def test_mode_and_navigation_discard_cached_document():
    app=load('Extract PDF')
    assert '_toolkit_pdf_cache' in app.session_state
    source(app).set_value(UPLOAD).run()
    assert '_toolkit_pdf_cache' not in app.session_state
    source(app).set_value(SAMPLE).run()
    assert '_toolkit_pdf_cache' in app.session_state
    app.sidebar.radio[0].set_value('Convert files').run()
    assert '_toolkit_pdf_cache' not in app.session_state
