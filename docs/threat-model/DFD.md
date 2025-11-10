# DFD — Data Flow Diagram (Wishlist Project)


```mermaid
flowchart LR
  subgraph Client[Trust Boundary: Client]
    U[User / Browser]
  end

  subgraph Edge[Trust Boundary: Edge]
    U -->|F1: HTTPS + JWT| API[FastAPI Backend]
    API -->|F2: Internal call| AUTH[Auth Middleware]
    API -->|F3: CRUD /wishes| APP[Wish Service]
  end

  subgraph Core[Trust Boundary: Core]
    APP -->|F4: SQL queries| DB[(Database)]
    APP -->|F5: Export job| FILES[(User Export File)]
  end

  subgraph DevOps[Trust Boundary: DevOps]
    CI[GitHub Actions] -->|F6: Security scan| CODE[Repository / Dependencies]
  end

  style API stroke-width:2px
  style DB stroke-width:2px
  style Edge stroke-dasharray:3 3
  style Core stroke-dasharray:3 3
  style DevOps stroke-dasharray:3 3
```

| ID     | Откуда → Куда              | Канал / Протокол           | Данные / PII                       | Комментарий                                                  | Связь с NFR    |
| ------ | -------------------------- | -------------------------- | ---------------------------------- | ------------------------------------------------------------ | -------------- |
| **F1** | User → API                 | HTTPS + JWT                | Credentials, Tokens                | Вход, регистрация, аутентификация (AuthN)                    | NFR-02         |
| **F2** | API → Auth Middleware      | Python func     | user_id, token                     | Проверка токена и прав доступа (AuthZ)                       | NFR-01         |
| **F3** | API → Wish Service         | FastAPI router             | title, link, price_estimate, notes | CRUD-операции, валидация входных данных                      | NFR-03, NFR-04 |
| **F4** | Wish Service → SQLite      | SQL            | wishes, owner_id                   | Запись/чтение данных владельца; контроль целостности         | NFR-08         |
| **F5** | Wish Service → Export File | JSON/CSV      | Wishes data (owner only)           | Генерация экспорта, ограничение размера и времени            | NFR-06         |
| **F6** | CI/CD → Repo/Dependencies  | GitHub Actions | configs          | Автоматическая проверка зависимостей (SCA)                   | NFR-07         |
| **F7** | User → API                 | HTTPS                      | CRUD requests                      | Нагрузочное использование; производительность (p95 ≤ 200 мс) | NFR-05         |
