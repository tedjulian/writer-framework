import json

from writer.abstract import register_abstract_template
from writer.ss_types import AbstractTemplate
from writer.workflows_blocks.blocks import WorkflowBlock


class WriterClassification(WorkflowBlock):

    @classmethod
    def register(cls, type: str):
        super(WriterClassification, cls).register(type)
        register_abstract_template("workflows_writerclassification", AbstractTemplate(
            baseType="workflows_node",
            writer={
                "name": "Writer Classification",
                "description": "Classify a text.",
                "category": "Content",
                "fields": {
                    "text": {
                        "name": "Text",
                        "type": "Text",
                    },
                    "categories": {
                        "name": "Categories",
                        "type": "Key-Value"
                    },
                    "additionalContext": {
                        "name": "Additional context",
                        "type": "Text",
                        "control": "Textarea"
                    },
                },
                "outs": {
                    "$dynamic": {
                        "field": "categories"
                    },
                    "error": {
                        "name": "Error",
                        "description": "If the function raises an Exception.",
                        "style": "error",
                    },
                },
            }
        ))

    def run(self):
        import writer.ai

        text = self._get_field("text")
        additional_context = self._get_field("additionalContext")
        categories = self._get_field("categories", as_json=True)
        # model_id = self._get_field("modelId")

        config = {}
        # if model_id:
        #     config["model"] = model_id

        try:
            prompt = f"""
Classify the text under “CONTENT” into one of the following categories:

{ json.dumps(categories) }

Your output should be only the key and not contain anything else. For example: { " , ".join(list(categories.keys())) }.

Additional context:

{ additional_context }

CONTENT:

{ text }
"""
            result = writer.ai.complete(prompt, config).strip()
            self.result = result
            self.outcome = f"$dynamic_{result}"
            print("result is")
            print(self.result)
            print(self.outcome)
        except BaseException as e:
            raise e
            self.result = "Text completion failed"
            self.outcome = "error"