from textwrap import dedent

from wfx.components.data import URLComponent
from wfx.components.input_output import ChatOutput, TextInputComponent
from wfx.components.models import LanguageModelComponent
from wfx.components.models_and_agents import PromptComponent
from wfx.components.processing import ParserComponent
from wfx.graph import Graph


def blog_writer_graph(template: str | None = None):
    if template is None:
        template = dedent("""Reference 1:

{references}

---

{instructions}

Blog:
""")
    url_component = URLComponent()
    url_component.set(urls=["https://prime.khulnasoft.com/", "https://docs.prime.khulnasoft.com/"])
    parse_data_component = ParserComponent()
    parse_data_component.set(input_data=url_component.fetch_content)

    text_input = TextInputComponent(_display_name="Instructions")
    text_input.set(
        input_value="Use the references above for style to write a new blog/tutorial about Primeagent and AI. "
        "Suggest non-covered topics."
    )

    prompt_component = PromptComponent()
    prompt_component.set(
        template=template,
        instructions=text_input.text_response,
        references=parse_data_component.parse_combined_text,
    )

    language_model_component = LanguageModelComponent()
    language_model_component.set(input_value=prompt_component.build_prompt)

    chat_output = ChatOutput()
    chat_output.set(input_value=language_model_component.text_response)

    return Graph(start=text_input, end=chat_output)
