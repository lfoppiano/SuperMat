.. _GitLab project page: https://gitlab.nims.go.jp/lfoppiano/SuperMat/issues

.. _Guidelines:

Material parser Guidelines
##########################

This section provides the guidelines for the material parser.
The material parser assume that the input string is a material name and outputs such name segmenting various components, such as formula, name, doping ratio etc.. more details below.

Notations
*********

In this guidelines we use only the XML notation where each class is represented by a ``<class_name>`` tag.
    .. code-block:: xml
        <?xml version="1.0" encoding="utf-8" ?>
        <materials>
	        <material><formula>LaFeAsO 1−x H x</formula></material>
	        <material><formula>LaFeAsO1−xHx</formula></material>
	        <material><formula>LaFeAsO 1−x H x</formula></material>
            [...]


Data quality
************

The "pre-annotated" data can for this model may contains mistakes or be incomplete. The quality depends on external causes and often incorrect data cannot be fixed.
It may happens happens that the upstream model is not able to extract the material correctly, or a formula is truncated irremediably.
For example the formula ``0.1 Cu O 7`` misses the initial material.
**All lines that contains mistakes should be ignored** using the notation ``<!-- -->``.

Tag set
*******

The component to be annotated are:

 - :ref:`name`

 - :ref:`formula`

 - :ref:`doping`

 - :ref:`shape`

 - :ref:`fabrication`

 - :ref:`substrate`

 - :ref:`variables`

In each section we provide a ``Motivation`` section which describes why such data is important, and ``Utilisation``, describing how we plan to use the data.

.. _name:

Material name
=============

Represent the canonical name of a material

**Tag**: ``<name>``

Examples:

- PCCO
- PCO
- Metal diboride
- hydryde
- carbon

.. _formula:

Formula
=======

Identify the material as expressed from the chemical formula

**Tag**: ``<formula>``

Examples:

- Pr1.869Ce0.131CuO 4−δ
- MgB2
- La 2-x Sr x CuO 4

.. _doping:

Doping
======

Identify the doping ratio and doping materials that are adjointed to the material name

**Tag**: ``<doping>``

Examples:

- overdoped
- underdopded
- optimally doped
- bulk
- pure
- ``Zn-doped`` should be annotated as ``<doping>Zn</doping>-doped``
- ``Zn concentration`` should be annotated as ``<doping>Zn concentration</doping>``
- ``1% Zn`` should be annotated as ``<doping>1% Zn</doping>``


.. _shape:

Shape
=====

Identify the shape of the material,

**Tag**: ``<shape>``

Examples:

- ``single crystal``
- ``polycrystaline``
- ``thin film``
- ``powder``
- ``film``


.. _variables:

Variables
=========

.. _values:

Identify the variables that can be substituted in the formula.

**Tag**: ``<variable>``

Examples:

- ``La x Fe 1-x O 7 with x < 3``, the variable should be ``x`` as ``La x Fe 1-x O 7 with <variable>x</variable> < 3``
- ``La x Fe 1-x O 7 with 1 < x < 3``, the variable should be ``x``  as ``La x Fe 1-x O 7 with 1 < <variable>x</variable> < 3``
- ``La x Fe 1-x O 7 with x = 1,2,3, and 4``, the variable should be ``x``` as ``La x Fe 1-x O 7 with <variable>x</variable> = 1,2,3, and 4``
- ``La x Fe y O 7 with x = 1,2,3, and 4 and y = 2,3,4`` the variables should be ``x`` and ``y`` as ``La x Fe y O 7 with <variable>x</variable> = 1,2,3, and 4 and <variable>y</variable> = 2,3,4``

Values
======

Identify the values expressed in the stoichiometric doping.

**Tag**: ``<value>``

Examples:

- ``La x Fe 1-x O 7 with x < 3``, the value should be ``< 3`` as ``La x Fe 1-x O 7 with x <value>< 3</value>``
- ``La x Fe 1-x O 7 with 1 < x < 3``, the value should be ``< 3`` and ``1 <`` as ``La x Fe 1-x O 7 with <value>1 <</value> x <value>< 3</value>``
- ``La x Fe 1-x O 7 with x = 1,2,3, and 4``, the value should be ``1,2,3, and 4`` as ``La x Fe 1-x O 7 with x = <value>1,2,3, and 4</value>``

.. _substrate:

Substrate
=========

Identify the substrates as defined in the material name

**Tag**: ``<substrate>``

Examples:

- ``PCCO films onto Pr 2 CuO 4 (PCO)/SrTiO 3``` the substrate should be annotated as ``PCCO films onto <substrate>Pr 2 CuO 4 (PCO)/SrTiO 3</substrate>```

.. _fabrication:

Fabrication
===========

Represent all the various information that are not belonging to any of the previous tags

Examples:

 - ``HfNCl containing cointercalated tetrahydrofuran solvent (THF)``
 - ``intercalated``
 - ``synthesized by MBE method``
 - ``electron-doped``
 - ``hole-doped``
