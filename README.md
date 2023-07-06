# Feecc Analytics Backend

Feecc Analytics Backend is the main software for deploying analytics service for Feecc, a Web3 enabled production tracking system.

## Setup and run

### Via Docker (Recomended)

>Install Docker and Docker-compose first.

Run in the directory:

```
docker-compose up --build
```

By default, access port is `5002`.

### Full deployment

Run in the command line:

```
poetry install
```

> Warning! Don't forget to put **"SECRET_KEY**" (SHA265 secret key) and **"MONGO_CONNECTION_URL"** (MongoDB url. Example: `mongodb+srv://<login>:<pass>@<atlas url>.mongodb.net/<database>?retryWrites=true&w=majority`) to your environment variables.

Run using:

```
uvicorn app:api --host <IP> --port <PORT>
```

Test availability:
```
curl -X 'GET' 'http://<HOST>:<PORT>/api/v1/status'
```

If the response is `{"status":"ok"}`, then it's alright.

## Configuration

To configure your deployment edit the environment variables, provided in `.env` file.

Environment variables:

- `MONGO_CONNECTION_URL` — your connection URI to MongoDB;
- `MONGO_DATABASE_NAME` — a database name of MongoDB;
- `SECRET_KEY` — secret key for hashing and dehashing;
- `IPFS_GATEWAY_HOST` — URL of IPFS Gateway;
- `USE_DATALOG` — sending analytics data to Robonomics (`true` or `false`);
- `ROBONOMICS_SEED` — seed-phrase for Robonomics account.

## API

For more information about endpoints, data flows and main operations, go to `http://<HOST>:<PORT>/docs`

Endpoints usage examples:

### Security

- /token

    POST: Log in to get auth bearer token. Request body: `{"username": string, "password": string}`

    Example: Returns `{"access_token": "string", "token_type": "string"}` if auth was successfull, `{"detail": "Incorrect username or password" or "validation error"}` otherwise.

### User management

- /api/v1/users/me

    GET: Information about user, using bearer token

    Example: `{"username":"username", "is_admin": false}`

### Database wrapper

> You need to log in and get a Bearer token to make API requests.

- `/api/v1/employees`

  GET: List of all employees and their overall count.

  Query params: If you want to get first 20 employees, make GET `/api/v1/employees?start=0&limit=20`. Start (*0* by default), Limit (*None* by default). To get all employees use GET `/api/v1/employees` without any params.

  > Note: "count" field does not depend on requested data

  Example:
  ```
  {"count": 1, "data": [{"rfid_card_id": "123", "name": "My Name", "position": "Engineer"}]}
  ```

- `/api/v1/employees/<rfid_card_id:string>`

  GET: Information about concrete employee by his rfid_card_id.

  Example: GET on ``/api/v1/employees/123`` returns:
  ```
  {"rfid_card_id": "123", "name": "My Name", "position": "Engineer"}
  ```

- `/api/v1/passports`

  GET: List of all passports and their overall count.

  Query params: If you want to get first 20 passports, make GET `/api/v1/passports?start=0&limit=20`. Start (*0* by default), Limit (*None* by default). To get all passports use GET `/api/v1/passports` without any params.

  > Note: "count" field does not depend on requested data

  Example:
  ```
  {"count": 1, "data": [{"model": "cryptoanalyzer", "uuid": "zxcqwer123","internal_id": "1","passport_short_url": "example.com","is_in_db": true}]}
  ```

- `/api/v1/passports/<internal_id:string>`

  GET: Information about passport by its internal_id.

  Example: GET on ``/api/v1/passports/1`` returns:
  ```
  {"model": "cryptoanalyzer", "uuid": "zxcqwer123","internal_id": "1","passport_short_url": "example.com","is_in_db": true}
  ```

- `/api/v1/stages`

  GET: List of all stages and their overall count.

  Query params: If you want to get first 20 passports, make GET `/api/v1/stages?start=0&limit=20`. Start (*0* by default), Limit (*None* by default). To get all stages use GET `/api/v1/stages` without any params.

  > Note: "count" field does not depend on requested data

  Example:
  ```
  {"count": 1, "data": [{"name": "stage","employee_name": "hashed_employee","parent_unit_uuid": "kldsjl1","session_start_time": "03-09-2021 17:04:05","session_end_time": "03-09-2021 17:04:07","video_hashes":["some_ipfs_hashes"],"additional_info": {}, "id": "zxc1", "is_in_db": true,"creation_time": "2021-09-03T14:04:05.360000"}]}
  ```

- `/api/v1/stages/<stage_id:string>`

  GET: Information about passport by its stage_id.

  Example: GET on `/api/v1/stages/zxc1` returns:
  ```
  {"name": "stage","employee_name": "hashed_employee","parent_unit_uuid": "kldsjl1","session_start_time": "03-09-2021 17:04:05","session_end_time": "03-09-2021 17:04:07","video_hashes":["some_ipfs_hashes"],"additional_info": {}, "id": "zxc1", "is_in_db": true,"creation_time": "2021-09-03T14:04:05.360000"}
  ```
