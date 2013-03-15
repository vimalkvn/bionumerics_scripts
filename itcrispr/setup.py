from distutils.core import setup

setup(name="itcrispr",
      version="0.1.4",
      description="Interface to assemble and track progress of CRISPR "\
      "sequence experiments in BioNumerics",
      author="Vimalkumar Velayudhan",
      author_email="vimalkumarvelayudhan@gmail.com",
      license="LICENSE.txt",
      url="http://github.com/vkvn/itcrispr",
      packages=["itcrispr", "itcrispr.ui", "itcrispr.tests"],
      package_data={"itcrispr": ["itcrispr.cfg", "itcrispr-menu.bns"],
                    "itcrispr.tests": ["data/*.cfg", "data/primer-newline.txt",
                                       "data/dups/*.txt",
                                       "data/primers/*.txt"]},
      data_files=[("", ["README.rst", "README.pdf", "LICENSE.txt"])],
      scripts=["run_itcrispr.py"],
      requires=["PyQt4"]
)
