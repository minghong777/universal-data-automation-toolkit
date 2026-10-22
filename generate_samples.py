"""Rebuild fictional demonstration inputs and actual service-generated outputs."""
from pathlib import Path
from io import BytesIO
import json
import pandas as pd
import pymupdf
from toolkit.tabular import read_table, merge_tables, clean_table, export_csv, export_excel, columns
from toolkit.pdf import extract_pdf
from toolkit.files import plan_files, build_zip, zip_outputs

ROOT=Path(__file__).parent/'samples'

def generate(destination=None):
    base=Path(destination) if destination is not None else ROOT
    inputs=base/'input';outputs=base/'output'
    inputs.mkdir(parents=True,exist_ok=True);outputs.mkdir(parents=True,exist_ok=True)
    header=[' Order ID ',' Customer Name ',' Region ',' Amount ']
    jan=pd.DataFrame([['001',' Alice Chen ',' North ','125.50'],['002','Ben Lin','South','80'],['002','Ben Lin','South','80'],[None,None,None,None]],columns=header)
    feb=pd.DataFrame([['003',' Cara Wu ','North','210'],['004','Dana Lee',None,'95']],columns=header)
    (inputs/'sales_january.csv').write_bytes(jan.to_csv(index=False).encode('utf-8-sig'))
    (inputs/'sales_february.xlsx').write_bytes(export_excel(feb))
    (inputs/'customers.json').write_text(json.dumps([{'customer_id':'C001','name':'Alice Chen','region':'North'},{'customer_id':'C002','name':'Ben Lin','region':'South'}],indent=2))
    (inputs/'unsupported_nested.json').write_text('{"customers": [{"name": "Example"}]}')
    (inputs/'malformed.csv').write_text('id,name\n1,Alice,unexpected\n')
    doc=pymupdf.open();p=doc.new_page(width=500,height=400)
    p.insert_text((40,40),'FICTIONAL INVOICE - DEMO ONLY',fontsize=14)
    p.insert_text((40,65),'Invoice INV-001 | Sample Studio | 2026-01-15',fontsize=10)
    xs=[40,240,330,430];ys=[100,130,160,190]
    for x in xs:p.draw_line((x,ys[0]),(x,ys[-1]))
    for y in ys:p.draw_line((xs[0],y),(xs[-1],y))
    for row,values in enumerate([['Service','Qty','Amount'],['Data cleanup','1','125.50'],['Report export','1','80.00']]):
        for col,value in enumerate(values):p.insert_text((xs[col]+8,ys[row]+20),value,fontsize=10)
    doc.save(inputs/'fictional_invoice.pdf')
    # A raster-only copy demonstrates OCR warnings without needing an OCR engine.
    pix=p.get_pixmap();scan=pymupdf.open();sp=scan.new_page(width=500,height=400)
    sp.insert_image(sp.rect,stream=pix.tobytes('png'));scan.save(inputs/'scanned_invoice.pdf');scan.close();doc.close()
    frames=[]
    for n in ['sales_january.csv','sales_february.xlsx']:
        f=read_table(n,(inputs/n).read_bytes());f.columns=columns(f.columns);frames.append(f)
    cleaned,summary=clean_table(merge_tables(frames))
    (outputs/'cleaned_sales.csv').write_bytes(export_csv(cleaned));(outputs/'cleaned_sales.xlsx').write_bytes(export_excel(cleaned))
    (outputs/'cleaning_summary.json').write_text(json.dumps(summary,indent=2))
    customers=read_table('customers.json',(inputs/'customers.json').read_bytes())
    (outputs/'converted_customers.csv').write_bytes(export_csv(customers))
    (outputs/'converted_customers.xlsx').write_bytes(export_excel(customers))
    pdf=extract_pdf('fictional_invoice.pdf',(inputs/'fictional_invoice.pdf').read_bytes())
    (outputs/'pdf_text.txt').write_text('\n'.join(pdf.pages['text']))
    tables={name+'.csv':export_csv(df) for name,df in pdf.tables}
    if tables:(outputs/'pdf_tables.zip').write_bytes(zip_outputs(tables))
    files=[(n,(inputs/n).read_bytes()) for n in ['sales_january.csv','fictional_invoice.pdf','customers.json']]
    plan=plan_files(files,prefix='client_',numbered=True,organize='extension')
    (outputs/'organized_files.zip').write_bytes(build_zip(files,plan))
    (outputs/'pdf_extraction_summary.json').write_text(json.dumps({'pages':len(pdf.pages),'tables':len(pdf.tables),'warnings':pdf.warnings},indent=2))
    print(f'Generated fictional inputs and verified-path outputs in {base}')

if __name__=='__main__':generate()
