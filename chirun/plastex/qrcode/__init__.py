from plasTeX import Command, dimen

def ProcessOptions(options, document):
    context = document.context

    links = 'nolinks' not in options
    
    document.userdata.setPath('packages/qrcode/links', links)

class qrcode(Command):
    args = '* [options:dict] text:str'

    def invoke(self, tex):
        a = self.parse(tex)
        self.text = a['text']
        
        default_link = self.ownerDocument.userdata.getPath('packages/qrcode/links')

        self.link = a['options'].get('hyperlink') or a['options'].get('link') or default_link
        height = a['options'].get('height')
        if height is not None:
            self.height = dimen(height)
