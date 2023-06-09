from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor

#TEXTRACT_EXTENSIONS = [".pdf", ".doc", ".docx", ".ppt", ".pptx"]
TEXTRACT_EXTENSIONS = [".pdf"]

class CustomLinkExtractor(LxmlLinkExtractor):

    def __init__(self, *args, **kwargs):
        super(CustomLinkExtractor, self).__init__(*args, **kwargs)
        # Keep the default values in "deny_extensions" *except* for those types we want.
        self.deny_extensions = [ext for ext in self.deny_extensions if ext not in TEXTRACT_EXTENSIONS]