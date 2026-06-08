# Backend API + credentials discipline

Load this reference when frontend code needs to hit a backend API, when you need
a dev token, or when credentials are missing.

## Frontend → backend API

When code needs a real backend response:

```
1. No credentials configured? → ask the user → save to .agent/credentials.json
   (chmod 600, listed in .gitignore via setup)
2. Need a response? → check .agent/data/<endpoint-slug>.json first
3. Not cached? → make a real request, save the response, then use it
```

This makes UI iteration fast (no live requests on every reload) and reproducible
(committed fixture data would be ideal — but only commit if the payload is
non-sensitive).

### Cache layout

```
.agent/
  credentials.json          gitignored
  data/
    auth-login.json
    users-list.json
    products-detail-42.json
```

Cache key convention: `<resource>-<action>[-<id>].json`. Hyphens, lowercase,
no slashes.

### Invalidating cache

When the API contract changes:
1. Delete the affected `.agent/data/*.json` file
2. Make a fresh request
3. Update any UI code that expected the old shape

Don't edit cache files by hand. Refetch.

## Backend (dev token workflow)

When testing a backend endpoint that needs auth in development:

```
1. Complete the endpoint implementation
2. Generate a dev token (project-specific command)
3. Test the endpoint with the token (curl, httpie, REST client)
4. Discard the token at end of session
```

If you MUST persist a token between commands within a session:
- Write to `.agent/.tmp/dev-token` (gitignored scratch space)
- `chmod 600` the file
- Delete it on task completion

NEVER:
- Commit a token
- Write a token to `.env` files that get committed
- Put a token in a task file, MEMORY, or PROGRESS
- Share a token in chat (paste the resulting curl with `Authorization: $TOKEN`)

## credentials.json schema

```json
{
  "api_base_url": "https://api.example.com",
  "api_key": "...",
  "test_user": {
    "email": "dev@example.com",
    "password": "..."
  }
}
```

The skill does not enforce a schema — project-specific. The only enforced rule
is location (`.agent/credentials.json`) and gitignore.

## When credentials don't exist

Ask the user once. Don't proceed with mocks unless the user says "use mocks".
Mocks that diverge from real APIs are a top source of "works locally, breaks
in prod" incidents. Document if mocks are used so the next agent knows.

## After every backend session

1. `rm .agent/.tmp/dev-token*`
2. Verify no credential or token landed in any committed file:
   `git diff --cached | grep -iE 'token|secret|password|api[_-]?key'`
3. If you ran any throwaway scripts, delete from `.agent/.tmp/`
