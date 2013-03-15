SCRIPT_PATH = r"C:\Python26\Lib\site-packages"

import site
site.addsitedir(SCRIPT_PATH)
from itcrispr import itcrispr

itcrispr.main(SCRIPT_PATH, __bnscontext__)  # IGNORE:E0602 @UndefinedVariable
