"""Text-layer extraction. No OCR and no inferred missing values."""
from dataclasses import dataclass
import pandas as pd
import pymupdf
from .safety import ValidationError, validate_upload

@dataclass
class PDFResult:
    pages: pd.DataFrame
    tables: list[tuple[str,pd.DataFrame]]
    warnings: list[str]

def extract_pdf(name, data):
    validate_upload(name,data,{'.pdf'})
    if not data.startswith(b'%PDF-'):raise ValidationError('File does not have a PDF signature.')
    try:
        with pymupdf.open(stream=data,filetype='pdf') as doc:
            if doc.needs_pass:raise ValidationError('Password-protected PDFs are unsupported.')
            if len(doc)>100:raise ValidationError('Maximum 100 PDF pages.')
            pages=[];tables=[];warnings=[];total=0
            for number,page in enumerate(doc,1):
                text=page.get_text('text',sort=True)
                total+=len(text)
                if total>2_000_000:raise ValidationError('Extracted text exceeds 2 million characters.')
                pages.append({'page':number,'text':text})
                if not text.strip():
                    warnings.append(f'Page {number}: no text layer found. Scanned/image pages require OCR; blank pages are also possible.')
                    continue
                try:
                    finder=page.find_tables()
                    for index,table in enumerate(finder.tables,1):
                        rows=table.extract()
                        if rows:
                            width=max(map(len,rows))
                            # Keep every detected row, including possible headers, without guessing.
                            frame=pd.DataFrame([r+[None]*(width-len(r)) for r in rows],columns=[f'column_{i+1}' for i in range(width)])
                            tables.append((f'page_{number}_table_{index}',frame))
                except Exception:
                    warnings.append(f'Page {number}: table detection failed; extracted text is still available.')
            if not tables:warnings.append('No tables detected. Text extraction does not guarantee table structure.')
            return PDFResult(pd.DataFrame(pages),tables,warnings)
    except ValidationError:raise
    except Exception as e:raise ValidationError('Could not parse this PDF. It may be damaged or unsupported.') from e

def preview_pdf(name, data):
    """Bounded first-page visual preview, returned as bytes to the same session."""
    validate_upload(name, data, {'.pdf'})
    try:
        with pymupdf.open(stream=data, filetype='pdf') as doc:
            if doc.needs_pass or not len(doc):
                raise ValidationError('Cannot preview an empty or password-protected PDF.')
            page = doc[0]
            scale = min(1.0, 1200 / max(page.rect.width, page.rect.height, 1))
            return page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False).tobytes('png')
    except ValidationError:
        raise
    except Exception as error:
        raise ValidationError('Cannot create a visual preview of this PDF.') from error
