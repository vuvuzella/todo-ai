# Datastar Web Development Learnings

Patterns and techniques discovered while building the todo app with Datastar + FastAPI.

## Installation & Setup

Load Datastar as an ES module from CDN or self-host.

- Use `<script type="module" src="...">` — Datastar requires ES module loading
- CDN: `https://cdn.jsdelivr.net/gh/starfederation/datastar@v1.0.2/bundles/datastar.js`
- Self-hosting recommended for production; download bundle or use the [bundler](https://data-star.dev/pro/bundler)
- Single ~12KB file, no npm/build step required

**Resources:**
- [Getting Started](https://data-star.dev/guide)
- [GitHub](https://github.com/starfederation/datastar)

## Auto-Fetch on Element Mount

Use `data-init` to trigger HTTP requests when an element enters the DOM.

- `data-init="@get('/endpoint')"` fires a GET request immediately on mount
- Useful for loading fragments into placeholder elements
- Combine with `data-indicator` to show loading state (define indicator signal *before* the fetch)

```html
<div id="task-list" data-init="@get('/tasks/fragments/list')">
  Loading...
</div>
```

**Resources:**
- [data-init](https://data-star.dev/reference/attributes#data-init)
- [data-indicator](https://data-star.dev/reference/attributes#data-indicator)

## Reactive Signals

`data-signals` creates reactive state; access values with `$signalName` syntax.

- Define signals as JSON: `data-signals='{"foo": "bar", "count": 0}'`
- Signals are reactive — changes automatically update dependent expressions
- Signals starting with `_` are excluded from backend requests by default
- Nested signals via dot notation: `data-signals:user.name="'John'"`

```html
<div data-signals='{"access_token": "{{ access_token }}"}'>
  <!-- $access_token is now available in expressions -->
</div>
```

**Resources:**
- [data-signals](https://data-star.dev/reference/attributes#data-signals)
- [Reactive Signals Guide](https://data-star.dev/guide/reactive_signals)

## Event Handling with Actions

`data-on:event` attaches listeners; `@get()`, `@post()` etc. are action helpers.

- Syntax: `data-on:click="@get('/endpoint')"`
- Pass custom headers: `headers: {Authorization: 'Bearer ' + $access_token}`
- Control which signals are sent: `filterSignals: { exclude: '.*' }` or `{ include: /pattern/ }`
- Modifiers available: `__debounce`, `__throttle`, `__once`, `__prevent`

```html
<button data-on:click="@get('/api/tasks', {
  headers: {Authorization: 'Bearer ' + $access_token},
  filterSignals: { exclude: '.*' }
})">
  Fetch Tasks
</button>
```

**Resources:**
- [data-on](https://data-star.dev/reference/attributes#data-on)
- [Backend Actions](https://data-star.dev/reference/actions#backend-actions)

## Fragment Architecture Pattern

Structure routes as full pages + fragment endpoints returning HTML partials.

- Full page route (`/tasks`) returns complete HTML with Datastar script
- Fragment routes (`/tasks/fragments/list`) return only the partial HTML to swap
- Partials must have an `id` attribute matching the placeholder element
- Datastar morphs (updates) the DOM element with matching ID

```
Routes:
  GET /tasks              → Full page (tasks.html)
  GET /tasks/fragments/*  → HTML partials only

templates/
  tasks.html              → Full page with <div id="task-list">
  partials/
    task_list.html        → Partial with <div id="task-list">
```

**Resources:**
- [Patching Elements](https://data-star.dev/guide#patching-elements)
- [SSE Events](https://data-star.dev/reference/sse_events)

## ID Matching for DOM Morphing

Datastar uses element IDs to determine which elements to update.

- Response HTML must contain elements with IDs matching existing DOM elements
- Morphing only updates changed parts, preserving state and improving performance
- Use `data-ignore-morph` to skip specific elements during morph
- Use `data-preserve-attr` to keep certain attributes unchanged

```html
<!-- Backend returns this partial -->
<div id="task-list">
  {% for task in tasks %}
  <div id="task-{{ task.id }}" class="task-item">
    <h3>{{ task.name }}</h3>
  </div>
  {% endfor %}
</div>
```

**Resources:**
- [Morphing Strategy](https://data-star.dev/guide#patching-elements)
- [data-ignore-morph](https://data-star.dev/reference/attributes#data-ignore-morph)

## FastAPI + Jinja2 Integration

Use Jinja2Templates with separate template directories for pages vs fragments.

- Create `Jinja2Templates` instances pointing to template directories
- Return `TemplateResponse` with `text/html` content type
- Pass context data to templates for server-side rendering
- Fragment routes return the same template type, just smaller HTML

```python
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
fragment_templates = Jinja2Templates(directory="web/templates")


@router.get("/tasks/fragments/list")
async def get_tasks_list_fragment(request: Request):
    tasks = get_tasks()  # fetch from DB
    return fragment_templates.TemplateResponse(
        "partials/task_list.html", {"request": request, "tasks": tasks}
    )
```

**Resources:**
- [Python SDK](https://data-star.dev/reference/sdks#python)
- [FastAPI Templates](https://fastapi.tiangolo.com/advanced/templates/)

## Auth Token Handling via Signals

Store auth tokens in signals for client-side use in API requests.

- Server renders token into `data-signals` on initial page load
- Client-side actions access token via `$access_token` in headers
- Token travels with requests without needing cookies or session storage
- Use `filterSignals: { exclude: '.*' }` to prevent signals from being sent in request body

```html
<!-- Server renders token into page -->
<div data-signals='{"access_token": "{{ access_token }}"}'>

<!-- Client uses token in subsequent requests -->
<button data-on:click="@get('/api/protected', {
  headers: {Authorization: 'Bearer ' + $access_token}
})">
  Call Protected API
</button>
```

## Common Gotchas

- **`data-on-load` renamed to `data-init`**: As of v1.0.0-RC.6, `data-on-load` was renamed to `data-init`. Use `data-init` for running expressions on element mount. See [v1.0.0-RC.6 release notes](https://github.com/starfederation/datastar/releases/tag/v1.0.0-RC.6).
- **Attribute key delimiter changed**: Also in v1.0.0-RC.6, the delimiter changed from `-` to `:` (e.g., `data-on-click` → `data-on:click`). Use regex to migrate: search `data-(?!(on-(intersect|interval|load|raf|resize|signal-patch|signal-patch-filter)(_|=)))(attr|bind|class|computed|indicator|on|persist|ref|signals|style)-` replace with `data-$4:`.
- **Attribute order matters**: `data-indicator` must appear before `data-init` on the same element
- **Signals are camelCase**: `data-signals:my-signal` creates `$mySignal` (hyphen-to-camel conversion)
- **Events are kebab-case by default**: `data-on:my-event` listens for `my-event`. Note: `load` is not a DOM event you can listen to with `data-on:load` — use `data-init` instead.
- **Two template directories**: Keep full pages and partials separate for clarity
- **Response content-type**: Must be `text/html` for morphing or `text/event-stream` for SSE

**Migration Resources:**
- [v1.0.0-RC.6 Breaking Changes](https://github.com/starfederation/datastar/releases/tag/v1.0.0-RC.6)
- [data-init Reference](https://data-star.dev/reference/attributes#data-init)

## Additional Resources

- [Datastar Guide](https://data-star.dev/guide)
- [Attributes Reference](https://data-star.dev/reference/attributes)
- [Actions Reference](https://data-star.dev/reference/actions)
- [SSE Events Reference](https://data-star.dev/reference/sse_events)
- [Python SDK](https://data-star.dev/reference/sdks#python)
- [Examples](https://data-star.dev/examples)
- [Discord Community](https://discord.gg/bnRNgZjgPh)
