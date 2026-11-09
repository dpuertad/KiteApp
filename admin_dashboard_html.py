def render_admin_dashboard(summary: dict) -> str:
    import json
    summary_json = json.dumps(summary)
    
    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>HolyGust · Admin Intelligence & Registered Riders</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    html, body {{
      max-width: 100vw;
      overflow-x: hidden;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col selection:bg-sky-500 selection:text-white pb-12 overflow-x-hidden w-full max-w-full">
  <!-- Top Navigation -->
  <header class="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur sticky top-0 z-40 px-4 py-3 sm:px-6">
    <div class="max-w-7xl mx-auto flex items-center justify-between">
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
            <p class="text-[11px] text-slate-400">Registered Riders, Quivers, Demographics & Spot Telemetry</p>
          </div>
        </a>
      </div>
      <div class="flex items-center space-x-1.5 sm:space-x-2 flex-shrink-0">
        <button onclick="fetchFreshData()" class="px-2.5 py-1.5 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700/80 text-xs font-semibold flex items-center space-x-1 transition active:scale-95">
          <i data-lucide="refresh-cw" class="w-3.5 h-3.5 text-sky-400"></i>
          <span class="hidden sm:inline">Refresh</span>
        </button>
        <button type="button" onclick="if (window.opener) {{ window.close(); }} else {{ window.location.href = '/'; }}" title="Close Admin View" class="w-8 h-8 rounded-xl bg-slate-800/90 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/80 flex items-center justify-center transition active:scale-95">
          <i data-lucide="x" class="w-4 h-4"></i>
        </button>
      </div>
    </div>
  </header>

  <main class="max-w-7xl w-full mx-auto px-3 sm:px-6 pt-4 sm:pt-6 space-y-5 sm:space-y-6 flex-1 overflow-x-hidden">
    <!-- Stat Cards (5 Core KPIs) -->
    <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4">
      <!-- 1. Registered Riders -->
      <div class="bg-slate-900/90 border border-sky-500/30 rounded-2xl p-4 shadow-sm relative overflow-hidden">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span class="text-sky-300 font-bold">Registered Riders</span>
          <i data-lucide="users" class="w-4 h-4 text-sky-400"></i>
        </div>
        <div id="stat-registered-riders" class="text-2xl font-black text-sky-400 font-mono">-</div>
        <p class="text-[10px] text-slate-400 mt-1">
          <span id="stat-beta-riders-count" class="font-bold text-amber-400 font-mono">0</span> ⚡ Beta Riders
        </p>
        <div class="absolute -right-2 -bottom-2 w-12 h-12 bg-sky-500/5 rounded-full pointer-events-none"></div>
      </div>

      <!-- 2. Spot Checks -->
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Spot Checks</span>
          <i data-lucide="eye" class="w-4 h-4 text-slate-400"></i>
        </div>
        <div id="stat-total-views" class="text-2xl font-black text-white font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Live forecast queries tracked</p>
      </div>

      <!-- 3. Watched Spots -->
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Active Spots</span>
          <i data-lucide="map-pin" class="w-4 h-4 text-emerald-400"></i>
        </div>
        <div id="stat-total-spots" class="text-2xl font-black text-white font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Global beaches viewed</p>
      </div>

      <!-- 4. Travel Inquiries -->
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Travel Inquiries</span>
          <i data-lucide="plane" class="w-4 h-4 text-amber-400"></i>
        </div>
        <div id="stat-total-travel" class="text-2xl font-black text-amber-400 font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Trip plans & quiver matches</p>
      </div>

      <!-- 5. Nationalities -->
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-sm">
        <div class="flex items-center justify-between text-slate-400 text-xs font-semibold mb-1">
          <span>Nationalities</span>
          <i data-lucide="globe" class="w-4 h-4 text-cyan-400"></i>
        </div>
        <div id="stat-nationalities" class="text-2xl font-black text-white font-mono">-</div>
        <p class="text-[10px] text-slate-500 mt-1">Countries represented</p>
      </div>
    </div>

    <!-- 👥 REGISTERED RIDERS DIRECTORY SECTION -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm space-y-4">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div class="flex items-center space-x-2">
            <i data-lucide="users" class="w-5 h-5 text-sky-400"></i>
            <h3 class="font-extrabold text-base text-white tracking-tight">HolyGust Registered Riders Directory</h3>
            <span id="stat-riders-badge" class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase font-mono bg-sky-500/20 text-sky-300 border border-sky-500/30">
              0 Accounts
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-1">Full breakdown of registered riders, quiver setups, weight, riding level & activity status.</p>
        </div>
        <div class="flex items-center space-x-2">
          <div class="relative w-full sm:w-64">
            <i data-lucide="search" class="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5"></i>
            <input 
              type="text" 
              id="rider-search-input" 
              oninput="filterRiders(this.value)" 
              placeholder="Search name, email, nationality..." 
              class="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 transition"
            >
          </div>
        </div>
      </div>

      <!-- Riders Cards Grid -->
      <div id="registered-riders-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
        <!-- Dynamic riders inserted via JavaScript -->
      </div>
    </div>

    <!-- ✈️ KITE TRAVEL DEMAND & GEAR GAP MONETIZATION SIGNALS -->
    <div class="bg-gradient-to-br from-slate-900/95 to-slate-900/60 border border-amber-500/30 rounded-3xl p-5 sm:p-6 shadow-xl space-y-5">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div class="flex items-center space-x-2">
            <span class="text-xl">✈️</span>
            <h3 class="font-extrabold text-base text-white tracking-tight">Kite Travel Demand & Gear Gap Signals</h3>
            <span class="px-2 py-0.5 rounded-full text-[10px] font-black uppercase font-mono bg-amber-500/20 text-amber-300 border border-amber-500/30">Commercial Leads</span>
          </div>
          <p class="text-xs text-slate-400 mt-1">High-intent purchase signals: destinations searched, travel months, and missing kite sizes for affiliate & hotel partnerships.</p>
        </div>
        <div id="stat-travel-count" class="px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700 text-xs font-mono font-bold text-amber-400 self-start sm:self-auto">
          0 Inquiries
        </div>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
        <!-- Top Travel Destinations -->
        <div class="space-y-3">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
            <i data-lucide="map-pin" class="w-3.5 h-3.5 text-amber-400"></i>
            <span>Top Trip Destinations Demanded</span>
          </h4>
          <div id="travel-destinations-container" class="space-y-2">
            <!-- Dynamic destinations -->
          </div>
        </div>

        <!-- Top Gear Gaps (Purchase Signals) -->
        <div class="space-y-3">
          <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
            <i data-lucide="shopping-bag" class="w-3.5 h-3.5 text-emerald-400"></i>
            <span>Most Advised Missing Kite Sizes (Affiliate Intent)</span>
          </h4>
          <div id="travel-gaps-container" class="space-y-2">
            <!-- Dynamic gear gaps -->
          </div>
        </div>
      </div>

      <!-- Recent Travel Leads Table -->
      <div class="pt-4 border-t border-slate-800/80 space-y-3">
        <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center space-x-1.5">
          <i data-lucide="plane-takeoff" class="w-3.5 h-3.5 text-sky-400"></i>
          <span>Recent Traveler Inquiries & Gear Intent</span>
        </h4>
        <div id="travel-leads-container" class="space-y-2 max-h-[300px] overflow-y-auto pr-1">
          <!-- Dynamic lead items -->
        </div>
      </div>
    </div>

    <!-- Main Grid: Top Spots vs Demographics -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left Column: Top Spots Leaderboard (Span 2) -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-slate-900/90 border border-slate-800 rounded-3xl p-5 sm:p-6 shadow-sm space-y-4">
          <div class="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 class="font-bold text-white text-base flex items-center space-x-2">
                <i data-lucide="trophy" class="w-4 h-4 text-amber-400"></i>
                <span>Top Queried Kite Spots</span>
              </h3>
              <p class="text-xs text-slate-400 mt-0.5">Ranked by rider search and live forecast activity</p>
            </div>
            <span class="text-xs font-mono text-slate-500">Live Telemetry</span>
          </div>

          <div id="top-spots-container" class="space-y-2.5">
            <!-- Dynamic spot items -->
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
    let allRiders = (initialData.registered_riders || []);

    function timeAgo(isoStr) {{
      if (!isoStr) return '';
      try {{
        const cleanIso = String(isoStr).replace('+00:00Z', 'Z').replace('+00:00', 'Z');
        const ts = new Date(cleanIso).getTime();
        if (isNaN(ts)) return '';
        const diff = Math.floor((Date.now() - ts) / 1000);
        if (diff < 60) return `${{Math.max(1, diff)}}s ago`;
        if (diff < 3600) return `${{Math.floor(diff/60)}}m ago`;
        if (diff < 86400) return `${{Math.floor(diff/3600)}}h ago`;
        return `${{Math.floor(diff/86400)}}d ago`;
      }} catch(e) {{
        return '';
      }}
    }}

    function toggleRiderQuiver(riderIdx, kind) {{
      const el = document.getElementById(`rider-${{kind}}-panel-${{riderIdx}}`);
      const chev = document.getElementById(`rider-${{kind}}-chev-${{riderIdx}}`);
      if (!el) return;
      const isHidden = el.classList.contains('hidden');
      if (isHidden) {{
        el.classList.remove('hidden');
        if (chev) chev.style.transform = 'rotate(180deg)';
      }} else {{
        el.classList.add('hidden');
        if (chev) chev.style.transform = 'rotate(0deg)';
      }}
    }}

    function getFlag(nat) {{
      const n = (nat || '').toLowerCase();
      if (n.includes('span')) return '🇪🇸';
      if (n.includes('swis')) return '🇨🇭';
      if (n.includes('germ')) return '🇩🇪';
      if (n.includes('braz')) return '🇧🇷';
      if (n.includes('ital')) return '🇮🇹';
      if (n.includes('fren')) return '🇫🇷';
      if (n.includes('brit') || n.includes('uk') || n.includes('eng')) return '🇬🇧';
      if (n.includes('dutc') || n.includes('neth')) return '🇳🇱';
      if (n.includes('austr')) return '🇦🇹';
      if (n.includes('usa') || n.includes('amer')) return '🇺🇸';
      if (n.includes('port')) return '🇵🇹';
      if (n.includes('pola')) return '🇵🇱';
      if (n.includes('denm') || n.includes('dani')) return '🇩🇰';
      if (n.includes('swed')) return '🇸🇪';
      if (n.includes('norw')) return '🇳🇴';
      if (n.includes('argen')) return '🇦🇷';
      return '🌍';
    }}

    function renderRidersList(riders) {{
      const cont = document.getElementById('registered-riders-container');
      if (!cont) return;

      if (!riders || riders.length === 0) {{
        cont.innerHTML = '<div class="col-span-full py-8 text-center text-xs text-slate-500 bg-slate-950/40 rounded-2xl border border-slate-800">No riders match search query.</div>';
        return;
      }}

      cont.innerHTML = riders.map((r, rIdx) => {{
        const isBeta = r.is_beta_rider;
        const flag = getFlag(r.nationality);
        const initial = (r.name || r.email || 'R')[0].toUpperCase();
        
        return `
          <div class="p-4 rounded-2xl bg-slate-950/70 border ${{isBeta ? 'border-amber-500/30 shadow-sm shadow-amber-500/5' : 'border-slate-800/80'}} flex flex-col justify-between space-y-3 hover:border-sky-500/40 transition">
            <!-- Top Row: Avatar & Rider Name -->
            <div class="flex items-start justify-between gap-2">
              <div class="flex items-center space-x-3 min-w-0">
                <div class="w-10 h-10 rounded-xl ${{isBeta ? 'bg-gradient-to-tr from-amber-500 to-amber-300 text-slate-950' : 'bg-gradient-to-tr from-sky-500 to-cyan-400 text-slate-950'}} font-black text-sm flex items-center justify-center flex-shrink-0 shadow-sm">
                  ${{isBeta ? '⚡' : initial}}
                </div>
                <div class="min-w-0 truncate">
                  <div class="flex items-center space-x-1.5 truncate">
                    <h4 class="font-bold text-sm text-white truncate">${{r.name || 'Rider'}}</h4>
                    ${{r.nationality && r.nationality !== 'Not specified' ? `<span class="text-xs" title="${{r.nationality}}">${{flag}}</span>` : ''}}
                  </div>
                  <p class="text-[11px] text-slate-400 font-mono truncate" title="${{r.email}}">${{r.email}}</p>
                </div>
              </div>

              ${{isBeta ? 
                `<span class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/40 flex-shrink-0">⚡ Beta</span>` : 
                (r.beta_status === 'pending' ? 
                  `<span class="px-2 py-0.5 rounded-full text-[9px] font-black uppercase tracking-wider bg-amber-500/20 text-amber-400 border border-amber-500/40 flex-shrink-0 animate-pulse">⏳ Pending Beta</span>` :
                  `<span class="px-2 py-0.5 rounded-full text-[9px] font-semibold bg-slate-800 text-slate-400 border border-slate-700/60 flex-shrink-0">Rider</span>`)}}
            </div>

            <!-- Setup & Demographics Pills -->
            <div class="flex flex-wrap items-center gap-1.5 text-[11px]">
              <span class="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-medium">
                ⚖️ <strong>${{r.weight_kg}} kg</strong>
              </span>
              <span class="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-medium">
                🎯 ${{r.level}}
              </span>
              <span class="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 font-medium">
                🏄 ${{r.board || 'Twintip'}}
              </span>
              ${{r.nationality && r.nationality !== 'Not specified' ? `
                <span class="px-2 py-0.5 rounded-lg bg-slate-900 border border-slate-800 text-sky-300 font-medium">
                  ${{flag}} ${{r.nationality}}
                </span>` : ''}}
            </div>

            <!-- Stored Cloud Gear & Boards (Expandable Dropdowns) -->
            <div class="bg-slate-900/60 rounded-xl p-2 border border-slate-800/80 space-y-1.5 text-[11px]">
              <!-- Kites Accordion -->
              <div>
                <button type="button" onclick="${{r.gear_count > 0 ? `toggleRiderQuiver(${{rIdx}}, 'kites')` : ''}}" class="w-full flex items-center justify-between text-left py-1 px-1.5 rounded-lg ${{r.gear_count > 0 ? 'hover:bg-slate-800/70 active:scale-[0.99] cursor-pointer' : 'cursor-default'}} transition">
                  <span class="flex items-center space-x-1.5 font-bold text-slate-200 flex-shrink-0">
                    <span>🪁</span>
                    <span>${{r.gear_count}} ${{r.gear_count === 1 ? 'Kite' : 'Kites'}}</span>
                  </span>
                  ${{r.gear_count > 0 ? `
                    <span class="flex items-center space-x-1.5 min-w-0 ml-2">
                      <span class="text-[10px] text-sky-400 font-semibold truncate max-w-[145px]">${{r.gear_summary}}</span>
                      <span id="rider-kites-chev-${{rIdx}}" class="text-[10px] text-sky-400 font-bold transition-transform duration-200 flex-shrink-0 px-1.5 py-0.5 rounded bg-sky-500/15 border border-sky-500/30">▼</span>
                    </span>
                  ` : `
                    <span class="text-[10px] text-slate-500">No kites yet</span>
                  `}}
                </button>
                ${{r.gear_count > 0 ? `
                  <div id="rider-kites-panel-${{rIdx}}" class="hidden mt-1.5 pt-1.5 border-t border-slate-800/80 space-y-1 px-1">
                    ${{(r.gear_list || []).map(g => `
                      <div class="flex items-center justify-between py-1 px-2 rounded-lg bg-slate-950/90 border border-slate-800/90 text-[11px]">
                        <div class="flex items-center space-x-2 min-w-0">
                          <span class="px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30 font-mono font-black text-[10px] flex-shrink-0">${{g.size}}m</span>
                          <span class="font-bold text-white truncate">${{g.brand}} ${{g.model}}</span>
                        </div>
                        <div class="flex items-center space-x-1.5 flex-shrink-0 ml-2">
                          ${{g.year ? `<span class="text-[10px] text-slate-400 font-mono">${{g.year}}</span>` : ''}}
                          <span class="text-[10px]" title="${{g.active !== false ? 'Packed in bag' : 'At home'}}">${{g.active !== false ? '🎒' : '🏠'}}</span>
                        </div>
                      </div>
                    `).join('')}}
                  </div>
                ` : ''}}
              </div>

              <!-- Boards Accordion -->
              <div class="border-t border-slate-800/60 pt-1">
                <button type="button" onclick="${{r.boards_count > 0 ? `toggleRiderQuiver(${{rIdx}}, 'boards')` : ''}}" class="w-full flex items-center justify-between text-left py-1 px-1.5 rounded-lg ${{r.boards_count > 0 ? 'hover:bg-slate-800/70 active:scale-[0.99] cursor-pointer' : 'cursor-default'}} transition">
                  <span class="flex items-center space-x-1.5 font-bold text-slate-200 flex-shrink-0">
                    <span>🏄</span>
                    <span>${{r.boards_count}} ${{r.boards_count === 1 ? 'Board' : 'Boards'}}</span>
                  </span>
                  ${{r.boards_count > 0 ? `
                    <span class="flex items-center space-x-1.5 min-w-0 ml-2">
                      <span class="text-[10px] text-violet-300 font-semibold truncate max-w-[145px]">${{r.boards_summary}}</span>
                      <span id="rider-boards-chev-${{rIdx}}" class="text-[10px] text-violet-300 font-bold transition-transform duration-200 flex-shrink-0 px-1.5 py-0.5 rounded bg-violet-500/15 border border-violet-500/30">▼</span>
                    </span>
                  ` : `
                    <span class="text-[10px] text-slate-500">No boards yet</span>
                  `}}
                </button>
                ${{r.boards_count > 0 ? `
                  <div id="rider-boards-panel-${{rIdx}}" class="hidden mt-1.5 pt-1.5 border-t border-slate-800/80 space-y-1 px-1">
                    ${{(r.boards_list || []).map(b => `
                      <div class="flex items-center justify-between py-1 px-2 rounded-lg bg-slate-950/90 border border-slate-800/90 text-[11px]">
                        <div class="flex items-center space-x-2 min-w-0">
                          <span class="px-1.5 py-0.5 rounded bg-violet-500/20 text-violet-300 border border-violet-500/30 font-mono font-black text-[10px] flex-shrink-0">${{b.size}}${{String(b.size).includes("'") ? '' : 'cm'}}</span>
                          <span class="font-bold text-white truncate">${{b.brand}} ${{b.model}}</span>
                        </div>
                        <div class="flex items-center space-x-1.5 flex-shrink-0 ml-2">
                          <span class="text-[10px] text-slate-400">${{b.type}}</span>
                          ${{b.carbon ? `<span class="text-[10px] text-amber-300 font-bold" title="Carbon / SLS">⚡</span>` : ''}}
                          <span class="text-[10px]" title="${{b.active !== false ? 'Packed in bag' : 'At home'}}">${{b.active !== false ? '🎒' : '🏠'}}</span>
                        </div>
                      </div>
                    `).join('')}}
                  </div>
                ` : ''}}
              </div>
            </div>

            ${{r.beta_status === 'pending' ? `
              <div class="flex items-center space-x-2 pt-1 border-t border-amber-500/20">
                <button type="button" onclick="approveBetaRider('${{r.email}}', this)" class="flex-1 py-1.5 px-3 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-950 font-black text-xs shadow-md shadow-amber-500/20 transition flex items-center justify-center space-x-1 active:scale-95">
                  <span>⚡ Approve Beta</span>
                </button>
                <button type="button" onclick="declineBetaRider('${{r.email}}', this)" class="py-1.5 px-3 rounded-xl bg-slate-900 hover:bg-rose-500/20 text-slate-400 hover:text-rose-300 font-semibold text-xs border border-slate-800 hover:border-rose-500/30 transition flex items-center justify-center space-x-1 active:scale-95">
                  <span>✕ Decline</span>
                </button>
              </div>
            ` : ''}}

            <!-- Footer: Last Spot & Timestamps -->
            <div class="flex items-center justify-between text-[10px] text-slate-400 font-mono border-t border-slate-800/80 pt-2">
              <span class="truncate max-w-[160px] text-slate-400" title="Last checked ${{r.last_spot}}">
                📍 ${{r.last_spot || 'None'}}
              </span>
              <span class="text-slate-400 flex-shrink-0">
                ${{r.last_active ? timeAgo(r.last_active) : timeAgo(r.registered_at)}}
              </span>
            </div>
          </div>
        `;
      }}).join('');
    }}

    function filterRiders(query) {{
      const q = (query || '').toLowerCase().trim();
      if (!q) {{
        renderRidersList(allRiders);
        return;
      }}
      const filtered = allRiders.filter(r => {{
        return (
          (r.name && r.name.toLowerCase().includes(q)) ||
          (r.email && r.email.toLowerCase().includes(q)) ||
          (r.nationality && r.nationality.toLowerCase().includes(q)) ||
          (r.level && r.level.toLowerCase().includes(q)) ||
          (r.gear_summary && r.gear_summary.toLowerCase().includes(q)) ||
          (r.last_spot && r.last_spot.toLowerCase().includes(q))
        );
      }});
      renderRidersList(filtered);
    }}

    function renderDashboard(d) {{
      const summary = d.summary || {{}};
      allRiders = (d.registered_riders || []);

      // 1. Core KPIs
      const regRidersEl = document.getElementById('stat-registered-riders');
      if (regRidersEl) regRidersEl.innerText = summary.total_registered_riders || allRiders.length || 0;

      const betaCountEl = document.getElementById('stat-beta-riders-count');
      if (betaCountEl) betaCountEl.innerText = summary.total_beta_riders || allRiders.filter(r => r.is_beta_rider).length || 0;

      const badgeEl = document.getElementById('stat-riders-badge');
      if (badgeEl) badgeEl.innerText = `${{summary.total_registered_riders || allRiders.length}} Verified Accounts`;

      document.getElementById('stat-total-views').innerText = summary.total_views || 0;
      document.getElementById('stat-total-spots').innerText = (d.top_spots || []).length;
      document.getElementById('stat-total-travel').innerText = summary.total_travel_inquiries || 0;
      document.getElementById('stat-nationalities').innerText = (d.top_nationalities || []).length;

      // 2. Render Riders Directory
      renderRidersList(allRiders);

      // 3. Top Spots Leaderboard
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

      // 4. Nationalities
      const natsCont = document.getElementById('nationalities-container');
      if (natsCont) {{
        if (!d.top_nationalities || d.top_nationalities.length === 0) {{
          natsCont.innerHTML = '<div class="text-xs text-slate-500 py-3 text-center">No nationality data collected yet.</div>';
        }} else {{
          natsCont.innerHTML = d.top_nationalities.map(n => `
            <div class="space-y-1">
              <div class="flex justify-between text-xs font-semibold">
                <span class="text-slate-200">${{getFlag(n.nationality)}} ${{n.nationality}}</span>
                <span class="text-sky-400 font-mono">${{n.count}} spot checks (${{n.pct}}%)</span>
              </div>
              <div class="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                <div class="bg-gradient-to-r from-sky-500 to-cyan-400 h-1.5 rounded-full" style="width: ${{Math.min(100, Math.max(8, n.pct))}}%"></div>
              </div>
            </div>
          `).join('');
        }}
      }}

      // 5. Travel Intelligence
      const travelIntel = d.travel_intelligence || {{}};
      const travelCountEl = document.getElementById('stat-travel-count');
      if (travelCountEl) {{
        travelCountEl.innerText = `${{summary.total_travel_inquiries || 0}} Inquiries`;
      }}

      // Travel Destinations
      const travelDestCont = document.getElementById('travel-destinations-container');
      if (travelDestCont) {{
        const dests = travelIntel.top_destinations || [];
        if (dests.length === 0) {{
          travelDestCont.innerHTML = '<div class="text-xs text-slate-500 py-3 text-center bg-slate-950/40 rounded-xl border border-slate-800">No travel trip inquiries logged yet.</div>';
        }} else {{
          travelDestCont.innerHTML = dests.map(item => `
            <div class="p-2.5 bg-slate-950/80 border border-slate-800 rounded-xl flex items-center justify-between text-xs">
              <span class="font-bold text-white truncate">${{item.destination}}</span>
              <span class="font-mono text-amber-400 font-bold">${{item.count}} searches</span>
            </div>
          `).join('');
        }}
      }}

      // Gear Gaps
      const gapsCont = document.getElementById('travel-gaps-container');
      if (gapsCont) {{
        const gaps = travelIntel.top_gear_gaps || [];
        if (gaps.length === 0) {{
          gapsCont.innerHTML = '<div class="text-xs text-slate-500 py-3 text-center bg-slate-950/40 rounded-xl border border-slate-800">No missing gear gap signals detected yet.</div>';
        }} else {{
          gapsCont.innerHTML = gaps.map(item => `
            <div class="p-2.5 bg-slate-950/80 border border-emerald-500/20 rounded-xl flex items-center justify-between text-xs">
              <div class="flex items-center space-x-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                <span class="font-bold text-emerald-300">${{item.size}}</span>
              </div>
              <span class="font-mono text-slate-300 font-bold">${{item.count}} riders advised</span>
            </div>
          `).join('');
        }}
      }}

      // Recent Travel Leads
      const leadsCont = document.getElementById('travel-leads-container');
      if (leadsCont) {{
        const leads = travelIntel.recent_travel_inquiries || [];
        if (leads.length === 0) {{
          leadsCont.innerHTML = '<div class="text-xs text-slate-500 py-3 text-center bg-slate-950/40 rounded-xl border border-slate-800">Waiting for first traveler lead.</div>';
        }} else {{
          leadsCont.innerHTML = leads.map(l => `
            <div class="p-2.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div class="min-w-0 flex-1">
                <div class="flex items-center space-x-2">
                  <span class="font-bold text-white">${{l.rider_name || 'Rider'}}</span>
                  ${{l.nationality && l.nationality !== 'Not Specified' ? `<span class="px-1.5 py-0.2 rounded text-[9px] bg-slate-800 text-sky-300 font-medium">${{l.nationality}}</span>` : ''}}
                  <span class="text-[10px] text-amber-400 font-semibold">→ ${{l.spot_name}} (${{l.month_name}})</span>
                </div>
                <p class="text-[10px] text-slate-400 mt-0.5 truncate">
                  Discipline: ${{l.discipline}} (${{l.weight_kg}}kg) · Quiver: ${{l.quiver_sizes.length ? l.quiver_sizes.map(s => s + 'm').join(', ') : 'None registered'}}
                </p>
              </div>
              <div class="text-left sm:text-right flex-shrink-0">
                ${{l.gear_gaps && l.gear_gaps.length ? `<span class="px-2 py-0.5 rounded-full text-[9px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-bold">Needs: ${{l.gear_gaps.map(g => g.size + 'm').join(', ')}}</span>` : '<span class="text-[9px] text-slate-500">Quiver complete</span>'}}
                <span class="block text-[9px] text-slate-500 font-mono mt-0.5">${{timeAgo(l.timestamp)}}</span>
              </div>
            </div>
          `).join('');
        }}
      }}

      // 6. Live Telemetry Feed
      const feedCont = document.getElementById('live-feed-container');
      if (feedCont) {{
        const acts = d.recent_views || [];
        if (acts.length === 0) {{
          feedCont.innerHTML = '<div class="text-xs text-slate-500 py-4 text-center">Telemetry feed is waiting for next spot check.</div>';
        }} else {{
          feedCont.innerHTML = acts.map(a => `
            <div class="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs flex items-center justify-between gap-2">
              <div class="min-w-0 flex-1 truncate">
                <div class="flex items-center space-x-1.5 truncate">
                  <span class="font-bold text-slate-200">${{a.rider_name || 'Rider'}}</span>
                  ${{a.nationality && a.nationality !== 'Not Specified' && a.nationality !== 'Undefined' ? `<span class="px-1.5 py-0.2 rounded text-[9px] bg-slate-800 text-sky-300 font-medium">${{getFlag(a.nationality)}} ${{a.nationality}}</span>` : ''}}
                </div>
                <p class="text-[11px] text-slate-400 truncate mt-0.5">Checked <strong>${{a.spot_name}}</strong></p>
              </div>
              <span class="text-[10px] text-slate-500 font-mono flex-shrink-0">${{timeAgo(a.timestamp)}}</span>
            </div>
          `).join('');
        }}
      }}

      if (window.lucide) lucide.createIcons();
    }}



        async function approveBetaRider(email, btnEl) {{
      if (!email) return;
      if (btnEl) {{
        btnEl.disabled = true;
        btnEl.innerText = 'Approving...';
      }}
      try {{
        const res = await fetch('/api/admin/approve-beta', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ email: email }})
        }});
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || 'Approval failed');
        if (btnEl) {{
          btnEl.className = 'flex-1 py-1.5 px-3 rounded-xl bg-emerald-500 text-white font-black text-xs';
          btnEl.innerText = '✅ Approved!';
        }}
        setTimeout(() => {{ fetchFreshData(); }}, 1200);
      }} catch (err) {{
        alert('Could not approve rider: ' + err.message);
        if (btnEl) {{
          btnEl.disabled = false;
          btnEl.innerText = '⚡ Retry Approve';
        }}
      }}
    }}

    async function declineBetaRider(email, btnEl) {{
      if (!confirm(`Are you sure you want to decline ${{email}}?`)) return;
      if (btnEl) {{
        btnEl.disabled = true;
        btnEl.innerText = 'Declining...';
      }}
      try {{
        const res = await fetch('/api/admin/decline-beta', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ email: email }})
        }});
        const data = await res.json();
        if (!res.ok || !data.success) throw new Error(data.error || 'Decline failed');
        fetchFreshData();
      }} catch (err) {{
        alert('Could not decline rider: ' + err.message);
        if (btnEl) {{
          btnEl.disabled = false;
          btnEl.innerText = '✕ Decline';
        }}
      }}
    }}

    async function fetchFreshData() {{
      try {{
        const res = await fetch('/api/admin/spot-insights');
        if (res.ok) {{
          const data = await res.json();
          renderDashboard(data);
        }}
      }} catch(e) {{
        console.error("Refresh error:", e);
      }}
    }}

    // Initial render
    renderDashboard(initialData);
  </script>
</body>
</html>
"""
