from fastapi import FastAPI

api = FastAPI(
    title="ONBOARD-WEEK1",
    description="""
## ONBOARD-WEEK1
### 목표
- 컨테이너로 분리된 API 서버를 구현합니다.
### 기술스택
- FastAPI
- Docker
""", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@api.get("/", summary="고정된 문자열을 출력합니다.", tags=["WEEK1"])
async def get_helloworld():
    return "Hello World!"