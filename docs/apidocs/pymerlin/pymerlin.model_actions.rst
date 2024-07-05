:py:mod:`pymerlin.model_actions`
================================

.. py:module:: pymerlin.model_actions

.. autodoc2-docstring:: pymerlin.model_actions
   :parser: myst
   :allowtitles:

Module Contents
---------------

Functions
~~~~~~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`_context <pymerlin.model_actions._context>`
     - .. autodoc2-docstring:: pymerlin.model_actions._context
          :parser: myst
          :summary:
   * - :py:obj:`_set_context <pymerlin.model_actions._set_context>`
     - .. autodoc2-docstring:: pymerlin.model_actions._set_context
          :parser: myst
          :summary:
   * - :py:obj:`_clear_context <pymerlin.model_actions._clear_context>`
     - .. autodoc2-docstring:: pymerlin.model_actions._clear_context
          :parser: myst
          :summary:
   * - :py:obj:`_set_yield_callback <pymerlin.model_actions._set_yield_callback>`
     - .. autodoc2-docstring:: pymerlin.model_actions._set_yield_callback
          :parser: myst
          :summary:
   * - :py:obj:`_clear_yield_callback <pymerlin.model_actions._clear_yield_callback>`
     - .. autodoc2-docstring:: pymerlin.model_actions._clear_yield_callback
          :parser: myst
          :summary:
   * - :py:obj:`delay <pymerlin.model_actions.delay>`
     - .. autodoc2-docstring:: pymerlin.model_actions.delay
          :parser: myst
          :summary:
   * - :py:obj:`spawn <pymerlin.model_actions.spawn>`
     - .. autodoc2-docstring:: pymerlin.model_actions.spawn
          :parser: myst
          :summary:
   * - :py:obj:`call <pymerlin.model_actions.call>`
     - .. autodoc2-docstring:: pymerlin.model_actions.call
          :parser: myst
          :summary:
   * - :py:obj:`wait_until <pymerlin.model_actions.wait_until>`
     - .. autodoc2-docstring:: pymerlin.model_actions.wait_until
          :parser: myst
          :summary:
   * - :py:obj:`_yield_with <pymerlin.model_actions._yield_with>`
     - .. autodoc2-docstring:: pymerlin.model_actions._yield_with
          :parser: myst
          :summary:

Data
~~~~

.. list-table::
   :class: autosummary longtable
   :align: left

   * - :py:obj:`Completed <pymerlin.model_actions.Completed>`
     - .. autodoc2-docstring:: pymerlin.model_actions.Completed
          :parser: myst
          :summary:
   * - :py:obj:`Delayed <pymerlin.model_actions.Delayed>`
     - .. autodoc2-docstring:: pymerlin.model_actions.Delayed
          :parser: myst
          :summary:
   * - :py:obj:`Calling <pymerlin.model_actions.Calling>`
     - .. autodoc2-docstring:: pymerlin.model_actions.Calling
          :parser: myst
          :summary:
   * - :py:obj:`Awaiting <pymerlin.model_actions.Awaiting>`
     - .. autodoc2-docstring:: pymerlin.model_actions.Awaiting
          :parser: myst
          :summary:

API
~~~

.. py:data:: Completed
   :canonical: pymerlin.model_actions.Completed
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: pymerlin.model_actions.Completed
      :parser: myst

.. py:data:: Delayed
   :canonical: pymerlin.model_actions.Delayed
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: pymerlin.model_actions.Delayed
      :parser: myst

.. py:data:: Calling
   :canonical: pymerlin.model_actions.Calling
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: pymerlin.model_actions.Calling
      :parser: myst

.. py:data:: Awaiting
   :canonical: pymerlin.model_actions.Awaiting
   :value: 'namedtuple(...)'

   .. autodoc2-docstring:: pymerlin.model_actions.Awaiting
      :parser: myst

.. py:function:: _context(scheduler, spawner=None)
   :canonical: pymerlin.model_actions._context

   .. autodoc2-docstring:: pymerlin.model_actions._context
      :parser: myst

.. py:function:: _set_context(context, spawner)
   :canonical: pymerlin.model_actions._set_context

   .. autodoc2-docstring:: pymerlin.model_actions._set_context
      :parser: myst

.. py:function:: _clear_context()
   :canonical: pymerlin.model_actions._clear_context

   .. autodoc2-docstring:: pymerlin.model_actions._clear_context
      :parser: myst

.. py:function:: _set_yield_callback(callback)
   :canonical: pymerlin.model_actions._set_yield_callback

   .. autodoc2-docstring:: pymerlin.model_actions._set_yield_callback
      :parser: myst

.. py:function:: _clear_yield_callback()
   :canonical: pymerlin.model_actions._clear_yield_callback

   .. autodoc2-docstring:: pymerlin.model_actions._clear_yield_callback
      :parser: myst

.. py:function:: delay(duration)
   :canonical: pymerlin.model_actions.delay
   :async:

   .. autodoc2-docstring:: pymerlin.model_actions.delay
      :parser: myst

.. py:function:: spawn(child)
   :canonical: pymerlin.model_actions.spawn

   .. autodoc2-docstring:: pymerlin.model_actions.spawn
      :parser: myst

.. py:function:: call(child)
   :canonical: pymerlin.model_actions.call
   :async:

   .. autodoc2-docstring:: pymerlin.model_actions.call
      :parser: myst

.. py:function:: wait_until(condition)
   :canonical: pymerlin.model_actions.wait_until
   :async:

   .. autodoc2-docstring:: pymerlin.model_actions.wait_until
      :parser: myst

.. py:function:: _yield_with(status)
   :canonical: pymerlin.model_actions._yield_with
   :async:

   .. autodoc2-docstring:: pymerlin.model_actions._yield_with
      :parser: myst
