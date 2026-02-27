from dataclasses import dataclass

from tdom.processor import ProcessContext, cached_processor_service_factory


@dataclass
class TdomRenderer:

    # @TODO: Use a protocol here, probably need one in TDOM itself that just
    # mirrors the one method we care about.
    processor_api: ProcessorService

    def make_process_context(self, system):
        system_ext = {
            "tdom_processor_api": self.processor_api,
            **system
        }
        return ProcessContext(parent_tag='div', ns='html', system=system_ext)

    def __call__(self, info):
        def render_func(value, system):
            return self.processor_api.process_template(
                value,
                assume_ctx=self.make_process_context(system))
        return render_func


def includeme(config):
    config.add_renderer(name='tdom', factory=TdomRenderer(processor_api=cached_processor_service_factory()))
