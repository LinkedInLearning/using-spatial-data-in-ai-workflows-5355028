// ──────────────────────────────────────────────
// Map Setup
// ──────────────────────────────────────────────

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
  center: [-98.5, 39.8],
  zoom: 4
});

map.addControl(new maplibregl.NavigationControl(), 'top-left');

map.on('load', () => {
  map.addSource('airports', {
    type: 'geojson',
    data: airportsData
  });

  map.addLayer({
    id: 'airport-circles',
    type: 'circle',
    source: 'airports',
    paint: {
      'circle-radius': [
        'match', ['get', 'type'],
        'large_airport', 7,
        'medium_airport', 5,
        'small_airport', 3,
        4
      ],
      'circle-color': [
        'match', ['get', 'type'],
        'large_airport', '#e94560',
        'medium_airport', '#f5a623',
        'small_airport', '#53a8b6',
        '#888'
      ],
      'circle-stroke-width': 1,
      'circle-stroke-color': '#fff',
      'circle-opacity': 0.9
    }
  });

  // Popup on click
  map.on('click', 'airport-circles', (e) => {
    const f = e.features[0];
    const p = f.properties;
    new maplibregl.Popup({ offset: 10 })
      .setLngLat(f.geometry.coordinates)
      .setHTML(`
        <div class="popup-title">${p.name} (${p.iata})</div>
        <div class="popup-detail">${p.city}, ${p.state}</div>
        <div class="popup-detail">Type: ${p.type.replace('_', ' ')} &bull; Elevation: ${p.elevation_ft} ft</div>
      `)
      .addTo(map);
  });

  map.on('mouseenter', 'airport-circles', () => { map.getCanvas().style.cursor = 'pointer'; });
  map.on('mouseleave', 'airport-circles', () => { map.getCanvas().style.cursor = ''; });

  applyFilters();
  buildStateList();
});

// ──────────────────────────────────────────────
// Filter Engine
// ──────────────────────────────────────────────

const filterLarge = document.getElementById('filter-large');
const filterMedium = document.getElementById('filter-medium');
const filterSmall = document.getElementById('filter-small');
const filterState = document.getElementById('filter-state');
const filterElevMin = document.getElementById('filter-elev-min');
const filterElevMax = document.getElementById('filter-elev-max');
const elevMinLabel = document.getElementById('elev-min-label');
const elevMaxLabel = document.getElementById('elev-max-label');
const airportCount = document.getElementById('airport-count');
const stateSuggestions = document.getElementById('state-suggestions');

let allStates = [];

function buildStateList() {
  const set = new Set();
  airportsData.features.forEach(f => set.add(f.properties.state));
  allStates = [...set].sort();
}

function applyFilters() {
  if (!map.getSource('airports')) return;

  const types = [];
  if (filterLarge.checked) types.push('large_airport');
  if (filterMedium.checked) types.push('medium_airport');
  if (filterSmall.checked) types.push('small_airport');

  const state = filterState.value.trim().toUpperCase();
  const elevMin = parseInt(filterElevMin.value);
  const elevMax = parseInt(filterElevMax.value);

  elevMinLabel.textContent = elevMin.toLocaleString();
  elevMaxLabel.textContent = elevMax.toLocaleString();

  // Build MapLibre filter (expression syntax)
  const conditions = ['all'];

  if (types.length < 3) {
    conditions.push(['in', ['get', 'type'], ['literal', types]]);
  }

  if (state) {
    conditions.push(['==', ['get', 'state'], state]);
  }

  conditions.push(['>=', ['get', 'elevation_ft'], elevMin]);
  conditions.push(['<=', ['get', 'elevation_ft'], elevMax]);

  map.setFilter('airport-circles', conditions);

  // Count visible
  const count = airportsData.features.filter(f => {
    const p = f.properties;
    if (!types.includes(p.type)) return false;
    if (state && p.state.toUpperCase() !== state) return false;
    if (p.elevation_ft < elevMin || p.elevation_ft > elevMax) return false;
    return true;
  }).length;

  airportCount.textContent = `${count} airport${count !== 1 ? 's' : ''}`;
}

// Widget event listeners
[filterLarge, filterMedium, filterSmall].forEach(cb => cb.addEventListener('change', applyFilters));
filterElevMin.addEventListener('input', applyFilters);
filterElevMax.addEventListener('input', applyFilters);

