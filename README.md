# Проект установки N8N, Minio, Tesseract OCR в Docker

Пререквизиты:

- Docker.Desktop (windows) https://www.docker.com/products/docker-desktop/

# Установка

## 0. Полная очистка Docker от всего

ЕСЛИ требуется полностью очистить Docker перед началом сборки, выполнить
`docker system prune --all --volumes --force`

## 1. Настроить Docker.Desktop

Секция Docker engine:
```
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "max-concurrent-downloads": 3,
  "max-download-attempts": 5,
  "registry-mirrors": [
    "https://hub.rat.dev",
    "https://mirror.ccs.tencentyun.com",
    "https://registry.cn-hangzhou.aliyuncs.com",
    "https://docker.m.daocloud.io"
  ]
}
```

## 2. Собрать образ (выполнять команды в cmd в папке с docker-compose.yml)

`docker compose up -d --build`


# Troubleshooting

## Проверка запущен ли tesseract
`docker inspect tesseract-api --format='{{json .State.Health}}'`
`docker compose exec n8n wget -qO- http://tesseract-api:8000/docs`

## Запущен ли MinIO?
`docker ps --filter "name=minio" --format "table {{.Status}}"`

## Что в логах MinIO? (ищем причину падения)
`docker logs minio --tail 30`

## Видит ли n8n контейнер minio по DNS?
`docker exec n8n ping -c 2 minio`

## Тест из контейнера n8n в MinIO
`docker exec n8n wget --spider -S http://minio:9000/minio/health/live`
Должно вернуть: 200 OK

## Тест из контейнера n8n в Tesseract
`docker exec n8n wget -qO- http://tesseract-api:8000/docs | Select-String "FastAPI"`
Должно вернуть HTML с упоминанием FastAPI

## проверка runner
`docker exec python-runner env | Select-String -Pattern "RUNNERS_AUTH_TOKEN"`
`docker exec n8n env | Select-String -Pattern "RUNNERS_AUTH_TOKEN"`

## проверка все ли контейнеры в общей сети

1. Найти точное имя сети
`docker network ls --filter "name=n8n"`

2. Подставить найденное имя в inspect
`docker network inspect <ТОЧНОЕ_ИМЯ_ИЗ_ВЫВОДА> --format "{{range .Containers}}{{.Name}} {{end}}"`
`docker network inspect n8n-minio-tesseract_n8n-network --format "{{range .Containers}}{{.Name}} {{end}}"`

# Проверка заняты ли порты в Windows
`netstat -ano | findstr :9000`

# Настройка mc и доступов к контейнеру MINIO
```
# 1. Зайди в контейнер minio
docker exec -it minio sh

# 2. Внутри контейнера: настрой алиас с правильными креденшиалами
mc alias set local http://localhost:9000 minioadmin minioadmin

# 3. Создай бакет (если не существует)
mc mb local/ocr

# 4. Дай публичный доступ на чтение (опционально, для тестов)
mc anonymous set download local/ocr

# 5. Проверь список файлов
mc ls local/ocr

# 6. Выйди из контейнера
exit
```
## Пересборка модификации образа

После изменений, например, N8N в docker-file.yml, выполнить команды:
```
docker compose down
docker compose build --no-cache n8n   # обязательно пересобрать образ с no-cache
docker compose up -d
```

## Полная пересборка

```
docker compose config 
# docker compose down -v - !!!! с очисткой volumes и потерей всех данных
docker compose down
docker builder prune -f
docker compose build --no-cache 
# docker compose up -d minio n8n tesseract-api
docker compose up -d
```

