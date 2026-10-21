"""Run with: streamlit run app.py"""
from dataclasses import asdict
from pathlib import Path
import hashlib
import os
import pandas as pd
import streamlit as st
from toolkit.safety import ValidationError, validate_batch
from toolkit.tabular import read_table, sheet_names, columns, merge_tables, clean_table, profile, filter_sort, export_csv, export_excel
from toolkit.pdf import extract_pdf
from toolkit.files import plan_files, build_zip, zip_outputs

ROOT=Path(__file__).parent
# Public deployments default to fictional samples; trusted local uploads are opt-in.
ALLOW_UPLOADS=os.environ.get('TOOLKIT_ALLOW_UPLOADS','false').lower()=='true'
st.set_page_config(page_title='Universal Data Automation Toolkit',page_icon='📁',layout='wide')
st.markdown('''<style>
.block-container {max-width:1200px;padding-top:2.5rem;}
h1 {letter-spacing:-0.04em;} [data-testid="stMetric"] {background:white;border:1px solid #dce5ed;border-radius:12px;padding:16px;}
</style>''',unsafe_allow_html=True)
st.sidebar.title('Data Automation')
st.sidebar.caption('A practical Python portfolio')
page=st.sidebar.radio('Workspace',['Overview','Clean & merge','Convert files','Extract PDF','Organize files'])
st.sidebar.divider()
st.sidebar.caption('Original uploads preserved · 10 MiB/file · 30 MiB/batch · 30 files')
if not ALLOW_UPLOADS:
    st.sidebar.info('Portfolio demo: fictional sample data only.')
st.title(page if page!='Overview' else 'Universal Data Automation Toolkit')
st.caption('Turn repetitive file work into a clear, repeatable workflow.')

def demo_toggle(key):
    return st.checkbox('Use fictional sample data',value=not ALLOW_UPLOADS,disabled=not ALLOW_UPLOADS,key=key)

def uploads(label, types=None, multiple=False):
    if not ALLOW_UPLOADS:
        raise ValidationError('Uploads are disabled in the public portfolio demo.')
    result=st.file_uploader(label,type=types,accept_multiple_files=multiple,max_upload_size=10)
    return result

def pairs(items):
    data=[(f.name,f.getvalue()) for f in items];validate_batch(data);return data

def downloads(df,stem='processed'):
    c1,c2=st.columns(2)
    c1.download_button('Download CSV',export_csv(df),stem+'.csv','text/csv',key=stem+'_csv')
    try:
        c2.download_button('Download Excel',export_excel(df),stem+'.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',key=stem+'_xlsx')
    except ValidationError as error:
        c2.warning(str(error))
    st.caption('CSV formula-like text is prefixed with an apostrophe for spreadsheet safety. Excel stores text literally.')

def table(name,data,key):
    sheet=None
    if name.lower().endswith('.xlsx'):
        sheet=st.selectbox(f'Worksheet · {name}',sheet_names(name,data),key=key)
    return read_table(name,data,sheet)

def demo_files(names):return [(n,(ROOT/'samples/input'/n).read_bytes()) for n in names]

