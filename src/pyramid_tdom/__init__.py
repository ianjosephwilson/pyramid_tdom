from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Protocol
from string.templatelib import Template

from tdom.processor import ProcessContext, TemplateProcessor, IComponentProcessor, ComponentProcessor


PyramidTdomCtx = ContextVar[dict[str, object] | None]('PyramidTdomCtx', default=None)


class IProcessorService(Protocol):

    def process_template(self, template: Template, assume_ctx: ProcessContext | None = None) -> str:
        ...


_default_processor_ctx = ProcessContext()


@dataclass
class TdomRenderer:

    processor_api: IProcessorService

    def __call__(self, info):
        def render_func(value, system):
            if isinstance(value, Template):
                with PyramidTdomCtx.set(system):
                    return self.processor_api.process(
                        value, assume_ctx=_default_processor_ctx)
            else:
                # View function can delegate setting context variable values
                # during the render.  Just fail here if the wrong thing was returned
                # maybe we can do something smarter later that is still "fast-like".
                value_t, cvals = value
                with PyramidTdomCtx.set(system), ContextVarSetter(context_values=cvals):
                    return self.processor_api.process(
                        value_t, assume_ctx=_default_processor_ctx)
        return render_func


class ContextVarSetter:
    """
    Context manager for working with many context vars (instead of only 1).

    This is meant to be created, used immediately and then discarded.

    This allows for dynamically specifying a tuple of var / value pairs that
    another part of the program can use to wrap some called code without knowing
    anything about either.
    """

    context_values: tuple[tuple[ContextVar, object], ...]  # Cvar / value pair.
    tokens: tuple[Token, ...]

    def __init__(self, context_values=()):
        self.context_values = context_values
        self.tokens = ()

    def __enter__(self):
        """Set every given context var to its paired value."""
        self.tokens = tuple(var.set(val) for var, val in self.context_values)

    def __exit__(self, exc_type, exc_value, traceback):
        """Reset every given context var."""
        for idx, var_value in enumerate(self.context_values):
            var_value[0].reset(self.tokens[idx])


@dataclass
class SystemComponentProcessor(IComponentProcessor):
    """
    Make pyramid's `system` dict available to components as `pyramid_system`.
    """

    default_processor_api: IComponentProcessor = field(
        default_factory=lambda: ComponentProcessor())

    def process(
        self,
        template: Template,
        last_ctx: ProcessContext,
        component_callable: object,
        attrs: tuple[TAttribute, ...],
        component_template: Template,
        provided_attrs: tuple[Attribute, ...] = (),
    ) -> Template:
        system = PyramidTdomCtx.get()
        if system is not None:
            extended_attrs = provided_attrs + (
                ('pyramid_system', system),
            )
        return self.default_processor_api.process(
            template,
            last_ctx,
            component_callable,
            attrs,
            component_template,
            provided_attrs=extended_attrs)


def includeme(config):

    tp = TemplateProcessor(
        component_processor_api=SystemComponentProcessor(),
    )
    config.add_renderer(name='tdom', factory=TdomRenderer(processor_api=tp))
