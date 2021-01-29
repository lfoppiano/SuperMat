
[![Documentation Status](https://readthedocs.org/projects/supermat/badge/?version=latest)](https://supermat.readthedocs.io/en/latest/?badge=latest)


# SuperMat 
SuperMat (Superconductors Material) dataset is a manually **linked** **annotated** dataset of superconductors related materials and properties. 

## Content
 - Annotated dataset:
    - XML-TEI annotated fulltext data:
        - [Bibliographic](data/biblio) data references as XML-TEI or JSON (CORD-19) format
        - Sources are referenced in the [Bibliographic](data/biblio) data
    - Tabular version of the linked annotated entities in the dataset [CSV](data/csv/SuperMat-1.0.csv) (*)
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
@unpublished{foppiano:hal-03101177,
  TITLE = {{SuperMat: Construction of a linked annotated dataset from superconductors-related publications}},
  AUTHOR = {Foppiano, Luca and Dieb, Sae and Suzuki, Akira and Baptista de Castro, Pedro and Iwasaki, Suguru and Uzuki, Azusa and Esparza Echevarria, Miren Garbine and Meng, Yan and Terashima, Kensei and Romary, Laurent and Takano, Yoshihiko and Ishii, Masashi},
  URL = {https://hal.inria.fr/hal-03101177},
  NOTE = {working paper or preprint},
  YEAR = {2021},
  MONTH = Jan,
  PDF = {https://hal.inria.fr/hal-03101177/file/SuperMat__Construction_of_a_linked_annotated_dataset_from_superconductors_related_publications-1.pdf},
  HAL_ID = {hal-03101177},
  HAL_VERSION = {v2},
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