try:
    if page=='Overview':
        st.markdown('### Less manual work. More dependable data.')
        st.write('Merge spreadsheets, clean records, convert formats, extract PDF content, and prepare organized file bundles — with previews before download.')
        a,b,c=st.columns(3)
        a.metric('Workspaces','4');b.metric('Supported workflows','Files → results');c.metric('Paid APIs required','0')
        st.markdown('### Choose a workflow')
        st.dataframe(pd.DataFrame([
            ['Clean & merge','Combine monthly exports; remove blanks and duplicates; filter records.'],
            ['Convert files','CSV ↔ Excel; flat JSON → CSV or Excel.'],
            ['Extract PDF','Export text and detected tables; flag pages that may need OCR.'],
            ['Organize files','Preview batch renames and folders; download a new ZIP.']],columns=['Workspace','What you can do']),hide_index=True,width='stretch')
        st.info('Every workspace includes fictional sample data. No account or API key is needed.')
        st.caption('Built as a demonstrable portfolio project. Sample businesses, names and amounts are fictional.')
    elif page=='Clean & merge':
        st.write('Compatible files share the same column names. Cleaning never fills in missing facts.')
        demo=demo_toggle('clean_demo')
        items=uploads('Upload CSV or Excel files',['csv','xlsx'],True) if not demo else []
        files=demo_files(['sales_january.csv','sales_february.xlsx']) if demo else pairs(items) if items else []
        if files:
            normalize=st.checkbox('Standardize column names',True)
            frames=[]
            header_changes=0
            for i,(name,data) in enumerate(files):
                f=table(name,data,f'clean_sheet_{i}')
                if normalize:
                    normalized=columns(f.columns)
                    header_changes+=sum(a!=b for a,b in zip(f.columns,normalized))
                    f=f.rename(columns=dict(zip(f.columns,normalized)))
                frames.append(f)
            before=merge_tables(frames)
            with st.expander('Inspect duplicate input records'):
                st.dataframe(before.loc[before.duplicated(keep=False)].head(100),hide_index=True)
            a,b,c=st.columns(3)
            trim=a.checkbox('Trim whitespace',True);empty=b.checkbox('Remove empty rows',True);dedup=c.checkbox('Remove duplicate rows',True)
            case=st.selectbox('Text formatting',['unchanged','lower','upper','title'])
            st.caption('Text formatting applies to all text columns. Keep “unchanged” when case-sensitive identifiers matter.')
            after,summary=clean_table(before,trim=trim,text_case=case,normalize_headers=False,remove_empty=empty,deduplicate=dedup)
            summary['headers_changed']=header_changes
            with st.expander('Filter and sort',expanded=True):
                a,b,c=st.columns(3)
                col=a.selectbox('Filter column',['(none)',*after.columns])
                op=b.selectbox('Condition',['contains','equals','missing','greater than','less than'])
                value=c.text_input('Filter value')
                sort=st.selectbox('Sort by',['(none)',*after.columns])
                ascending=st.checkbox('Ascending order',True)
                result=filter_sort(after,None if col=='(none)' else col,op,value,None if sort=='(none)' else sort,ascending)
                st.caption('CSV values stay as text to preserve IDs such as 001. Numeric comparisons parse values explicitly; sorting follows the stored column type.')
            a,b,c=st.columns(3)
            a.metric('Input rows',len(before));b.metric('Result rows',len(result));c.metric('Duplicates removed',summary['duplicate_rows_removed'])
            left,right=st.columns(2)
            left.subheader('Before');left.dataframe(before.head(100),hide_index=True)
            right.subheader('After');right.dataframe(result.head(100),hide_index=True)
            st.subheader('Modification summary');st.json({**summary,'rows_removed_by_filter':len(after)-len(result)})
            st.subheader('Missing-value report');st.json(profile(result))
            st.caption(f'Before cleaning: {profile(before)["duplicate_rows"]} duplicate rows (after selected header normalization).')
            downloads(result)
        else:st.info('Upload files or enable the sample to begin.')
    elif page=='Convert files':
        demo=demo_toggle('convert_demo')
        item=uploads('Upload CSV, XLSX or flat JSON',['csv','xlsx','json']) if not demo else None
        if demo or item:
            name,data=demo_files(['customers.json'])[0] if demo else pairs([item])[0]
            df=table(name,data,'convert_sheet')
            st.dataframe(df.head(100),hide_index=True)
            st.success(f'Ready to export {len(df):,} rows and {len(df.columns)} columns.')
            st.caption('JSON must be an array of flat objects with identical keys. XLSX exports contain the selected worksheet only; formatting and formulas are not recalculated or preserved as executable formulas.')
            downloads(df,'converted')
        else:st.info('Upload a file or enable the sample to begin.')
    elif page=='Extract PDF':
        st.write('Extract existing PDF text and detected tables. Review the output against the original document.')
        demo=demo_toggle('pdf_demo')
        item=uploads('Upload a text-based PDF',['pdf']) if not demo else None
        if demo or item:
            sample_name=st.selectbox('Sample PDF',['fictional_invoice.pdf','scanned_invoice.pdf']) if demo else None
            name,data=demo_files([sample_name])[0] if demo else pairs([item])[0]
            # Cache in this session only, keyed by current file content.
            digest=hashlib.sha256(data).hexdigest()
            if st.session_state.get('pdf_digest')!=digest:
                st.session_state.pdf_result=extract_pdf(name,data);st.session_state.pdf_digest=digest
            result=st.session_state.pdf_result
            for warning in result.warnings:st.warning(warning)
            st.dataframe(result.pages,hide_index=True)
            text='\n\n'.join(f'--- Page {r.page} ---\n{r.text}' for r in result.pages.itertuples())
            st.download_button('Download extracted text',text,'extracted_text.txt','text/plain')
            downloads(result.pages,'pdf_pages')
            if result.tables:
                outputs={}
                for label,df in result.tables:
                    st.subheader(label.replace('_',' ').title());st.dataframe(df,hide_index=True)
                    outputs[label+'.csv']=export_csv(df);outputs[label+'.xlsx']=export_excel(df)
                st.download_button('Download all tables (ZIP)',zip_outputs(outputs),'pdf_tables.zip','application/zip')
                st.caption('Detected rows are preserved, including possible header rows. Generic column names avoid guessing.')
        else:st.info('Upload a PDF or enable the sample to begin.')
    elif page=='Organize files':
        st.write('Prepare renamed copies in a ZIP. Original files are never renamed or moved. Uploaded archives are treated as opaque files and never extracted.')
        demo=demo_toggle('files_demo')
        items=uploads('Upload files to organize',multiple=True) if not demo else []
        files=demo_files(['sales_january.csv','fictional_invoice.pdf','customers.json']) if demo else pairs(items) if items else []
        if files:
            a,b,c=st.columns(3)
            prefix=a.text_input('Add prefix',value='client_');find=b.text_input('Find text');replace=c.text_input('Replace with')
            numbered=st.checkbox('Add sequence numbers',True)
            organize=st.selectbox('Organize into folders',['extension','prefix rules','none'])
            rules=st.text_area('Prefix rules (first match wins)',value='sales=reports\nfictional=invoices') if organize=='prefix rules' else ''
            plan=plan_files(files,prefix,find,replace,numbered,organize,rules)
            st.subheader('Preview');st.dataframe(pd.DataFrame(asdict(op) for op in plan).drop(columns=['index']),hide_index=True)
            confirmed=st.checkbox('I have reviewed these destination filenames',key='confirm_'+hashlib.sha256(repr(plan).encode()).hexdigest())
            if confirmed:
                st.download_button('Download organized ZIP',build_zip(files,plan),'organized_files.zip','application/zip')
            else:st.info('Confirm the current preview to prepare the ZIP.')
except ValidationError as e:
    st.error(str(e))
except Exception:
    st.error('Processing could not complete. Check the file contents and try a smaller supported file. No original files were changed.')
