.. _Webanno: https://webanno.github.io/webanno/

Automatic Extraction of Superconductor-related information from Scientific Literature
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. toctree::
  :maxdepth: 3

  data-model.rst
  workflow.rst
  guidelines.rst
  annotation-tool.rst
  references.rst


Automatic collection of material information from research papers using Machine Learning (ML) and Natural Language Processing (NLP) is a needed milestone to ensure a sustainable process for enrich data bases in Material Informatics (MI). The availability of a large quantity of data provides an opportunity to apply TDM at large scale. New methods and approaches are required to keep up with the growing rate of newly available data and creation of new material databases. For example, the manual data collection used to populate SuperCon [1]_ cannot catch up with the massive fresh information from the increasing number of articles each year. It is then mandatory to consider new large-scale automatic processes for enriching SuperCon with additional information.
Although the general understanding of the necessity of TDM, the wide variation of writing styles and formats within the same research topics makes such task demanding new statistical approaches, which can bring deeper understanding of the domain.
This project aims to construct a system for the automatic collection of superconductor-related information from scientific literature using text mining techniques. The first step, then, consists of creating new high-quality annotated training data for superconductor research.

This documentation is organised as follow. The description of the project is articulated in four sections. First we describe the logical model, in :ref:`Data model`. The section :ref:`Annotation workflow` tackle our approach and process is organised. The core of this documentation is contained in section :ref:`Guidelines`, where all the rules followed by annotators are illustrated. :ref:`Annotation tools` describes how to use the annotation tool selected for this exercise: `Webanno`_.

For engineers we recommend to read the whole documentation. Domain experts can skip :ref:`Annotation workflow`, this section provides a view on the larger picture of the whole project.


.. [1] SuperCon `<http://supercon.nims.go.jp/>`_