filterState.addEventListener('input', () => {
  const val = filterState.value.trim().toUpperCase();
  if (val.length === 0) {
    stateSuggestions.classList.remove('active');
    applyFilters();
    return;
  }
  const matches = allStates.filter(s => s.startsWith(val)).slice(0, 8);
  if (matches.length > 0) {
    stateSuggestions.innerHTML = matches.map(s =>
      `<div class="suggestion-item" data-state="${s}">${s}</div>`
    ).join('');
    stateSuggestions.classList.add('active');
  } else {
    stateSuggestions.classList.remove('active');
  }
  applyFilters();
});

stateSuggestions.addEventListener('click', (e) => {
  const item = e.target.closest('.suggestion-item');
  if (item) {
    filterState.value = item.dataset.state;
    stateSuggestions.classList.remove('active');
    applyFilters();
  }
});

document.addEventListener('click', (e) => {
  if (!e.target.closest('#filter-state') && !e.target.closest('#state-suggestions')) {
    stateSuggestions.classList.remove('active');
  }
});

document.getElementById('reset-filters').addEventListener('click', () => {
  resetAllFilters();
});

function resetAllFilters() {
  filterLarge.checked = true;
  filterMedium.checked = true;
  filterSmall.checked = true;
  filterState.value = '';
  filterElevMin.value = 0;
  filterElevMax.value = 15000;
  applyFilters();
}

// ──────────────────────────────────────────────
// Groq AI Chat
// ──────────────────────────────────────────────

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const chatSend = document.getElementById('chat-send');
const groqKeyInput = document.getElementById('groq-key');
const saveKeyBtn = document.getElementById('save-key');

let groqApiKey = sessionStorage.getItem('groq_key') || '';
if (groqApiKey) {
  groqKeyInput.value = '••••••••';
  chatInput.disabled = false;
  chatSend.disabled = false;
}

saveKeyBtn.addEventListener('click', () => {
  const key = groqKeyInput.value.trim();
  if (key && !key.startsWith('••')) {
    groqApiKey = key;
    sessionStorage.setItem('groq_key', key);
    groqKeyInput.value = '••••••••';
    chatInput.disabled = false;
    chatSend.disabled = false;
  }
});

const conversationHistory = [];

const SYSTEM_PROMPT = `You are an AI assistant for a US Airport Explorer map application. You help users explore airports across the United States on an interactive map.

You have access to a dataset of ~150 US airports with these properties:
- name: Airport name
- city: City name
- state: 2-letter state code (e.g., "CA", "NY", "TX", "AK", "HI", "PR", "VI")
- iata: 3-letter IATA code (e.g., JFK, LAX, ORD)
- type: "large_airport", "medium_airport", or "small_airport"
- elevation_ft: Elevation in feet

The dataset covers 49 states and territories including Alaska, Hawaii, Puerto Rico, and the US Virgin Islands.

You can use the following tools to control the map and filters:

1. move_map: Pan the map to a location
2. filter_airports: Apply filters to show specific airports
3. reset_filters: Clear all filters and show all airports

When the user mentions a state name, convert it to the 2-letter code for filtering (e.g., "California" → "CA", "Alaska" → "AK").
When the user asks about a location, use move_map to fly there AND filter_airports to show relevant results.
When giving info about airports, be concise and helpful. Always use the tools to make changes visible on the map.
If the user asks something unrelated to airports or maps, politely redirect.`;

