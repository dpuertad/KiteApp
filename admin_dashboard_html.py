def render_admin_dashboard(summary: dict) -> str:
    import json
    summary_json = json.dumps(summary)
    
    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>HolyGust · Spot Intelligence & Rider Demographics</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col selection:bg-sky-500 selection:text-white pb-12">
  <!-- Top Navigation -->
  <header class="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur sticky top-0 z-40 px-4 py-3 sm:px-6">
    <div class="max-w-6xl mx-auto flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <a href="/" class="flex items-center space-x-2.5 group">
          <div class="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-emerald-400 flex items-center justify-center text-slate-950 font-black shadow-md shadow-sky-500/20 group-hover:scale-105 transition">
            ⚡
          </div>
          <div>
            <div class="flex items-center space-x-2">
              <span class="font-extrabold text-sm sm:text-base text-white tracking-tight">HolyGust</span>
              <span class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase font-mono bg-sky-500/20 text-sky-300 border border-sky-500/30">Admin Intelligence</span>
            </div>
            <p class="text-[11px] text-slate-400">Rider Demographics & Spot Telemetry</p>
          </div>
        </a>
      </div>
      <div class="flex items-center space-x-2">
        <button onclick="fetchFreshData()" class="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center space-x-1.5 transition">
          <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-sky-400"></i>
          <span>Live Refresh</span>
        </button>
        <a href="/" class="px-3 py-1.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs shadow-sm shadow-sky-600/30 transition flex items-center space-x-1">
          <span>Open App</span>
          <i data-lucide="external-link" class="w-3 h-3"></i>
        </a>
      </div>
    </div>
  </header>

  <main class="max-w-6xl w-full mx-auto px-4 sm:px-6 pt-6 space-y-6 flex-1">
    <!-- Stat Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Total Spot Checks</span>
          <i data-lucide="eye" class="w-4 h-4 text-sky-400"></i>
        </div>
        <div id="stat-total-views" class="text-2xl font-black text-white font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Live forecast queries tracked</p>
      </div>

      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Active Watched Spots</span>
          <i data-lucide="map-pin" class="w-4 h-4 text-emerald-400"></i>
        </div>
        <div id="stat-total-spots" class="text-2xl font-black text-white font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Global beaches viewed</p>
      </div>

      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Active Riders</span>
          <i data-lucide="users" class="w-4 h-4 text-amber-400"></i>
        </div>
        <div id="stat-active-riders" class="text-2xl font-black text-white font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Registered cloud riders</p>
      </div>

      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Rider Nationalities</span>
          <i data-lucide="globe" class="w-4 h-4 text-cyan-400"></i>
        </div>
        <div id="stat-nationalities" class="text-2xl font-black text-white font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Countries represented</p>
      </div>
    </div>

    <!-- Main 2-Column Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column: Top Spots & Searches (Span 2) -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Top Spots Card -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-sm space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-bold text-white text-sm flex items-center space-x-2">
                <i data-lucide="flame" class="w-4 h-4 text-amber-400"></i>
                <span>Most Viewed Kite Spots (What People Are Looking At)</span>
              </h3>
              <p class="text-xs text-slate-400 mt-0.5">Real-time demand ranking across HolyGust riders</p>
            </div>
            <span class="text-[10px] font-mono text-slate-500">Live Telemetry</span>
          </div>

          <div id="top-spots-container" class="space-y-2">
            <!-- Dynamic Spot Rows -->
          </div>
        </div>

        <!-- Top Searches Card -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-sm space-y-3">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-white text-sm flex items-center space-x-2">
              <i data-lucide="search" class="w-4 h-4 text-sky-400"></i>
              <span>Most Searched Locations & Secret Spots</span>
            </h3>
            <span class="text-[10px] font-mono text-slate-500">Search Engine Log</span>
          </div>
          <div id="top-searches-container" class="flex flex-wrap gap-2">
            <!-- Dynamic search badges -->
          </div>
        </div>
      </div>

      <!-- Right Column: Nationality Demographics & Live Feed (Span 1) -->
      <div class="space-y-6">
        <!-- Rider Nationalities Card -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-sm space-y-3.5">
          <div>
            <h3 class="font-bold text-white text-sm flex items-center space-x-2">
              <i data-lucide="compass" class="w-4 h-4 text-cyan-400"></i>
              <span>Rider Nationalities</span>
            </h3>
            <p class="text-xs text-slate-400 mt-0.5">Self-reported passport & country of origin</p>
          </div>

          <div id="nationalities-container" class="space-y-2.5">
            <!-- Dynamic nationality bars -->
          </div>
        </div>

        <!-- Real-Time Activity Feed -->
        <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 shadow-sm space-y-3.5">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-white text-sm flex items-center space-x-2">
              <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Live Spot Activity Feed</span>
            </h3>
            <span class="text-[10px] font-mono text-emerald-400 font-semibold">STREAMING</span>
          </div>

          <div id="live-feed-container" class="space-y-2 max-h-[380px] overflow-y-auto pr-1">
            <!-- Dynamic activity events -->
          </div>
        </div>
      </div>
    </div>
  </main>

  <script>
    let initialData = {summary_json};

    function timeAgo(isoStr) {{
      if (!isoStr) return '';
      try {{
        const diff = Math.floor((Date.now() - new Date(isoStr).getTime()) / 1000);
        if (diff < 60) return `${{diff}}s ago`;
        if (diff < 3600) return `${{Math.floor(diff/60)}}m ago`;
        if (diff < 86400) return `${{Math.floor(diff/3600)}}h ago`;
        return `${{Math.floor(diff/86400)}}d ago`;
      }} catch(e) {{
        return '';
      }}
    }}

    function renderDashboard(d) {{
      document.getElementById('stat-total-views').innerText = d.total_spot_views || 0;
      document.getElementById('stat-total-spots').innerText = (d.top_spots || []).length;
      document.getElementById('stat-active-riders').innerText = d.unique_registered_riders_active || 0;
      document.getElementById('stat-nationalities').innerText = (d.top_nationalities || []).length;

      // Top Spots
      const spotsCont = document.getElementById('top-spots-container');
      if (spotsCont) {{
        if (!d.top_spots || d.top_spots.length === 0) {{
          spotsCont.innerHTML = '<div class="text-xs text-slate-500 py-4 text-center">No spot check telemetry recorded yet today.</div>';
        }} else {{
          spotsCont.innerHTML = d.top_spots.map((s, idx) => `
            <div class="p-3 bg-slate-950/70 border border-slate-800/80 rounded-2xl flex items-center justify-between gap-3">
              <div class="flex items-center space-x-3 min-w-0 flex-1">
                <span class="w-6 h-6 rounded-lg bg-slate-800 text-sky-400 font-bold text-xs flex items-center justify-center font-mono flex-shrink-0">
                  #${{idx + 1}}
                </span>
                <div class="truncate">
                  <h4 class="font-bold text-xs text-white truncate">${{s.spot_name}}</h4>
                  <p class="text-[10px] text-slate-400 mt-0.5">
                    ${{s.lat !== null && s.lat !== undefined ? `${{s.lat}}°, ${{s.lon}}° · ` : ''}}
                    <span class="text-slate-500">Last viewed ${{timeAgo(s.last_viewed)}}</span>
                  </p>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <span class="font-mono font-bold text-sm text-emerald-400">${{s.views}} views</span>
                <span class="block text-[10px] font-mono text-slate-400">${{s.share_pct}}% share</span>
              </div>
            </div>
          `).join('');
        }}
      }}

      // Nationalities
      const natsCont = document.getElementById('nationalities-container');
      if (natsCont) {{
        if (!d.top_nationalities || d.top_nationalities.length === 0) {{
          natsCont.innerHTML = '<div class="text-xs text-slate-500 py-3 text-center">No nationality data collected yet.</div>';
        }} else {{
          natsCont.innerHTML = d.top_nationalities.map(n => `
            <div class="space-y-1">
              <div class="flex justify-between text-xs font-semibold">
                <span class="text-slate-200">${{n.nationality}}</span>
                <span class="text-sky-400 font-mono">${{n.count}} riders (${{n.pct}}%)</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div class="bg-gradient-to-r from-sky-500 to-cyan-400 h-1.5 rounded-full" style="width: ${{Math.min(100, Math.max(8, n.pct))}}%"></div>
              </div>
            </div>
          `).join('');
        }}
      }}

      // Live Feed
      const feedCont = document.getElementById('live-feed-container');
      if (feedCont) {{
        const acts = d.recent_activity || [];
        if (acts.length === 0) {{
          feedCont.innerHTML = '<div class="text-xs text-slate-500 py-4 text-center">Telemetry feed is waiting for next spot check.</div>';
        }} else {{
          feedCont.innerHTML = acts.map(a => `
            <div class="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs flex items-center justify-between gap-2">
              <div class="min-w-0 flex-1 truncate">
                <div class="flex items-center space-x-1.5 truncate">
                  <span class="font-bold text-slate-200">${{a.rider_name || 'Rider'}}</span>
                  ${{a.nationality && a.nationality !== 'Not Specified' ? `<span class="px-1.5 py-0.2 rounded text-[9px] bg-slate-800 text-sky-300 font-medium">${{a.nationality}}</span>` : ''}}
                </div>
                <p class="text-[11px] text-slate-400 truncate mt-0.5">Checked <strong>${{a.spot_name}}</strong></p>
              </div>
              <span class="text-[10px] text-slate-500 font-mono flex-shrink-0">${{timeAgo(a.timestamp)}}</span>
            </div>
          `).join('');
        }}
      }}

      // Top Searches
      const searchCont = document.getElementById('top-searches-container');
      if (searchCont) {{
        const searches = d.top_searches || [];
        if (searches.length === 0) {{
          searchCont.innerHTML = '<span class="text-xs text-slate-500">No searches recorded yet.</span>';
        }} else {{
          searchCont.innerHTML = searches.map(s => `
            <span class="px-2.5 py-1 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 flex items-center space-x-1">
              <span>${{s.query}}</span>
              <span class="text-sky-400 font-mono text-[10px] font-bold">×${{s.count}}</span>
            </span>
          `).join('');
        }}
      }}

      if (window.lucide) lucide.createIcons();
    }}

    async function fetchFreshData() {{
      try {{
        const res = await fetch('/api/admin/spot-insights');
        if (res.ok) {{
          const d = await res.json();
          renderDashboard(d);
        }}
      }} catch(e) {{
        console.warn('Dashboard refresh failed:', e);
      }}
    }}

    document.addEventListener('DOMContentLoaded', () => {{
      renderDashboard(initialData);
      setInterval(fetchFreshData, 10000);
    }});
  </script>
</body>
</html>"""
