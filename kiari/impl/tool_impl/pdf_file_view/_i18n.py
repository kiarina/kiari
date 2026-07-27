from kiarina.i18n import I18n


class PdfFileViewI18n(I18n, scope="kiari.impl.tool_impl.pdf_file_view"):
    result: str = "Viewed the PDF file successfully."
    not_found_error: str = (
        "Error: '{uri_or_file_path}' was not found.\n\n"
        "Please specify an existing file path and try again."
    )
    not_pdf_error: str = (
        "Error: '{uri_or_file_path}' is not a PDF file.\n\nPlease specify a PDF file and try again."
    )
