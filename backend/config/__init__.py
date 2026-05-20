import sys


# Django 4.2's BaseContext.__copy__ implementation is incompatible with Python 3.14.
# Patch at startup so admin changelist pages can render until Django/Python versions are aligned.
if sys.version_info >= (3, 14):
	try:
		from django.template.context import BaseContext

		def _safe_base_context_copy(self):
			duplicate = self.__class__.__new__(self.__class__)
			duplicate.__dict__ = self.__dict__.copy()
			duplicate.dicts = self.dicts[:]
			return duplicate

		BaseContext.__copy__ = _safe_base_context_copy
	except Exception:
		# Do not block app startup if the patch can't be applied.
		pass
