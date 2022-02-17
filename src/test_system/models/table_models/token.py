# std
from hashlib import sha3_512
from datetime import datetime
from typing import List, Optional
# custom
from test_system.constants import MAX_HASH_GENERATION_TRY_COUNT
from test_system.models.database import db
from .answers import EvaluableTestAnswer
from .test import Test


class Token(db.Model):
    __tablename__ = "token"

    token = db.Column(db.String, primary_key=True)
    max_usage_count: db.Column = db.Column(db.Integer)
    personal_data_test_name = db.Column(db.String, db.ForeignKey("test.name"))
    pre_collect_test_names = db.Column(db.ARRAY(db.String))  # references name (column) from test (table)
    evaluable_test_name = db.Column(db.String, db.ForeignKey("test.name"))
    creation_timestamp = db.Column(db.TIMESTAMP)

    personal_data_test = db.relationship("Test", foreign_keys=[personal_data_test_name])
    evaluable_test = db.relationship("Test", foreign_keys=[evaluable_test_name])

    @classmethod
    def generate_token(cls,
                       max_usage_count: Optional[int],
                       personal_data_test_name: str,
                       pre_collect_test_names: List[str],
                       evaluable_test_name: str) -> "Token":
        for _ in range(MAX_HASH_GENERATION_TRY_COUNT):
            token_hash = cls._generate_hash()
            if cls.query.filter_by(token=token_hash).first() is None:
                break
        else:
            raise RuntimeError(f"Couldn't generate an unknown hash within {MAX_HASH_GENERATION_TRY_COUNT} tries.")
        return cls(token=token_hash,
                   max_usage_count=max_usage_count,
                   personal_data_test_name=personal_data_test_name,
                   pre_collect_test_names=pre_collect_test_names,
                   evaluable_test_name=evaluable_test_name)

    @staticmethod
    def _generate_hash() -> str:
        now = datetime.now()
        token_seed = str(now).encode()
        token_hash = sha3_512(token_seed).hexdigest()
        return token_hash

    def __init__(self, **kwargs):
        if "creation_timestamp" not in kwargs:
            kwargs["creation_timestamp"] = db.func.now()
        super(Token, self).__init__(**kwargs)

    def __repr__(self):
        return (f"Token '{self.token}' ("
                f"personal data test: {self.personal_data_test_name}, "
                f"pre collect Tests: {self.pre_collect_test_names}, "
                f"evaluable test: {self.evaluable_test_name}, "
                f"usages: {self.max_usage_count})")

    def is_expired(self, remove_if_expired: bool = False) -> bool:
        expired = self.max_usage_count is not None and self.max_usage_count <= 0
        if remove_if_expired and expired:
            db.session.delete(self)
            db.session.commit()
        return expired

    def use_for(self, evaluable_test_answer: EvaluableTestAnswer) -> None:
        evaluable_test_answer.was_evaluated_with_token = True
        if self.max_usage_count is not None:
            self.max_usage_count -= 1
            db.session.commit()

    def get_pre_collect_tests(self) -> List[Test]:
        possible_pre_collect_tests = [Test.query.filter_by(name=pre_collect_test_name).first()
                                      for pre_collect_test_name in self.pre_collect_test_names]
        pre_collect_tests = list(filter(lambda test: test is not None, possible_pre_collect_tests))
        return pre_collect_tests
