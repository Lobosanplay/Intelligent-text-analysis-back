from transformers import pipeline

generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-large",
    max_length=256,
)


class QAService:
    def generate_answer(self, question: str, context: str) -> str:
        try:
            prompt = f"""
            Answer ONLY using the provided context.

            If the answer is not explicitly stated in the context, reply exactly:

            "No relevant information found in the document."

            Do not infer.
            Do not guess.
            Do not use outside knowledge.

            Context:
            {context}

            Question:
            {question}
            """

            output = generator(prompt)
            return output[0]["generated_text"]
        except Exception as e:
            raise Exception("error generating response", e)

    async def generate_title(self, summary: str) -> str:
        prompt = f"""
        Generate a short title max 6 words for this document:

        {summary}
        """

        output = generator(prompt, max_length=20)
        return output[0]["generated_text"].strip()


qa_service = QAService()
