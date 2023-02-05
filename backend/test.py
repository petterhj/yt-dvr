import fastapi
import starlette.testclient
from pydantic import BaseModel, Field

app = fastapi.FastAPI()

class DbModel(BaseModel):
    foo: str = Field(alias='bar')

class OutModel(BaseModel):
    foo: str
    
    class Config:
        allow_population_by_field_name = True

@app.get(
    '/test',
    response_model=OutModel,
    # response_model_by_alias=True,
)
def test():
    foo = DbModel(bar="foo")
    print(foo)
    print(foo.dict()) # {'foo': 'foo'}
    return foo#.dict()


with starlette.testclient.TestClient(app) as test_client:
    try:
        print(test_client.get('/test').json())
    except Exception as exc:
        print(exc)