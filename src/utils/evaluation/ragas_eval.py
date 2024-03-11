from datasets import Dataset
import asyncio
# from src.query_engine import RAG
from src.utils.logging import Logger
from ragas import evaluate
from ragas.metrics import (
 faithfulness,
 answer_relevancy,
 context_recall,
 context_precision,
)

class RagasEval:
    def __init__(self, rag = None):
        self.rag = rag

    async def evaluate_rag(self, rag):
        questions = ["Как подготовить пространство для новой жизни?",
                    "Какие есть способы влияния на реальность?",
                    "Как восстановить дугу интституции?",
        ]

        ground_truths = [["Избавиться от ненужных вещей: Всё, чем вы не пользуетесь, что вам не нужно, следует отдать, продать или выбросить. Это может касаться различных предметов, включая одежду, которая вам больше не нравится или которая кажется вам ненужной. Уменьшить визуальный шум: Важно осознать, что многие этикетки, наклейки и стикеры на товарах созданы, чтобы привлекать ваше внимание. Следует удалять всё это, чтобы снизить нагрузку на психику. Предметы следует раскладывать по ячейкам и скрывать в тумбочках, стеллажах, на полках, чтобы сосредоточиться на главном – перестройке себя и создании новой стратегии вашей жизни."],
        ["Интеллект: Использование умственных способностей и знаний для влияния на окружающий мир. Материальный мир: Влияние через материальные ресурсы и физические объекты. Тело: Использование физической силы, здоровья и личной привлекательности. Социальный капитал, влияние и навык: Воздействие через социальные связи, репутацию и умение общаться. Искусство образов: Создание и использование визуальных и концептуальных образов для влияния на восприятие и поведение людей. "],
        ["Изменение Восприятия Возможностей: Необходимо преодолеть пессимистическое видение жизни и иррациональные убеждения о том, что что-то невозможно или не получится. Это влияет на энерговыдачу организма и на способность достигать целей. Иррациональная Вера в Возможности: Важно иметь веру в то, что всё возможно, независимо от обстоятельств. Это может быть вера через религию, эзотерику, или понимание причинно-следственных связей в мире. Работа над Конкретной Цепочкой Действий: Необходимо подобрать и следовать определённому плану действий, который приведёт к желаемому результату. Использование Примеров Успеха Других: Опираясь на примеры людей, которые смогли добиться успеха, закрыть для себя вопрос о возможности или невозможности радикального улучшения своей жизни."]]
        answers = []
        contexts = []

        async def process_query(rag, query):
            try:
                return await rag.take_answer(query)
            except Exception as e:
                print(f"Error processing query '{query}': {e}")
                return {"response_text": None, "contexts": None}

        responses = await asyncio.gather(*(process_query(rag, query) for query in questions))
        for resp in responses:
            answers.append(resp["response_text"])
            contexts.append(resp["contexts"])


        # To dict
        data = {
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truths": ground_truths
        }

        Logger().log('Data.Data.Data')
        Logger().log(data)


        # Convert dict to dataset
        dataset = Dataset.from_dict(data)

        result = evaluate(
            dataset = dataset,
            metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
            ],
        )

        Logger().log("Evaluation.Evaluation.Evaluation.")
        Logger().log(result.to_pandas)

        return result
