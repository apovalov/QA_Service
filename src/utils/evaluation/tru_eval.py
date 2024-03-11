import os
import numpy as np
from trulens_eval import Tru, Select
from trulens_eval.feedback import Feedback, Groundedness
from trulens_eval.feedback.provider.openai import OpenAI as fOpenAI
from trulens_eval.app import App

class TestEngine:
    def __init__(self, rag_chain=None):
        self.tru = Tru()
        self.tru.reset_database
        self.tru.run_dashboard()

        fopenai = fOpenAI()
        grounded = Groundedness(groundedness_provider=fopenai)


        # Define a groundedness feedback function
        self.f_groundedness = (
            Feedback(grounded.groundedness_measure_with_cot_reasons, name="Groundedness")
            .on(Select.RecordCalls.retrieve.rets.collect())
            .on_output()
            .aggregate(grounded.grounded_statements_aggregator)
        )

        # Question/answer relevance between overall question and answer.
        self.answer_relevance = (
            Feedback(fopenai.relevance_with_cot_reasons, name="Answer Relevance")
            .on(Select.RecordCalls.retrieve.args.query)
            .on_output()
        )

        # Question/statement relevance between question and each context chunk.
        self.context_relevance = (
            Feedback(fopenai.qs_relevance_with_cot_reasons, name="Context Relevance")
            .on(Select.RecordCalls.retrieve.args.query)
            .on(Select.RecordCalls.retrieve.rets.collect())
            .aggregate(np.mean)
        )


        if rag_chain:
            App.select_context(rag_chain)

        context = App.select_context(rag_chain)

        self.lc_groundedness = (
            Feedback(grounded.groundedness_measure_with_cot_reasons)
            .on(context.collect()) # collect context chunks into a list
            .on_output()
            .aggregate(grounded.grounded_statements_aggregator)
        )

        # Question/answer relevance between overall question and answer.
        self.lc_qa_relevance = Feedback(fopenai.relevance).on_input_output()
        # Question/statement relevance between question and each context chunk.
        self.lc_context_relevance = (
            Feedback(fopenai.qs_relevance)
            .on_input()
            .on(context)
            .aggregate(np.mean)
        )




