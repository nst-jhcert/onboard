# Week4 Development Guide
## Project Structure
- Docker Compose를 사용하여 컨테이너를 분리하여 개발합니다.
- Python FastAPI를 사용하면서, swagger를 통해 문서도 동시에 작성할 수 있도록 합니다.
- React/Next.js 로 사용자가 웹에서 API를 편히 사용할 수 있게 프론트엔드를 구성합니다.
- 사용자가 웹 페이지에서 CSP/CCSDS 패킷을 생성하고 파싱하는 것이 1차 목표입니다.
- 사용자가 웹 페이지에서 ZeroMQ/MQTT 패킷을 실시간으로 모니터링하는 것이 2차 목표입니다.

## Rules
- 코드 작성 전 반드시 사용자의 지시를 기다립니다.
- 임의로 파일을 생성하거나 구조를 변경하지 않습니다.
- 사용자가 요구하지 않은 기능이나 개선을 추가하지 않습니다.
- 서비스 단위로 사용자에 의한 단위 테스트 및 커밋을 진행하려고 하니, 서비스 모듈 단위로 작업해주세요.

## Docker
- `docker-compose.yml`은 `week4/` 루트에 위치합니다.
- 각 서비스는 별도의 디렉토리에 `dockerfile`을 둡니다.
- 컨테이너 실행/중지는 사용자 확인 후 수행합니다.

## Conventions
- 이전 주차(week1~3)의 패턴을 참고하되, 사용자 지시를 우선합니다.
- dockerfile 파일명은 소문자 `dockerfile`을 사용합니다.
- README.md는 사용자가 요청할 때만 작성합니다.
- Google 스타일을 기준으로 코드 컨벤션을 맞춰주세요.



