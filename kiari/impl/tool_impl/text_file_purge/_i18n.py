from kiarina.i18n import I18n


class TextFilePurgeI18n(I18n, scope="kiari.impl.tool_impl.text_file_purge"):
    result: str = "Purged text files from History."
    purged: str = "Purged IDs: {ids}"
    not_found: str = "Not found IDs: {ids}"
    not_text: str = "Non-text IDs not purged: {ids}"
