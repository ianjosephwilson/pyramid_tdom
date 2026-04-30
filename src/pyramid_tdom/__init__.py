from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Protocol

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
            with PyramidTdomCtx.set(system):
                return self.processor_api.process(
                    value, assume_ctx=_default_processor_ctx)
        return render_func


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
