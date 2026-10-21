from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
APP=Path(__file__).resolve().parents[1]/'app.py'

@pytest.mark.parametrize('page',['Overview','Clean & merge','Convert files','Extract PDF','Organize files'])
def test_workspaces_and_fictional_demo(page):
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception
    if page!='Overview':
        if not app.checkbox[0].value:
            app.checkbox[0].check().run()
        assert not app.exception
        assert not app.error, [e.value for e in app.error]
        assert len(app.dataframe)>0
        if page=='Clean & merge':assert app.metric[1].value=='4'
        if page=='Organize files':
            app.checkbox[-1].check().run()
            assert not app.exception and not app.error


def test_public_demo_disables_uploads(monkeypatch):
    monkeypatch.delenv('TOOLKIT_ALLOW_UPLOADS',raising=False)
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    for page in ['Clean & merge','Convert files','Extract PDF','Organize files']:
        app.sidebar.radio[0].set_value(page).run()
        assert app.checkbox[0].value and app.checkbox[0].disabled
        assert not app.get('file_uploader')
        assert not app.exception and not app.error


def test_local_upload_mode_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setenv('TOOLKIT_ALLOW_UPLOADS','true')
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    app.sidebar.radio[0].set_value('Convert files').run()
    assert not app.checkbox[0].value and not app.checkbox[0].disabled
    assert len(app.get('file_uploader'))==1
    assert not app.exception

def test_scanned_pdf_is_demonstrable_without_public_uploads(monkeypatch):
    monkeypatch.delenv('TOOLKIT_ALLOW_UPLOADS',raising=False)
    app=AppTest.from_file(str(APP),default_timeout=30).run()
    app.sidebar.radio[0].set_value('Extract PDF').run()
    app.selectbox[0].set_value('scanned_invoice.pdf').run()
    assert any('OCR' in w.value for w in app.warning)
    assert not app.get('file_uploader')
    assert not app.exception and not app.error
