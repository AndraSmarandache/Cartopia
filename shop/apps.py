from django.apps import AppConfig


class ShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shop'

    def ready(self):
        import sys
        if sys.version_info >= (3, 14):
            try:
                from django.template.context import BaseContext

                def _basecontext_copy(self):
                    # Create a new instance without calling __init__, then copy
                    # all regular attributes and finally shallow-copy dict stack
                    duplicate = self.__class__.__new__(self.__class__)
                    if hasattr(self, "__dict__"):
                        duplicate.__dict__.update(self.__dict__)
                    duplicate.dicts = self.dicts[:]
                    return duplicate

                BaseContext.__copy__ = _basecontext_copy
            except Exception:
                # If anything goes wrong, don't block app startup
                pass

        import shop.signals

