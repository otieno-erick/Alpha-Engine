<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://unpkg.com/htmx.org@1.9.12"></script>
    <script defer src="https://unpkg.com/alpinejs@3.13.0/dist/cdn.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Alpha Engine</title>
  </head>
  <body class="bg-slate-100 text-slate-900">
    <main class="mx-auto max-w-5xl py-12 px-4" x-data="{
      quota: {remaining: 100, reserve: 10},
      cache: {saved: 0},
      tasks: [],
      session: {minutes_left: 54},
      sim_today: 42,
      reset: {hours: 6, minutes: 12}
    }">
      <header class="mb-8 flex items-center justify-between gap-4">
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Phase 1</p>
          <h1 class="text-3xl font-bold">Alpha Engine</h1>
        </div>
        <div class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm shadow-sm">
          <span class="font-semibold">Quota reserve:</span>
          <span x-text="quota.reserve || 10">10</span>
        </div>
      </header>

      <section class="mb-8 grid gap-4 md:grid-cols-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">Session time left</p>
          <p class="mt-2 text-3xl font-bold" x-text="session.minutes_left + ' min'">54 min</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">Simulations left today</p>
          <p class="mt-2 text-3xl font-bold" x-text="sim_today">42</p>
        </div>
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <p class="text-sm text-slate-500">Quota reset in</p>
          <p class="mt-2 text-3xl font-bold" x-text="reset.hours + 'h ' + reset.minutes + 'm'">6h 12m</p>
        </div>
      </section>

      <section class="mb-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-4 flex items-center justify-between gap-2">
          <h2 class="text-lg font-semibold">LLM Providers</h2>
          <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Providers</span>
        </div>
        <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">Google AI Studio</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">Groq</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">Cerebras</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">OpenRouter</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">NVIDIA NIM</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">Mistral</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">GitHub Models</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">Hugging Face (free)</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">OpenAI</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
          <div class="rounded-lg border border-slate-200 bg-slate-50 p-3"><div class="font-semibold">Anthropic Claude</div><button class="mt-3 rounded-md bg-slate-900 px-3 py-1.5 text-sm text-white">Add key</button></div>
        </div>
      </section>

      <section class="mb-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="mb-2 flex items-center justify-between gap-2">
          <h2 class="text-lg font-semibold">Budget</h2>
          <span class="text-xs uppercase tracking-[0.2em] text-slate-500">Daily</span>
        </div>
        <ul class="text-sm text-slate-700">
          <li>OpenAI: 12 requests</li>
          <li>Groq: 8 requests</li>
          <li>Anthropic Claude: 3 requests</li>
        </ul>
      </section>

      <section class="grid gap-4 md:grid-cols-3">
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><p class="text-sm text-slate-500">Remaining quota</p><p class="mt-2 text-3xl font-bold" x-text="quota.remaining || 100">100</p></div>
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><p class="text-sm text-slate-500">Saved by hash cache</p><p class="mt-2 text-3xl font-bold" x-text="cache.saved || 0">0</p></div>
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"><p class="text-sm text-slate-500">Running tasks</p><p class="mt-2 text-3xl font-bold" x-text="tasks.length || 0">0</p></div>
      </section>

      <section class="mt-8 rounded-xl border border-slate-200 bg-white p-5 shadow-sm" x-data="{quota: {remaining: 100, reserve: 10}, cache: {saved: 0}, tasks: []}">
        <div class="flex items-center justify-between gap-4">
          <h2 class="text-lg font-semibold">Runtime status</h2>
          <button class="rounded-md bg-slate-900 px-4 py-2 text-white" hx-post="/api/tasks" hx-vals='{"name":"phase1-task","source":"LLM","slots":2}' hx-target="#task-output" hx-swap="innerHTML">Start task</button>
        </div>
        <pre id="task-output" class="mt-4 whitespace-pre-wrap text-sm text-slate-700">Waiting for task status...</pre>
      </section>
    </main>
  </body>
</html>
