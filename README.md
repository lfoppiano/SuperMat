
[![Documentation Status](https://readthedocs.org/projects/supermat/badge/?version=latest)](https://supermat.readthedocs.io/en/latest/?badge=latest)
[![Build unstable](https://github.com/lfoppiano/SuperMat/actions/workflows/ci-build.yml/badge.svg)](https://github.com/lfoppiano/SuperMat/actions/workflows/ci-build.yml)

# SuperMat 
SuperMat (Superconductors Material) dataset is a manually **linked** **annotated** dataset of superconductors related materials and properties. 

## Content
 - Annotated dataset:
    - Superconductors data:
        - [Bibliographic](data/biblio) data references as XML-TEI or JSON (CORD-19) format
        - Sources are referenced in the [Bibliographic](data/biblio) data
        - :warning: The annotations are not public due to copyright, however 
          - :fire: SuperMat can be considerd one of the few un-biased dataset for LLMs evaluation :fire: 
    - CSV of the linked annotated entities in the dataset [CSV](data/csv/SuperMat-1.0.csv) (*)
    - Material data for segmenting inorganic material names
 - Annotation guidelines:
    - [Online version](https://supermat.readthedocs.io)
    - [Changelog](docs/CHANGELOG.md)
    - [Source](docs), 
 - [Transformation scripts](scripts)
    - [tsv2xml](scripts/tsv2xml.py) / [xml2tsv](scripts/xml2tsv.py): Transformation from and to the INCEpTION TSV 3.2 format
    - [xml2csv](scripts/xml2csv.py): Converts the corpus into the CSV (*) tabular format
    - [xml2csv_entities](scripts/xml2csv_entities.py): Converts the corpus to CSV ignoring entity relations
    - [xml2LossyJSON.py](scripts/xml2LossyJSON.py): Converts the TEI-XML corpus to a Lossy JSON (based on CORD-19 dataset)
 - Analysis Jupyter Notebooks:
    - [dataset-analysis-labelling.ipynb](scripts/jupyter/dataset-analysis-labelling.ipynb)
    - [dataset-analysis-linking.ipynb](scripts/jupyter/dataset-analysis-linking.ipynb)
    - [dataset-analysis-papers.ipynb](scripts/jupyter/dataset-analysis-papers.ipynb)

Feel free to contact us for any information. 

## Reference

If you use the data, please consider citing the related paper: 

```bibtex
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

### Getting started

To use the scripts and analysis data 

```bash
conda create --name SuperMat pip
pip install -r requirements.txt 
```

### Conversion tools

```bash
python scripts/tsv2xml.py --help
```

### Analysis tools 

The analysis tools provide statistics and information from the dataset, they also run consistency checks of the format and content. 
Results can be seen directly on the repository. 

```bash
jupyter-lab
```

### Annotation guidelines

We use reStructured TExt using the utility [Sphinx](https://www.sphinx-doc.org/en/master/) which provide several output formats. Currently we support XML and PDF. 

To build this documentation locally, we recommend to create a virtual environment such as `virtualenv` or `conda`:  

```bash 
conda create -name guidelines 
conda activate guidelines
conda install sphinx
``` 

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

### Make a new release 

```bash
bump-my-version bump major|minor|patch 
```

## Licence

The dataset is licensed under CC BY 4.0 CC. The [Bibliographic](data/biblio) data refers to the original content. 

The code is licences under Apache 2.0 
