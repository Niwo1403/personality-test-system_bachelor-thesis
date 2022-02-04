# custom
from test_system.models.database import db


class EvaluableTestAnswer(db.Model):  # consists of multiple EvaluableQuestionAnswers
    __tablename__ = "evaluable_test_answer"

    id = db.Column(db.Integer, primary_key=True)
    was_evaluated_with_token = db.Column(db.BOOLEAN, default=False)
    test_answer_id = db.Column(db.Integer, db.ForeignKey("test_answer.id"))
    question_answers = db.relationship("EvaluableQuestionAnswer")