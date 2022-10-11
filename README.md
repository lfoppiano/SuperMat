
[![Documentation Status](https://readthedocs.org/projects/supermat/badge/?version=latest)](https://supermat.readthedocs.io/en/latest/?badge=latest)


# SuperMat 
SuperMat (Superconductors Material) dataset is a manually **linked** **annotated** dataset of superconductors related materials and properties. 

## Content
 - Annotated dataset:
    - Superconductors data:
        - [Bibliographic](data/biblio) data references as XML-TEI or JSON (CORD-19) format
        - Sources are referenced in the [Bibliographic](data/biblio) data
        - The annotations are not public due to copyright 
    - Tabular version of the linked annotated entities in the dataset [CSV](data/csv/SuperMat-1.0.csv) (*)
    - Material data for segmenting inorganic material names
 - Annotation guidelines:
    - [Online version](https://supermat.readthedocs.io)
    - [Changelog](docs/CHANGELOG.md)
    - [Source](docs), 
 - [Transformation scripts](super_mat/converters)
    - [tsv2xml](super_mat/converters/tsv2xml.py) / [xml2tsv](super_mat/converters/xml2tsv.py): Transformation from an to the INCEpTION TSV 3.2 format
    - [xmlSupermat2csv](super_mat/converters/xmlSupermat2csv.py): Converts the corpus into the CSV (*) tabular format
 - Analysis Jupyter Notebooks:
    - [dataset-analysis-labelling.ipynb](super_mat/dataset-analysis-labelling.ipynb)
    - [dataset-analysis-linking.ipynb](super_mat/dataset-analysis-linking.ipynb)
    - [dataset-analysis-papers.ipynb](super_mat/dataset-analysis-papers.ipynb)
 
## Dataset information

## Reference

If you use the data, please consider citing the related paper: 

```
@article{doi:10.1080/27660400.2021.1918396,
author = {Luca Foppiano and Sae Dieb and Akira Suzuki and Pedro Baptista de Castro and Suguru Iwasaki and Azusa Uzuki and Miren Garbine Esparza Echevarria and Yan Meng and Kensei Terashima and Laurent Romary and Yoshihiko Takano and Masashi Ishii},
title = {SuperMat: construction of a linked annotated dataset from superconductors-related publications},
journal = {Science and Technology of Advanced Materials: Methods},
volume = {1},
number = {1},
pages = {34-44},
year  = {2021},
publisher = {Taylor & Francis},
doi = {10.1080/27660400.2021.1918396},

URL = { 
        https://doi.org/10.1080/27660400.2021.1918396
    
},
eprint = { 
        https://doi.org/10.1080/27660400.2021.1918396
    
}

}
```
 
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

The dataset is licensed under CC BY 4.0 CC. The [Bibliographic](data/biblio) data refers to the original content. 

The code is licences under Apache 2.0 
