"""Run with: streamlit run app.py. No uploaded data is stored globally."""
from dataclasses import asdict
from pathlib import Path
import hashlib
import os
import pandas as pd
import streamlit as st
from toolkit.safety import ValidationError, validate_batch
from toolkit.tabular import read_table, sheet_names, columns, merge_tables, clean_table, profile, filter_sort, export_csv, export_excel
from toolkit.pdf import extract_pdf, preview_pdf
from toolkit.files import plan_files, build_zip, zip_outputs
from toolkit.downloads import download_markup, image_markup
from toolkit.session import session_epoch, clear_session, clear_results, pdf_result

ROOT = Path(__file__).parent
# Both modes are available by default, including on Community Cloud.
# An owner can disable uploads explicitly as an operational kill switch.
ALLOW_UPLOADS = os.environ.get('TOOLKIT_ALLOW_UPLOADS', 'true').lower() == 'true'
SAMPLE = 'Try with sample data'
UPLOAD = 'Upload your own files'
st.set_page_config(page_title='Universal Data Automation Toolkit', page_icon='📁', layout='wide')
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:2.5rem;}
h1 {letter-spacing:-0.04em;} [data-testid="stMetric"] {background:white;border:1px solid #dce5ed;border-radius:12px;padding:16px;}
a.toolkit-download {display:inline-block;background:#167D8D;color:white!important;text-decoration:none;padding:0.65rem 1rem;border-radius:8px;margin:0.3rem 0;}
</style>''', unsafe_allow_html=True)

def reset_session():
    clear_session(st.session_state)

def reset_results():
    clear_results(st.session_state)

st.sidebar.title('Data Automation')
st.sidebar.caption('Practical tools for everyday file work')
page = st.sidebar.radio('Workspace', ['Overview', 'Clean & merge', 'Convert files', 'Extract PDF', 'Organize files'], key='workspace', on_change=reset_session)
epoch = session_epoch(st.session_state)
st.sidebar.divider()
st.sidebar.button('Clear my session', on_click=reset_session, help='Remove this session’s upload/result references and reset file controls. Downloaded files cannot be deleted by the app.')
st.sidebar.caption('10 MiB/file · 30 MiB/batch · 30 files\nOriginal files remain unchanged.')
with st.sidebar.expander('How your files are handled'):
    st.write('Uploads travel to this server. The app processes them in session memory, without saving client files to a database or shared output folder. Use non-sensitive files only.')
    st.write('Clearing the session removes app references and resets file controls. Framework buffers and temporary resources follow their own cleanup lifecycle; instant secure erasure is not guaranteed.')
    st.write('Downloaded files and browser memory remain under your control. This public demo has no client login or malware sandbox.')
st.title(page if page != 'Overview' else 'Universal Data Automation Toolkit')
st.caption('Choose your files, review the changes, and download the result.')

def source_mode(workflow):
    options = [SAMPLE, UPLOAD] if ALLOW_UPLOADS else [SAMPLE]
    selected = st.radio('Choose your data', options, horizontal=True, key=f'source_{workflow}_{epoch}', on_change=reset_results)
    if not ALLOW_UPLOADS:
        st.info('The owner has temporarily disabled uploads. Fictional samples remain available.')
    if selected == UPLOAD:
        st.info('Use non-sensitive test files. Uploaded contents are sent to this server for processing. Do not upload passwords, account keys, financial records or confidential customer data.')
    return selected == SAMPLE

def uploads(label, types=None, multiple=False, key='upload'):
    if not ALLOW_UPLOADS:
        raise ValidationError('Uploads are temporarily disabled.')
    formats = ', '.join(t.upper() for t in types) if types else 'Any file type, for renaming only; contents are not executed or extracted'
    st.caption(f'Supported: {formats}. Up to 10 MiB per file; 30 MiB and 30 files per batch.')
    return st.file_uploader(label, type=types, accept_multiple_files=multiple, max_upload_size=10, key=f'upload_{key}_{epoch}', on_change=reset_results)

def pairs(items):
    data = [(f.name, f.getvalue()) for f in items]
    validate_batch(data)
    return data

def download(label, data, filename, mime):
    # Inline URI belongs to this rendered session; no shared media-file endpoint.
    st.markdown(download_markup(label, data, filename, mime), unsafe_allow_html=True)

def downloads(df, stem='processed'):
    c1, c2 = st.columns(2)
    with c1:
        download('Download CSV', export_csv(df), stem+'.csv', 'text/csv')
    with c2:
        try:
            download('Download Excel', export_excel(df), stem+'.xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except ValidationError as error:
            st.warning(str(error))
    st.caption('CSV protects formula-like text with an apostrophe. Excel stores text literally. Downloads are generated for this browser session.')

def table(name, data, key):
    sheet = None
    if name.lower().endswith('.xlsx'):
        digest = hashlib.sha256(data).hexdigest()[:16]
        sheet = st.selectbox(f'Worksheet · {name}', sheet_names(name, data), key=f'{key}_{digest}_{epoch}')
    return read_table(name, data, sheet)

def demo_files(names):
    return [(name, (ROOT/'samples/input'/name).read_bytes()) for name in names]

def sample_downloads(files):
    formats={'.csv':'text/csv','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
             '.json':'application/json','.pdf':'application/pdf'}
    with st.expander('Download sample inputs to try the upload mode'):
        st.caption('Save these fictional files, then select Upload your own files to test the complete flow.')
        for name,data in files:
            download('Download sample · '+name,data,name,formats[Path(name).suffix.lower()])

try:
    if page == 'Overview':
        st.markdown('### Less manual work. More dependable data.')
        st.write('Clean spreadsheets, convert formats, extract PDF content, or organize attachments. Every workflow lets you try fictional samples or upload your own non-sensitive files.')
        a,b,c = st.columns(3)
        a.metric('Workflows', '4'); b.metric('Ways to try', 'Samples or uploads'); c.metric('Paid APIs needed', '0')
        st.dataframe(pd.DataFrame([
            ['Clean & merge', 'Combine monthly exports and remove blanks or duplicates.'],
            ['Convert files', 'Convert CSV, Excel worksheets and flat JSON records.'],
            ['Extract PDF', 'Preview a PDF, extract existing text/tables and identify OCR needs.'],
            ['Organize files', 'Preview new names and folders, then download a ZIP.'],
        ], columns=['Workflow', 'What you can do']), hide_index=True, width='stretch')
        st.info('Start with a workflow on the left. Samples are preloaded; choose “Upload your own files” to select files from your computer.')
        st.caption('Independent portfolio demonstration. All included businesses, names and amounts are fictional. Public uploads are for non-sensitive testing only.')
    elif page == 'Clean & merge':
        st.write('Combine files with matching columns. Review originals, choose cleaning options, and inspect the result before downloading.')
        demo = source_mode('clean')
        items = uploads('Choose CSV or Excel files', ['csv','xlsx'], True, 'clean') if not demo else []
        files = demo_files(['sales_january.csv','sales_february.xlsx']) if demo else pairs(items) if items else []
        if files:
            if demo:sample_downloads(files)
            originals = [table(name, data, f'clean_sheet_{i}') for i,(name,data) in enumerate(files)]
            with st.expander('Original data · preview each file', expanded=True):
                for (name,_), frame in zip(files, originals):
                    st.caption(name); st.dataframe(frame.head(100), hide_index=True)
            st.subheader('Choose cleaning options')
            normalize = st.checkbox('Standardize column names', True)
            frames=[]; header_changes=0
            for frame in originals:
                f=frame.copy(deep=True)
                if normalize:
                    normalized=columns(f.columns)
                    header_changes+=sum(a!=b for a,b in zip(f.columns,normalized))
                    f.columns=normalized
                frames.append(f)
            before=merge_tables(frames)
            with st.expander('Inspect duplicate input records'):
                st.dataframe(before.loc[before.duplicated(keep=False)].head(100), hide_index=True)
            a,b,c=st.columns(3)
            trim=a.checkbox('Trim whitespace',True); empty=b.checkbox('Remove empty rows',True); dedup=c.checkbox('Remove duplicate rows',True)
            case=st.selectbox('Text formatting',['unchanged','lower','upper','title'])
            st.caption('Text formatting affects all text columns; keep unchanged for case-sensitive IDs. Results update automatically.')
            after,summary=clean_table(before,trim=trim,text_case=case,normalize_headers=False,remove_empty=empty,deduplicate=dedup)
            summary['headers_changed']=header_changes
            with st.expander('Filter and sort'):
                a,b,c=st.columns(3)
                col=a.selectbox('Filter column',['(none)',*after.columns])
                op=b.selectbox('Condition',['contains','equals','missing','greater than','less than'])
                value=c.text_input('Filter value')
                sort=st.selectbox('Sort by',['(none)',*after.columns])
                ascending=st.checkbox('Ascending order',True)
                result=filter_sort(after,None if col=='(none)' else col,op,value,None if sort=='(none)' else sort,ascending)
                st.caption('CSV values stay as text to preserve IDs such as 001. Numeric comparisons parse values explicitly; sorting follows the stored column type.')
            a,b,c=st.columns(3)
            a.metric('Input rows',len(before)); b.metric('Result rows',len(result)); c.metric('Duplicates removed',summary['duplicate_rows_removed'])
            left,right=st.columns(2)
            left.subheader('Before'); left.dataframe(before.head(100),hide_index=True)
            right.subheader('After'); right.dataframe(result.head(100),hide_index=True)
            st.subheader('Modification summary'); st.json({**summary,'rows_removed_by_filter':len(after)-len(result)})
            st.subheader('Missing-value report'); st.json(profile(result))
            downloads(result)
        else:
            st.info('Select one or more CSV/XLSX files above, or choose the sample-data mode.')
    elif page == 'Convert files':
        demo=source_mode('convert')
        item=uploads('Choose CSV, Excel or flat JSON', ['csv','xlsx','json'], key='convert') if not demo else None
        if demo or item:
            name,data=demo_files(['customers.json'])[0] if demo else pairs([item])[0]
            if demo:sample_downloads([(name,data)])
            df=table(name,data,'convert_sheet')
            st.subheader('Original data')
            if name.lower().endswith(('.json','.csv')):
                with st.expander('Original file contents'):
                    st.code(data.decode('utf-8-sig')[:8000],language='json' if name.endswith('.json') else None)
                    st.caption('Text preview limited to the first 8,000 characters.')
            st.dataframe(df.head(100),hide_index=True)
            st.subheader('Export preview')
            st.dataframe(df.head(100),hide_index=True)
            st.success(f'{len(df):,} rows and {len(df.columns)} columns ready. Choose CSV or Excel below.')
            st.caption('Flat JSON objects need identical keys. Only the selected Excel worksheet is converted; layout and executable formulas are not preserved.')
            downloads(df,'converted')
        else:
            st.info('Select a supported file above, or choose the sample-data mode.')
    elif page == 'Extract PDF':
        st.write('Preview the original PDF, then review extracted text and detected tables. No OCR or missing-data invention.')
        demo=source_mode('pdf')
        item=uploads('Choose a text-based PDF', ['pdf'], key='pdf') if not demo else None
        if demo or item:
            sample_name=st.selectbox('Sample PDF',['fictional_invoice.pdf','scanned_invoice.pdf']) if demo else None
            name,data=demo_files([sample_name])[0] if demo else pairs([item])[0]
            if demo:sample_downloads([(name,data)])
            digest=hashlib.sha256(data).hexdigest()
            result,preview=pdf_result(st.session_state,digest,lambda:(extract_pdf(name,data),preview_pdf(name,data)))
            with st.expander('Original PDF · first-page preview',expanded=False):
                st.markdown(image_markup(preview),unsafe_allow_html=True)
                st.caption('First-page visual preview only. Extracted results below may include additional pages.')
            for warning in result.warnings:
                st.warning(warning)
            st.subheader('Extracted text by page'); st.dataframe(result.pages,hide_index=True)
            text='\n\n'.join(f'--- Page {r.page} ---\n{r.text}' for r in result.pages.itertuples())
            download('Download extracted text',text.encode('utf-8'),'extracted_text.txt','text/plain')
            downloads(result.pages,'pdf_pages')
            if result.tables:
                outputs={}
                for label,df in result.tables:
                    st.subheader(label.replace('_',' ').title()); st.dataframe(df,hide_index=True)
                    outputs[label+'.csv']=export_csv(df); outputs[label+'.xlsx']=export_excel(df)
                download('Download all tables (ZIP)',zip_outputs(outputs),'pdf_tables.zip','application/zip')
                st.caption('Detected rows include possible headers. Generic column names avoid guessing.')
        else:
            reset_results()
            st.info('Select a PDF above, or choose the sample-data mode.')
    elif page == 'Organize files':
        st.write('Create renamed copies in a new ZIP. Originals are never renamed, moved or overwritten; archives are never extracted.')
        demo=source_mode('files')
        items=uploads('Choose files to organize',multiple=True,key='files') if not demo else []
        files=demo_files(['sales_january.csv','fictional_invoice.pdf','customers.json']) if demo else pairs(items) if items else []
        if files:
            if demo:sample_downloads(files)
            st.subheader('Original files')
            st.dataframe(pd.DataFrame([{'filename':name,'bytes':len(data)} for name,data in files]),hide_index=True)
            st.subheader('Choose naming and folder rules')
            a,b,c=st.columns(3)
            prefix=a.text_input('Add prefix',value='client_'); find=b.text_input('Find text'); replace=c.text_input('Replace with')
            numbered=st.checkbox('Add sequence numbers',True)
            organize=st.selectbox('Organize into folders',['extension','prefix rules','none'])
            rules=st.text_area('Prefix rules (first match wins)',value='sales=reports\nfictional=invoices') if organize=='prefix rules' else ''
            plan=plan_files(files,prefix,find,replace,numbered,organize,rules)
            st.subheader('Preview renamed copies')
            st.dataframe(pd.DataFrame(asdict(op) for op in plan).drop(columns=['index']),hide_index=True)
            fingerprint=hashlib.sha256(repr(plan).encode()+b''.join(hashlib.sha256(d).digest() for _,d in files)).hexdigest()
            confirmed=st.checkbox('I have reviewed these destination filenames',key='confirm_'+fingerprint+'_'+epoch)
            if confirmed:
                download('Download organized ZIP',build_zip(files,plan),'organized_files.zip','application/zip')
            else:
                st.info('Confirm the current preview to enable the ZIP download.')
        else:
            st.info('Select files above, or choose the sample-data mode.')
except ValidationError as error:
    st.error(str(error))
except Exception:
    st.error('Processing could not complete. Check the file contents and try a smaller supported file. No original files were changed.')
