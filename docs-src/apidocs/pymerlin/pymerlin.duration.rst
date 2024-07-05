:py:mod:`pymerlin.duration`
===========================

.. py:module:: pymerlin.duration

.. autodoc2-docstring:: pymerlin.duration
   :parser: myst
   :allowtitles:

Module Contents
---------------

Classes
~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Duration <pymerlin.duration.Duration>`
     - .. autodoc2-docstring:: pymerlin.duration.Duration
          :parser: myst
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`ZERO <pymerlin.duration.ZERO>`
     - .. autodoc2-docstring:: pymerlin.duration.ZERO
          :parser: myst
          :summary:
   * - :py:obj:`MICROSECOND <pymerlin.duration.MICROSECOND>`
     - .. autodoc2-docstring:: pymerlin.duration.MICROSECOND
          :parser: myst
          :summary:
   * - :py:obj:`MICROSECONDS <pymerlin.duration.MICROSECONDS>`
     - .. autodoc2-docstring:: pymerlin.duration.MICROSECONDS
          :parser: myst
          :summary:
   * - :py:obj:`MILLISECOND <pymerlin.duration.MILLISECOND>`
     - .. autodoc2-docstring:: pymerlin.duration.MILLISECOND
          :parser: myst
          :summary:
   * - :py:obj:`MILLISECONDS <pymerlin.duration.MILLISECONDS>`
     - .. autodoc2-docstring:: pymerlin.duration.MILLISECONDS
          :parser: myst
          :summary:
   * - :py:obj:`SECOND <pymerlin.duration.SECOND>`
     - .. autodoc2-docstring:: pymerlin.duration.SECOND
          :parser: myst
          :summary:
   * - :py:obj:`SECONDS <pymerlin.duration.SECONDS>`
     - .. autodoc2-docstring:: pymerlin.duration.SECONDS
          :parser: myst
          :summary:
   * - :py:obj:`MINUTE <pymerlin.duration.MINUTE>`
     - .. autodoc2-docstring:: pymerlin.duration.MINUTE
          :parser: myst
          :summary:
   * - :py:obj:`MINUTES <pymerlin.duration.MINUTES>`
     - .. autodoc2-docstring:: pymerlin.duration.MINUTES
          :parser: myst
          :summary:
   * - :py:obj:`HOUR <pymerlin.duration.HOUR>`
     - .. autodoc2-docstring:: pymerlin.duration.HOUR
          :parser: myst
          :summary:
   * - :py:obj:`HOURS <pymerlin.duration.HOURS>`
     - .. autodoc2-docstring:: pymerlin.duration.HOURS
          :parser: myst
          :summary:

API
~~~

.. py:class:: Duration(micros)
   :canonical: pymerlin.duration.Duration

   .. autodoc2-docstring:: pymerlin.duration.Duration
      :parser: myst

   .. rubric:: Initialization

   .. autodoc2-docstring:: pymerlin.duration.Duration.__init__
      :parser: myst

   .. py:method:: times(scalar)
      :canonical: pymerlin.duration.Duration.times

      .. autodoc2-docstring:: pymerlin.duration.Duration.times
         :parser: myst

   .. py:method:: plus(other)
      :canonical: pymerlin.duration.Duration.plus

      .. autodoc2-docstring:: pymerlin.duration.Duration.plus
         :parser: myst

   .. py:method:: negate()
      :canonical: pymerlin.duration.Duration.negate

      .. autodoc2-docstring:: pymerlin.duration.Duration.negate
         :parser: myst

   .. py:method:: of(scalar, unit)
      :canonical: pymerlin.duration.Duration.of
      :staticmethod:

      .. autodoc2-docstring:: pymerlin.duration.Duration.of
         :parser: myst

   .. py:method:: from_string(duration_string)
      :canonical: pymerlin.duration.Duration.from_string
      :staticmethod:

      .. autodoc2-docstring:: pymerlin.duration.Duration.from_string
         :parser: myst

   .. py:method:: __repr__()
      :canonical: pymerlin.duration.Duration.__repr__

   .. py:method:: __eq__(other)
      :canonical: pymerlin.duration.Duration.__eq__

   .. py:method:: __gt__(other)
      :canonical: pymerlin.duration.Duration.__gt__

   .. py:method:: __ge__(other)
      :canonical: pymerlin.duration.Duration.__ge__

   .. py:method:: __lt__(other)
      :canonical: pymerlin.duration.Duration.__lt__

   .. py:method:: __le__(other)
      :canonical: pymerlin.duration.Duration.__le__

.. py:data:: ZERO
   :canonical: pymerlin.duration.ZERO
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.ZERO
      :parser: myst

.. py:data:: MICROSECOND
   :canonical: pymerlin.duration.MICROSECOND
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.MICROSECOND
      :parser: myst

.. py:data:: MICROSECONDS
   :canonical: pymerlin.duration.MICROSECONDS
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.MICROSECONDS
      :parser: myst

.. py:data:: MILLISECOND
   :canonical: pymerlin.duration.MILLISECOND
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.MILLISECOND
      :parser: myst

.. py:data:: MILLISECONDS
   :canonical: pymerlin.duration.MILLISECONDS
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.MILLISECONDS
      :parser: myst

.. py:data:: SECOND
   :canonical: pymerlin.duration.SECOND
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.SECOND
      :parser: myst

.. py:data:: SECONDS
   :canonical: pymerlin.duration.SECONDS
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.SECONDS
      :parser: myst

.. py:data:: MINUTE
   :canonical: pymerlin.duration.MINUTE
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.MINUTE
      :parser: myst

.. py:data:: MINUTES
   :canonical: pymerlin.duration.MINUTES
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.MINUTES
      :parser: myst

.. py:data:: HOUR
   :canonical: pymerlin.duration.HOUR
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.HOUR
      :parser: myst

.. py:data:: HOURS
   :canonical: pymerlin.duration.HOURS
   :value: None

   .. autodoc2-docstring:: pymerlin.duration.HOURS
      :parser: myst
