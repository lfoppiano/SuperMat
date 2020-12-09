# SuperMat 
SuperMat (Superconductors Material) dataset is a manually **linked** **annotated** dataset of superconductors related materials and properties. 

## Content
 - Annotated dataset:
    - XML annotated fulltext data (under `data`)
    - CSV tabular superconductors data (supercon_manual.csv)
 - Annotation guidelines (under `docs`), [online version](supermat.readthedocs.io) [will work after the repository will be published]
 - Transformation scripts (under `super_mat/converters`)
 - Analysis Jupyter Notebooks (under `super_mat/`)
    - [dataset-analysis-labelling.ipynb](super_mat/dataset-analysis-labelling.ipynb)
    - [dataset-analysis-linking.ipynb](super_mat/dataset-analysis-linking.ipynb)
    - [dataset-analysis-papers.ipynb](super_mat/dataset-analysis-papers.ipynb)
 
## Dataset information

 
## Usage

### Conversion tools

To use the scripts and analysis data 

> conda create --name SuperMat pip 

> pip install -r requirements.txt 

### Analysis tools 

The analysis tools provide statistics and information from the dataset, they also run consistency checks of the format and content. 
Results can be seen directly on the repository. 
 
> jupyter-lab 


### Annotation guidelines

We use reStructured TExt using the utility [Sphinx](https://www.sphinx-doc.org/en/master/) which provide several output formats. Currently we support XML and PDF. 

To build this documentation locally, we recommend to create a virtual environment such as `virtualenv` or `conda`:  

> conda create -name guidelines 
> conda activate guidelines
>
> conda install sphinx 

#### Build HTML site

To build the documentation as a website: 

> sphinx-build -b html docs _build

##### Automatic build

Sphinx allows automatic build using `sphinx-autobuild`, which will automatically reload and update on a webservice spawned at-hoc. 
You can launch the automatic build using: 

> sphinx-autobuild docs build_ 

you can access the service by opening the browser at `http://localhost:8000`.

#### Build PDF 

You can export this document as PDF using `rst2pdf`. 

Even if you have conda, you should install the version provided by pipy: 

> pip install rst2pdf

Then you need to modify your `config.py` by adding the following information: 

```python
extensions = ['rst2pdf.pdfbuilder']
pdf_documents = [('index', u'filename', u'Title', u'Author')]
``` 

and build using 

> sphinx-build -b pdf sourcedir builddir

and a file with the specified name will be created in `builddir`.

## Licence

The dataset is licensed under CC BY 4.0 CC

The code is licences under Apache 2.0 

## To cite ths work
TBA