const TOOLS = [
  {
    type: 'function',
    function: {
      name: 'move_map',
      description: 'Pan and zoom the map to a specific location in the US. Use this when the user wants to see a particular area.',
      parameters: {
        type: 'object',
        properties: {
          latitude: { type: 'number', description: 'Latitude of the target location' },
          longitude: { type: 'number', description: 'Longitude of the target location' },
          zoom: { type: 'number', description: 'Zoom level (4=full US, 6=state, 8=city, 12=close)' }
        },
        required: ['latitude', 'longitude', 'zoom']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'filter_airports',
      description: 'Filter airports displayed on the map. Only include parameters you want to change.',
      parameters: {
        type: 'object',
        properties: {
          types: {
            type: 'array',
            items: { type: 'string', enum: ['large_airport', 'medium_airport', 'small_airport'] },
            description: 'Airport types to show. Omit to keep current setting.'
          },
          state: {
            type: 'string',
            description: '2-letter US state code to filter by (e.g., "CA", "TX", "NY"). Empty string to clear state filter.'
          },
          min_elevation: {
            type: 'number',
            description: 'Minimum elevation in feet'
          },
          max_elevation: {
            type: 'number',
            description: 'Maximum elevation in feet'
          }
        }
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'reset_filters',
      description: 'Reset all filters to show all airports. Use when the user wants to clear filters or start fresh.',
      parameters: {
        type: 'object',
        properties: {}
      }
    }
  }
];

function executeToolCall(name, args) {
  switch (name) {
    case 'move_map':
      console.log(args)
      map.flyTo({
        center: [args.longitude, args.latitude],
        zoom: args.zoom,
        duration: 2000
      });
      return `Map moved to [${args.latitude.toFixed(2)}, ${args.longitude.toFixed(2)}] at zoom ${args.zoom}`;

    case 'filter_airports':
      console.log(args)
      if (args.types) {
        filterLarge.checked = args.types.includes('large_airport');
        filterMedium.checked = args.types.includes('medium_airport');
        filterSmall.checked = args.types.includes('small_airport');
      }
      if (args.state !== undefined) {
        filterState.value = args.state;
      }
      if (args.min_elevation !== undefined) {
        filterElevMin.value = args.min_elevation;
      }
      if (args.max_elevation !== undefined) {
        filterElevMax.value = args.max_elevation;
      }
      applyFilters();
      return `Filters applied. ${airportCount.textContent} visible.`;

    case 'reset_filters':
      console.log(`All filters reset. ${airportCount.textContent} visible.`)
      resetAllFilters();
      map.flyTo({ center: [-98.5, 39.8], zoom: 4, duration: 2000 });
      return `All filters reset. ${airportCount.textContent} visible.`;

    default:
      return 'Unknown tool.';
  }
}

function addMessage(role, content) {
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.innerHTML = content;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return div;
}

function addThinking(toolCalls) {
  const div = document.createElement('div');
  div.className = 'message thinking';

  const details = toolCalls.map(tc => {
    const args = JSON.parse(tc.function.arguments);
    return `${tc.function.name}(${JSON.stringify(args, null, 2)})`;
  }).join('\n\n');

  div.innerHTML = `
    <div class="thinking-header" onclick="this.querySelector('.arrow').classList.toggle('open'); this.nextElementSibling.classList.toggle('open')">
      <span class="arrow">&#9654;</span> Thinking &mdash; ${toolCalls.length} action${toolCalls.length > 1 ? 's' : ''}
    </div>
    <div class="thinking-body">${details}</div>
  `;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(userText) {
  addMessage('user', userText);
  chatInput.value = '';
  chatInput.disabled = true;
  chatSend.disabled = true;

  conversationHistory.push({ role: 'user', content: userText });

  const loadingDiv = addMessage('assistant', '<span class="loading-dots">Thinking</span>');

  try {
    let messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...conversationHistory
    ];

    // Loop for tool calls (Groq may make multiple rounds)
    let maxRounds = 5;
    while (maxRounds-- > 0) {
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${groqApiKey}`
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages: messages,
          tools: TOOLS,
          tool_choice: 'auto',
          temperature: 0.3
        })
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.error?.message || `API error: ${response.status}`);
      }

      const data = await response.json();
      const choice = data.choices[0];
      const assistantMsg = choice.message;

      // Add assistant message to history
      messages.push(assistantMsg);
      conversationHistory.push(assistantMsg);

      if (assistantMsg.tool_calls && assistantMsg.tool_calls.length > 0) {
        // Show thinking
        addThinking(assistantMsg.tool_calls);

        // Execute each tool call
        for (const tc of assistantMsg.tool_calls) {
          const args = JSON.parse(tc.function.arguments);
          const result = executeToolCall(tc.function.name, args);
          const toolMsg = { role: 'tool', tool_call_id: tc.id, content: result };
          messages.push(toolMsg);
          conversationHistory.push(toolMsg);
        }

        // If there's also text content, don't loop — show it
        if (choice.finish_reason === 'stop' && assistantMsg.content) {
          break;
        }
        // Otherwise loop to get the final text response
        continue;
      }

      // No tool calls — we have the final text
      break;
    }

    // Show final assistant text
    const lastAssistant = [...messages].reverse().find(m => m.role === 'assistant' && m.content);
    loadingDiv.remove();
    if (lastAssistant?.content) {
      addMessage('assistant', lastAssistant.content);
    }

  } catch (err) {
    loadingDiv.remove();
    addMessage('error', `Error: ${err.message}`);
    console.error(err);
  } finally {
    chatInput.disabled = false;
    chatSend.disabled = false;
    chatInput.focus();
  }
}

chatSend.addEventListener('click', () => {
  const text = chatInput.value.trim();
  if (text) sendMessage(text);
});

chatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (text) sendMessage(text);
  }
});
