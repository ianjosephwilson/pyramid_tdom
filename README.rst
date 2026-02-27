pyramid_tdom
~~~~~~~~~~~~

This is a simple implementation of a `Pyramid` `IRenderer` which renders "TDOM Compatible" Template objects with the `tdom` library.

Usage
=====


.. code-block:: python

    # in main() or subsequent includeme
    config.include('pyramid_tdom')

    # view callable returns `Template` directly
    def welcome_view(request):
        title = "Welcome to TDOM!"
        heading = "Welcome to TDOM!"
        return t'<!doctype html><html><body><head><title>{title}</title><meta chartset="utf8"></head><body><h1>{heading}</h1></body></html>'

    config.add_route("welcome", "/welcome")

    # set renderer via add_view or dynamically with `@view_config(renderer="tdom")`
    config.add_view(welcome_view, route_name="welcome", renderer="tdom", request_method="GET")
