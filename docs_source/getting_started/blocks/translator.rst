################
 The Translator
################

Amulet is built on top of a powerful translator which allows editing
data in any version of the users choice regardless of which platform and
game version the data originated in.

The translator will be further expanded upon in further examples but
this should introduce it and explain some of the methods to get you
started.

The translator for the level is found in
:attr:`~amulet.api.level.BaseLevel.translation_manager` and can be used
to find which platforms and versions are supported.
:meth:`~PyMCTranslate.py3.api.translation_manager.translation_manager.TranslationManager.platforms`
will give a list of the valid platforms and
:meth:`~PyMCTranslate.py3.api.translation_manager.translation_manager.TranslationManager.version_numbers`
will give a list of versions numbers for a given platform.

.. literalinclude:: translator.py
