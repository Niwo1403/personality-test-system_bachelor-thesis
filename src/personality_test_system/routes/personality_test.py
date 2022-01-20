# std
import json
# 3rd party
from flask import request, abort
# custom
from personality_test_system import app
from personality_test_system.constants import API_PREFIX
from personality_test_system.models import db, Token, Test


@app.route(f'{API_PREFIX}/tests/', methods=['GET'])
def get_tests():
    request_token = request.args.get("token", type=str)
    if request_token is None:
        abort(400, "Token missing.")

    token = db.session.query(Token).filter_by(token=request_token).first()
    if token is None or token.is_expired():
        abort(401, "Token doesn't exist or is expired.")

    tests = db.session.query(Test).filter(Test.name.in_(token.test_names)).all()

    test_names = ', '.join(test.name for test in tests)
    app.logger.info(f"Requested tests '{test_names}' with token '{token.token}'.")

    descriptions = json.dumps([test.description_json for test in tests])
    return descriptions
