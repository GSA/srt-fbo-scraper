from datetime import datetime as dt
from io import BytesIO
import zipfile

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4

# utility functions to get zip file as binary in memory for testing purposes

def generate_zip(file_details):
    mem_zip = BytesIO()
    with zipfile.ZipFile(mem_zip, mode = "w", compression = zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(file_details[0], file_details[1])

    return mem_zip.getvalue()

def generate_pdf():
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize = A4)
    textobject = canvas.beginText(1.5, -2.5)
    textobject.textLine("this is a test")
    canvas.saveState()
    canvas.save()
    pdf = buffer.getvalue()
    buffer.close()

    return pdf

def get_zip_in_memory():
    file_name = 'test.pdf'
    pdf = generate_pdf()
    full_zip_in_memory = generate_zip((file_name, pdf))

    return full_zip_in_memory

def get_day_side_effect(*args, **kwargs):
    if args[0] == 'today':
        return dt.strptime('2019-09-19', "%Y-%m-%d")
    elif args[0] == 'yesterday':
        return dt.strptime('2019-09-18', "%Y-%m-%d")
    else:
        raise Exception

if __name__ == '__main__':
    full_zip_in_memory = get_zip_in_memory()