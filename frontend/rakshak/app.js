// Project Rakshak JavaScript Logic

document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // 1. API CONFIGURATION
    // -------------------------------------------------------------------------
    const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';
    const WS_BASE_URL = 'ws://127.0.0.1:8000/ws/transactions';
    
    const api = axios.create({
        baseURL: API_BASE_URL,
        headers: {
            'Content-Type': 'application/json'
        }
    });

    // Request Interceptor
    api.interceptors.request.use(config => {
        // You can attach tokens here if backend requires them later
        return config;
    }, error => Promise.reject(error));

    // Response Interceptor
    api.interceptors.response.use(response => response, error => {
        console.error('API Error:', error);
        showToast(error.response?.data?.detail || 'An API error occurred', 'error');
        return Promise.reject(error);
    });

    // -------------------------------------------------------------------------
    // 1.5. STATE MANAGEMENT
    // -------------------------------------------------------------------------
    const state = {
        isAuthenticated: false,
        activeView: 'dashboard',
        settings: {
            sensitivity: 84,
            deviationLimit: 2.4,
            requireMfa: true,
            simEnabled: false,
            simRunning: false
        },
        dashboard: {
            alertsToday: 1284,
            suspiciousAccounts: 42,
            blockedFunds: 4.2,
            anomalies: 12,
            frozen: 8,
            activeInvestigations: 15
        },
        feeds: {
            globalSystemRisk: 62.3,
            blacklisted: [
                { id: 'ACC-992120001', type: 'NCRP Block' },
                { id: 'PHN-9122334455', type: 'High Risk' },
                { id: 'PAN-ABCDE1234F', type: 'Investigate' }
            ]
        },
        selectedTxn: 'RX-9921',
        isScrubberPlaying: true,
        scrubberProgress: 75
    };

    // -------------------------------------------------------------------------
    // 2. DOM ELEMENT REFERENCES
    // -------------------------------------------------------------------------
    const el = {
        viewLogin: document.getElementById('view-login'),
        viewApp: document.getElementById('view-app'),
        loginForm: document.getElementById('loginForm'),
        demoBtn: document.getElementById('demoBtn'),
        logoutBtn: document.getElementById('logoutBtn'),
        mfaToggle: document.getElementById('mfaToggle'),
        togglePassword: document.getElementById('togglePassword'),
        passwordInput: document.getElementById('password'),
        
        sidebarNav: document.getElementById('sidebar-nav'),
        sidebarLinks: document.querySelectorAll('.sidebar-link'),
        topNavTitle: document.getElementById('top-nav-title'),
        topSearchInput: document.getElementById('top-search-input'),
        
        toast: document.getElementById('alert-toast'),
        toastMsg: document.getElementById('toast-message'),
        toastIcon: document.getElementById('toast-icon'),
        
        // Settings page inputs
        sensRange: document.getElementById('range-sensitivity'),
        sensVal: document.getElementById('sens-val'),
        devRange: document.getElementById('range-deviation'),
        devVal: document.getElementById('dev-val'),
        generateApiKeyBtn: document.getElementById('generateApiKeyBtn'),
        apiKeysList: document.getElementById('apiKeysList'),
        simToggle: document.getElementById('sim-toggle'),
        runSimBtn: document.getElementById('run-sim-btn'),
        simMuleNodes: document.getElementById('sim-mule-nodes'),
        simSuccessRate: document.getElementById('sim-success-rate'),
        resetConfigBtn: document.getElementById('resetConfigBtn'),
        saveConfigBtn: document.getElementById('saveConfigBtn'),
        
        // Feeds
        systemRiskScore: document.getElementById('system-risk-score'),
        riskBar: document.getElementById('risk-bar'),
        aiInsight: document.getElementById('ai-insight'),
        simIdInput: document.getElementById('sim-id'),
        simulateIdBtn: document.getElementById('simulateIdBtn'),
        blacklistList: document.getElementById('blacklist-list'),
        deployBlocklistBtn: document.getElementById('deployBlocklistBtn'),
        feedsManualSyncBtn: document.getElementById('feedsManualSyncBtn'),
        feedContainer: document.getElementById('feed-container'),
        
        // Heatmap
        heatmapGrid: document.getElementById('heatmapGrid'),
        
        // Scrubber
        scrubberPlayBtn: document.getElementById('scrubberPlayBtn'),
        scrubberProgress: document.getElementById('scrubber-progress'),
        scrubberPin: document.getElementById('scrubber-pin'),
        muleLiveStatus: document.getElementById('mule-live-status'),
        svgNodesCluster: document.getElementById('svgNodesCluster'),
        freezeClusterBtn: document.getElementById('freezeClusterBtn'),
        openClusterCaseBtn: document.getElementById('openClusterCaseBtn'),
        floatingSignalFeed: document.getElementById('floatingSignalFeed'),
        liveFeedToggle: document.getElementById('liveFeedToggle'),
        liveFeedToast: document.getElementById('liveFeedToast'),
        
        // Transactions
        transactionTableRows: document.querySelectorAll('#transactionTableBody tr'),
        drawerTxnTitle: document.getElementById('drawer-txn-title'),
        drawerRiskScore: document.getElementById('drawer-risk-score'),
        drawerConfidence: document.getElementById('drawer-confidence'),
        drawerLatency: document.getElementById('drawer-latency'),
        drawerTimelineOrigin: document.getElementById('drawer-timeline-origin'),
        drawerRiskBadge: document.getElementById('drawer-risk-badge'),
        drawerGaugeCircle: document.getElementById('drawer-gauge-circle'),
        blockTxnBtn: document.getElementById('blockTxnBtn'),
        verifyTxnBtn: document.getElementById('verifyTxnBtn'),
        
        // Recalibrate
        recalibrateBtn: document.getElementById('recalibrateBtn'),
        
        // Cases
        caseNotesInput: document.getElementById('caseNotesInput'),
        saveCaseNoteBtn: document.getElementById('saveCaseNoteBtn'),
        caseActivityLog: document.getElementById('caseActivityLog'),
        freezeSubjectAccountsBtn: document.getElementById('freezeSubjectAccountsBtn'),
        closeCaseArchiveBtn: document.getElementById('closeCaseArchiveBtn')
    };

    // -------------------------------------------------------------------------
    // 3. TOAST SYSTEM
    // -------------------------------------------------------------------------
    function showToast(message, type = 'success') {
        el.toastMsg.innerText = message;
        el.toastIcon.innerText = type === 'success' ? 'check_circle' : 'warning';
        
        // Remove toast classes
        el.toast.classList.remove('translate-y-20', 'opacity-0');
        el.toast.classList.add('translate-y-0', 'opacity-100');
        
        setTimeout(() => {
            el.toast.classList.remove('translate-y-0', 'opacity-100');
            el.toast.classList.add('translate-y-20', 'opacity-0');
        }, 3000);
    }

    // -------------------------------------------------------------------------
    // 4. SPA VIEWS SWITCHER
    // -------------------------------------------------------------------------
    function switchView(viewName) {
        state.activeView = viewName;
        
        // Update Sidebar active classes
        el.sidebarLinks.forEach(link => {
            const linkTarget = link.getAttribute('data-target');
            if (linkTarget === viewName) {
                link.className = 'sidebar-link flex items-center gap-3 px-4 py-2 bg-secondary-container text-on-secondary-container rounded-lg font-bold transition-transform scale-95';
            } else {
                link.className = 'sidebar-link flex items-center gap-3 px-4 py-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-variant/50 transition-colors duration-200 rounded-lg';
            }
        });

        // Hide all canvases and show the current one
        document.querySelectorAll('.canvas-view').forEach(view => {
            view.classList.add('hidden');
        });
        
        const activeCanvas = document.getElementById(`canvas-${viewName}`);
        if (activeCanvas) {
            activeCanvas.classList.remove('hidden');
        }

        // Hide or show floating actions based on page
        if (viewName === 'alerts' || viewName === 'dashboard') {
            el.floatingSignalFeed.classList.remove('hidden');
        } else {
            el.floatingSignalFeed.classList.add('hidden');
        }

        // Update TopNavBar details
        let titleText = '';
        let searchPlaceholder = '';
        
        switch (viewName) {
            case 'dashboard':
                titleText = 'Fraud Intelligence Hub';
                searchPlaceholder = 'Global Entity Search...';
                break;
            case 'transactions':
                titleText = 'Transaction Explorer & Tracing';
                searchPlaceholder = 'Search by Hash, Wallet, or Entity...';
                break;
            case 'risk-engine':
                titleText = 'Risk Engine Intelligence';
                searchPlaceholder = 'Probe transaction ID or entity...';
                break;
            case 'alerts':
                titleText = 'Alert Center';
                searchPlaceholder = 'Search alerts by ID, source...';
                break;
            case 'mule-graph':
                titleText = 'Mule Graph Intelligence';
                searchPlaceholder = 'Search entity, SHA-8, or IP...';
                break;
            case 'explainability':
                titleText = 'Explainability Intelligence';
                searchPlaceholder = 'Search explainability entities...';
                break;
            case 'cases':
                titleText = 'CASE #9942-XJ';
                searchPlaceholder = 'Search case entities, transactions, or SAR IDs...';
                break;
            case 'feeds':
                titleText = 'Regulatory Intelligence Feeds';
                searchPlaceholder = 'Search Intel Feeds...';
                break;
            case 'settings':
                titleText = 'Configuration & Control Center';
                searchPlaceholder = 'Search settings parameters...';
                break;
        }
        
        el.topNavTitle.innerText = titleText;
        el.topSearchInput.setAttribute('placeholder', searchPlaceholder);
    }

    async function fetchDashboardData() {
        try {
            // Fetch alerts count
            const alertsRes = await api.get('/alerts/');
            const alerts = alertsRes.data;
            document.getElementById('stat-alerts').innerText = alerts.length.toLocaleString();
            
            // Fetch suspicious accounts count
            const accountsRes = await api.get('/accounts/');
            const accounts = accountsRes.data;
            document.getElementById('stat-mules').innerText = accounts.length.toLocaleString();

            showToast('Dashboard data synchronized with backend.');
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
            document.getElementById('stat-alerts').innerText = 'ERROR';
        }
    }

    let ws = null;
    function initWebSocket() {
        ws = new WebSocket(WS_BASE_URL);
        ws.onopen = () => {
            console.log('Connected to Rakshak Live Transaction Stream');
        };
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('Live WS Event:', data);
                if (data.type === 'transaction_scored') {
                    handleLiveTransaction(data.payload);
                }
            } catch (e) {
                console.error("Error parsing WS message", e);
            }
        };
        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
        };
        ws.onclose = () => {
            console.log('WebSocket connection closed. Reconnecting...');
            setTimeout(initWebSocket, 5000);
        };
    }

    function handleLiveTransaction(payload) {
        if (!payload || !payload.transaction) return;
        const txId = payload.transaction.id;
        const shortId = txId.substring(0,8).toUpperCase();
        const score = payload.scores ? payload.scores.final_risk_score.toFixed(1) : "N/A";
        const isCritical = payload.scores && payload.scores.final_risk_score > 80;
        
        // 1. Show Toast
        if (el.liveFeedToast) {
            el.liveFeedToast.innerHTML = `
                <div class="flex gap-3">
                    <div class="w-8 h-8 rounded ${isCritical ? 'bg-error/20 text-error' : 'bg-secondary/20 text-secondary'} flex items-center justify-center shrink-0">
                        <span class="material-symbols-outlined text-[16px]">${isCritical ? 'warning' : 'info'}</span>
                    </div>
                    <div>
                        <p class="text-[11px] font-bold text-on-surface">LIVE: TXN ${shortId}</p>
                        <p class="text-[10px] ${isCritical ? 'text-error' : 'text-secondary'}">Risk Score: ${score}</p>
                    </div>
                </div>
            `;
            
            if (el.liveFeedToast.classList.contains('opacity-0')) {
                el.liveFeedToast.classList.remove('opacity-0', 'scale-90', 'translate-y-4', 'pointer-events-none');
                el.liveFeedToast.classList.add('opacity-100', 'scale-100', 'translate-y-0');
                setTimeout(() => {
                    el.liveFeedToast.classList.add('opacity-0', 'scale-90', 'translate-y-4', 'pointer-events-none');
                    el.liveFeedToast.classList.remove('opacity-100', 'scale-100', 'translate-y-0');
                }, 4000);
            }
        }

        // 2. Add to transaction table
        const tbody = document.getElementById('transactionTableBody');
        if (tbody) {
            const tr = document.createElement('tr');
            tr.className = 'hover:bg-surface-variant/30 cursor-pointer transition-all group animate-fade-in';
            tr.setAttribute('data-txn', txId);
            const timeStr = new Date().toISOString().replace('T', ' ').substring(0, 19);
            tr.innerHTML = `
                <td class="px-4 py-3 font-mono text-xs text-on-surface-variant">${shortId}</td>
                <td class="px-4 py-3">
                    <div class="flex flex-col">
                        <span class="text-sm font-bold">Sender: ${payload.transaction.sender_account_id}</span>
                    </div>
                </td>
                <td class="px-4 py-3">
                    <div class="flex flex-col">
                        <span class="text-sm font-bold">Receiver: ${payload.transaction.receiver_account_id}</span>
                    </div>
                </td>
                <td class="px-4 py-3 font-bold text-on-surface">$${payload.transaction.amount}</td>
                <td class="px-4 py-3">
                    <div class="flex items-center gap-2">
                        <div class="w-12 h-1.5 bg-surface-container-highest rounded-full overflow-hidden">
                            <div class="h-full ${isCritical ? 'bg-error' : 'bg-secondary'}" style="width: ${Math.min(100, score)}%"></div>
                        </div>
                        <span class="text-xs font-black ${isCritical ? 'text-error' : 'text-secondary'}">${score}</span>
                    </div>
                </td>
                <td class="px-4 py-3"></td> <!-- Empty chart col -->
                <td class="px-4 py-3 text-[11px] font-medium text-on-surface-variant">${timeStr}</td>
                <td class="px-4 py-3">
                    <span class="px-2 py-0.5 ${isCritical ? 'bg-error/20 text-error' : 'bg-secondary/15 border border-secondary/30 text-secondary'} text-[10px] font-bold rounded uppercase tracking-tighter">${isCritical ? 'Critical' : 'Low'}</span>
                </td>
            `;
            tbody.prepend(tr);

            if (tbody.children.length > 50) tbody.lastElementChild.remove();

            tr.addEventListener('click', () => {
                document.querySelectorAll('#transactionTableBody tr').forEach(r => r.className = 'hover:bg-surface-variant/30 cursor-pointer transition-colors group');
                tr.className = 'hover:bg-surface-variant/30 cursor-pointer transition-colors group bg-surface-container-highest/20 ring-1 ring-inset ring-primary/30';
                
                if (el.drawerTxnTitle) {
                    el.drawerTxnTitle.innerText = 'TXN: #' + shortId;
                    el.drawerRiskScore.innerText = score;
                    el.drawerConfidence.innerText = 'Live Stream';
                    el.drawerLatency.innerText = 'Real-time';
                    el.drawerTimelineOrigin.innerText = 'WebSocket Event';
                    el.drawerRiskBadge.innerText = isCritical ? 'Critical' : 'Low';
                    el.drawerGaugeCircle.setAttribute('stroke-dashoffset', isCritical ? 20 : 200);
                    
                    if (isCritical) {
                        el.drawerRiskBadge.className = 'px-2 py-0.5 bg-error/20 text-error text-[10px] font-black rounded uppercase';
                        el.drawerGaugeCircle.setAttribute('class', 'text-error');
                    } else {
                        el.drawerRiskBadge.className = 'px-2 py-0.5 bg-secondary/20 text-secondary text-[10px] font-black rounded uppercase';
                        el.drawerGaugeCircle.setAttribute('class', 'text-secondary');
                    }
                }
                showToast(`Loaded details for Transaction: ${txId}`);
            });
        }
    }

    // Attach sidebar navigation listeners
    el.sidebarLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const target = link.getAttribute('data-target');
            switchView(target);
        });
    });

    // -------------------------------------------------------------------------
    // 5. LOGIN FLOW SIMULATION
    // -------------------------------------------------------------------------
    el.loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const btn = this.querySelector('button[type="submit"]');
        const originalContent = btn.innerHTML;
        
        btn.disabled = true;
        btn.innerHTML = `
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Verifying Session...</span>
        `;
        
        setTimeout(() => {
            btn.innerHTML = `<span class="material-symbols-outlined">check_circle</span> <span>Authorized</span>`;
            btn.classList.remove('bg-primary-container');
            btn.classList.add('bg-secondary-container');
            
            setTimeout(() => {
                state.isAuthenticated = true;
                el.viewLogin.classList.add('hidden');
                el.viewApp.classList.remove('hidden');
                showToast('Identity Confirmed. Secure session initialized on SG-7-DELTA.');
                
                // Reset form button
                btn.innerHTML = originalContent;
                btn.disabled = false;
                btn.classList.add('bg-primary-container');
                btn.classList.remove('bg-secondary-container');
                
                // Initialize modules
                switchView('dashboard');
                generateHeatmap();
                fetchDashboardData();
                initWebSocket();
            }, 1000);
        }, 1500);
    });

    el.demoBtn.addEventListener('click', () => {
        state.isAuthenticated = true;
        el.viewLogin.classList.add('hidden');
        el.viewApp.classList.remove('hidden');
        showToast('Accessing restricted demo sandbox.');
        switchView('dashboard');
        generateHeatmap();
    });

    el.logoutBtn.addEventListener('click', (e) => {
        e.preventDefault();
        state.isAuthenticated = false;
        el.viewApp.classList.add('hidden');
        el.viewLogin.classList.remove('hidden');
        showToast('Secure session disconnected successfully.');
    });

    el.togglePassword.addEventListener('click', () => {
        const type = el.passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        el.passwordInput.setAttribute('type', type);
        el.togglePassword.querySelector('span').innerText = type === 'password' ? 'visibility' : 'visibility_off';
    });

    // -------------------------------------------------------------------------
    // 6. SYSTEM SETTINGS PROTOCOLS
    // -------------------------------------------------------------------------
    el.sensRange.addEventListener('input', (e) => {
        state.settings.sensitivity = e.target.value;
        el.sensVal.innerText = `${state.settings.sensitivity}%`;
        
        // Dynamically update stats if sensitivity increases
        if (state.settings.sensitivity > 85) {
            document.getElementById('stat-alerts').innerText = "1,312";
            document.getElementById('stat-alerts').classList.add('text-error');
        } else {
            document.getElementById('stat-alerts').innerText = "1,284";
            document.getElementById('stat-alerts').classList.remove('text-error');
        }
    });

    el.devRange.addEventListener('input', (e) => {
        state.settings.deviationLimit = (e.target.value / 10).toFixed(1);
        el.devVal.innerText = `${state.settings.deviationLimit} σ`;
    });

    // Simulation toggle logic
    el.simToggle.addEventListener('change', () => {
        state.settings.simEnabled = el.simToggle.checked;
        if (state.settings.simEnabled) {
            el.runSimBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            el.runSimBtn.classList.add('animate-pulse');
            el.runSimBtn.disabled = false;
        } else {
            el.runSimBtn.classList.add('opacity-50', 'cursor-not-allowed');
            el.runSimBtn.classList.remove('animate-pulse');
            el.runSimBtn.disabled = true;
        }
    });

    el.runSimBtn.addEventListener('click', async () => {
        if (!state.settings.simEnabled) return;
        
        el.runSimBtn.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Initializing Matrix...';
        el.runSimBtn.classList.remove('bg-tertiary', 'text-on-tertiary');
        el.runSimBtn.classList.add('bg-secondary-container', 'text-on-secondary-container');
        
        try {
            await api.post('/simulate/start');
            showToast('Rakshak Simulation Environment: Coordinated Mule Attack Deployed.', 'warning');
        } catch (error) {
            console.error('Failed to start simulation', error);
            showToast('Failed to start simulation.', 'error');
        } finally {
            el.runSimBtn.innerHTML = '<span class="material-symbols-outlined">play_circle</span> Initialize Simulation Run';
            el.runSimBtn.classList.add('bg-tertiary', 'text-on-tertiary');
            el.runSimBtn.classList.remove('bg-secondary-container', 'text-on-secondary-container');
        }
    });

    // API Key Generation
    el.generateApiKeyBtn.addEventListener('click', () => {
        const id = Math.random().toString(36).substring(2, 6).toLowerCase();
        const keyDiv = document.createElement('div');
        keyDiv.className = 'bg-surface-container-lowest/50 border border-outline-variant/20 rounded-lg p-4 flex items-center justify-between animate-fade-in';
        keyDiv.innerHTML = `
            <div class="flex items-center gap-4">
                <div class="p-2 bg-surface-container-highest rounded-lg">
                    <span class="material-symbols-outlined text-on-surface-variant">key</span>
                </div>
                <div>
                    <p class="font-label-medium text-on-surface">Dynamic_Agent_Session_${id}</p>
                    <code class="text-caption text-secondary/70">rk_live_••••••••••••••••${id}a3</code>
                </div>
            </div>
            <div class="flex items-center gap-2">
                <span class="text-caption text-on-surface-variant mr-2">Created Just Now</span>
                <button class="p-1.5 hover:bg-surface-variant rounded transition-colors"><span class="material-symbols-outlined text-[18px]">content_copy</span></button>
                <button class="p-1.5 hover:bg-error/20 hover:text-error rounded transition-colors" onclick="this.closest('.bg-surface-container-lowest').remove();"><span class="material-symbols-outlined text-[18px]">delete</span></button>
            </div>
        `;
        el.apiKeysList.prepend(keyDiv);
        showToast('Created new Production API Session key.');
    });

    el.saveConfigBtn.addEventListener('click', () => {
        showToast('Enterprise configurations pushed to edge routers.');
    });
    
    el.resetConfigBtn.addEventListener('click', () => {
        el.sensRange.value = 84;
        state.settings.sensitivity = 84;
        el.sensVal.innerText = '84%';
        el.devRange.value = 24;
        state.settings.deviationLimit = 2.4;
        el.devVal.innerText = '2.4 σ';
        showToast('Config limits reset to system defaults.');
    });

    // -------------------------------------------------------------------------
    // 7. FEEDS & BLACKLIST SIMULATOR
    // -------------------------------------------------------------------------
    const aiInsights = [
        "Adjusting risk scores for 1,248 accounts based on NCRP injection...",
        "CERT-IN cyber alert correlated with high-frequency login attempts. Escalating 12 cases.",
        "Cross-referencing new RBI guidelines with current merchant profiles. 14% non-compliance detected.",
        "Phishing campaign 'Deep Blue' signature detected in current transaction stream.",
        "Autonomous block initiated for 5 high-velocity withdrawal requests."
    ];

    const feedTemplates = [
        { source: 'RBI', icon: 'account_balance', color: 'blue', title: 'New Payment Gateway Regulations', text: 'Stricter 2FA requirements for transactions over INR 2L.' },
        { source: 'CERT-IN', icon: 'security', color: 'error', title: 'Ransomware Campaign Detected', text: 'New strain "R-Alpha" targeting banking backend infrastructure.' },
        { source: 'NCRP', icon: 'policy', color: 'yellow', title: 'Batch Blacklist ID: N821', text: '42 UPI IDs linked to regional crypto-mule network added.' },
        { source: 'CERT-IN', icon: 'warning', color: 'error', title: 'Phishing Domain Spree', text: '412 domain names identified spoofing government tax portals.' }
    ];

    function updateRiskDashboard() {
        el.systemRiskScore.innerText = state.feeds.globalSystemRisk.toFixed(1);
        el.riskBar.style.width = `${state.feeds.globalSystemRisk}%`;
        
        if (state.feeds.globalSystemRisk > 80) {
            el.riskBar.className = 'h-full bg-error transition-all duration-1000 ease-out';
            el.systemRiskScore.className = 'text-page-heading font-black text-error';
        } else {
            el.riskBar.className = 'h-full bg-primary transition-all duration-1000 ease-out';
            el.systemRiskScore.className = 'text-page-heading font-black text-primary';
        }
        
        el.aiInsight.innerText = aiInsights[Math.floor(Math.random() * aiInsights.length)];
    }

    el.simulateIdBtn.addEventListener('click', () => {
        const id = el.simIdInput.value.trim();
        if (!id) return;
        
        const item = document.createElement('div');
        item.className = 'flex items-center justify-between py-1 border-b border-outline-variant/10 animate-pulse';
        item.innerHTML = `
            <span class="text-xs font-mono text-on-surface">${id}</span>
            <span class="text-[10px] bg-primary/15 text-primary px-1.5 rounded uppercase font-bold">Manual Block</span>
        `;
        el.blacklistList.prepend(item);
        el.simIdInput.value = '';
        
        // Spike system risk slightly
        state.feeds.globalSystemRisk = Math.min(100, state.feeds.globalSystemRisk + 4.5);
        updateRiskDashboard();
        showToast(`Simulated blacklist injection on target: ${id}`);
    });

    el.deployBlocklistBtn.addEventListener('click', () => {
        showToast('Global blocklist synchronised across nodes.');
    });

    el.feedsManualSyncBtn.addEventListener('click', () => {
        el.feedsManualSyncBtn.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Syncing';
        setTimeout(() => {
            el.feedsManualSyncBtn.innerHTML = '<span class="material-symbols-outlined">bolt</span> Manual Sync';
            showToast('Regulatory registries pulled successfully.');
            addFeedItem();
        }, 1200);
    });

    function addFeedItem() {
        const template = feedTemplates[Math.floor(Math.random() * feedTemplates.length)];
        const time = new Date().toLocaleTimeString([], { hour12: false });
        const div = document.createElement('div');
        div.className = 'p-4 rounded-lg bg-surface-container-highest/40 border border-outline-variant/20 flex gap-4 items-start transition-all hover:bg-surface-container-highest/60 opacity-0 transform -translate-y-4';
        div.style.transition = 'all 0.5s ease-out';
        
        let colorClass = 'text-primary bg-primary/10';
        if (template.color === 'error') colorClass = 'text-error bg-error/10';
        if (template.color === 'yellow') colorClass = 'text-tertiary bg-tertiary/10';
        
        div.innerHTML = `
            <div class="w-10 h-10 rounded flex items-center justify-center shrink-0 ${colorClass}">
                <span class="material-symbols-outlined">${template.icon}</span>
            </div>
            <div class="flex-1">
                <div class="flex justify-between items-start">
                    <span class="text-[11px] font-bold uppercase tracking-wider ${template.color === 'error' ? 'text-error' : 'text-primary'}">${template.source} Update</span>
                    <span class="text-[10px] text-on-surface-variant font-medium">${time}</span>
                </div>
                <h4 class="text-body-data font-bold mt-0.5">${template.title}</h4>
                <p class="text-caption text-on-surface-variant mt-1">${template.text}</p>
                <div class="mt-2 flex gap-2">
                    <span class="px-2 py-0.5 rounded-full bg-surface-variant text-on-surface-variant text-[10px] font-bold">Auto-Sync</span>
                </div>
            </div>
        `;
        
        el.feedContainer.prepend(div);
        setTimeout(() => {
            div.classList.remove('opacity-0', '-translate-y-4');
        }, 50);
        
        if (el.feedContainer.children.length > 8) {
            el.feedContainer.removeChild(el.feedContainer.lastChild);
        }
    }

    // Auto feeds updates
    setInterval(() => {
        if (state.isAuthenticated && state.activeView === 'feeds') {
            addFeedItem();
        }
    }, 12000);

    // -------------------------------------------------------------------------
    // 8. HEATMAP GENERATION
    // -------------------------------------------------------------------------
    function generateHeatmap() {
        if (!el.heatmapGrid) return;
        el.heatmapGrid.innerHTML = '';
        
        const intensities = [
            'bg-surface-variant/30', 
            'bg-primary-container/20',
            'bg-primary-container/40', 
            'bg-secondary/60', 
            'bg-error/80'
        ];
        
        for (let i = 0; i < 64; i++) {
            const rand = Math.floor(Math.random() * intensities.length);
            const cell = document.createElement('div');
            cell.className = `w-full h-full rounded-sm ${intensities[rand]} hover:ring-1 ring-on-surface cursor-crosshair transition-all`;
            el.heatmapGrid.appendChild(cell);
        }
    }

    // -------------------------------------------------------------------------
    // 9. MULE GRAPH INTELLIGENCE & SCRUBBER
    // -------------------------------------------------------------------------
    let scrubberInterval = null;
    
    function updateScrubber() {
        el.scrubberProgress.style.width = `${state.scrubberProgress}%`;
        el.scrubberPin.style.left = `${state.scrubberProgress}%`;
        
        if (state.scrubberProgress >= 100) {
            state.scrubberProgress = 0;
        }
    }

    el.scrubberPlayBtn.addEventListener('click', () => {
        state.isScrubberPlaying = !state.isScrubberPlaying;
        if (state.isScrubberPlaying) {
            el.scrubberPlayBtn.querySelector('span').innerText = 'pause_circle';
            el.muleLiveStatus.innerText = 'LIVE MONITORING';
            el.muleLiveStatus.className = 'text-caption font-caption text-primary font-bold uppercase tracking-tighter';
            startScrubber();
        } else {
            el.scrubberPlayBtn.querySelector('span').innerText = 'play_circle';
            el.muleLiveStatus.innerText = 'PAUSED';
            el.muleLiveStatus.className = 'text-caption font-caption text-on-surface-variant font-bold uppercase tracking-tighter';
            clearInterval(scrubberInterval);
        }
    });

    function startScrubber() {
        clearInterval(scrubberInterval);
        scrubberInterval = setInterval(() => {
            state.scrubberProgress += 0.5;
            updateScrubber();
        }, 100);
    }
    
    startScrubber();

    // SVG node clicks updates Cluster details
    if (el.svgNodesCluster) {
        el.svgNodesCluster.querySelectorAll('circle').forEach(node => {
            node.addEventListener('click', () => {
                const id = node.getAttribute('data-id');
                const title = document.querySelector('.font-card-title.text-on-surface');
                if (id === 'ACC-MAIN') {
                    showToast('Selected Core Target Node: Vikram V.');
                } else {
                    showToast(`Selected Suspicious Mule Node: ${id}`);
                }
            });
        });
    }

    el.freezeClusterBtn.addEventListener('click', () => {
        showToast('Enforcing freezing protocol. 14 node assets restricted.', 'warning');
    });

    el.openClusterCaseBtn.addEventListener('click', () => {
        showToast('Opening new investigation case worksheet.');
        switchView('cases');
    });

    // Floating signals
    el.liveFeedToggle.addEventListener('click', () => {
        const isHidden = el.liveFeedToast.classList.contains('opacity-0');
        if (isHidden) {
            el.liveFeedToast.classList.remove('opacity-0', 'scale-90', 'translate-y-4', 'pointer-events-none');
            el.liveFeedToast.classList.add('opacity-100', 'scale-100', 'translate-y-0');
        } else {
            el.liveFeedToast.classList.add('opacity-0', 'scale-90', 'translate-y-4', 'pointer-events-none');
            el.liveFeedToast.classList.remove('opacity-100', 'scale-100', 'translate-y-0');
        }
    });

    // -------------------------------------------------------------------------
    // 10. TRANSACTION VIEWS & DRAWER DETAILS
    // -------------------------------------------------------------------------
    const txnData = {
        'RX-9921': {
            title: 'TXN: #RX-9921',
            score: '94.2',
            confidence: '99.8%',
            latency: '42ms',
            origin: 'Moscow Cluster • 14:22:01',
            badge: 'Critical',
            gaugeOffset: 15
        },
        'RX-9844': {
            title: 'TXN: #RX-9844',
            score: '12.5',
            confidence: '95.1%',
            latency: '14ms',
            origin: 'Berlin Cluster • 14:18:45',
            badge: 'Low',
            gaugeOffset: 220
        },
        'RX-9730': {
            title: 'TXN: #RX-9730',
            score: '88.9',
            confidence: '98.3%',
            latency: '36ms',
            origin: 'Tor Gateway • 14:05:12',
            badge: 'Critical',
            gaugeOffset: 28
        }
    };

    el.transactionTableRows.forEach(row => {
        row.addEventListener('click', () => {
            // Remove ring active class from all rows
            el.transactionTableRows.forEach(r => r.className = 'hover:bg-surface-variant/30 cursor-pointer transition-colors group');
            row.className = 'hover:bg-surface-variant/30 cursor-pointer transition-colors group bg-surface-container-highest/20 ring-1 ring-inset ring-primary/30';
            
            const txnId = row.getAttribute('data-txn');
            const data = txnData[txnId];
            
            if (data) {
                el.drawerTxnTitle.innerText = data.title;
                el.drawerRiskScore.innerText = data.score;
                el.drawerConfidence.innerText = data.confidence;
                el.drawerLatency.innerText = data.latency;
                el.drawerTimelineOrigin.innerText = data.origin;
                el.drawerRiskBadge.innerText = data.badge;
                el.drawerGaugeCircle.setAttribute('stroke-dashoffset', data.gaugeOffset);
                
                if (data.badge === 'Critical') {
                    el.drawerRiskBadge.className = 'px-2 py-0.5 bg-error/20 text-error text-[10px] font-black rounded uppercase';
                    el.drawerGaugeCircle.setAttribute('class', 'text-error');
                } else {
                    el.drawerRiskBadge.className = 'px-2 py-0.5 bg-secondary/20 text-secondary text-[10px] font-black rounded uppercase';
                    el.drawerGaugeCircle.setAttribute('class', 'text-secondary');
                }
                
                showToast(`Loaded details for Transaction: ${txnId}`);
            }
        });
    });

    el.blockTxnBtn.addEventListener('click', () => {
        showToast('Alert: Transaction blocked. Dispatched notification to compliance.', 'warning');
    });

    el.verifyTxnBtn.addEventListener('click', () => {
        showToast('Transaction verified and cleared successfully.');
    });

    // Recalibrate button on Risk Engine
    el.recalibrateBtn.addEventListener('click', () => {
        showToast('Initiating full system risk recalibration... Done.');
    });

    // -------------------------------------------------------------------------
    // 11. CASES WORKSPACE ACTIONS
    // -------------------------------------------------------------------------
    el.saveCaseNoteBtn.addEventListener('click', (e) => {
        e.preventDefault();
        const noteText = el.caseNotesInput.value.trim();
        if (!noteText) return;
        
        const logItem = document.createElement('div');
        logItem.className = 'relative pl-8';
        logItem.innerHTML = `
            <div class="absolute left-1.5 top-1.5 w-3 h-3 rounded-full bg-secondary ring-4 ring-secondary/20"></div>
            <div class="text-[11px] font-bold text-on-surface-variant">JUST NOW</div>
            <div class="text-sm font-medium">${noteText}</div>
            <div class="text-[11px] opacity-50 italic">Investigator Vikram Singh</div>
        `;
        el.caseActivityLog.prepend(logItem);
        el.caseNotesInput.value = '';
        showToast('Draft Case Note saved to ledger.');
    });

    el.freezeSubjectAccountsBtn.addEventListener('click', () => {
        showToast('System Override: Subject accounts restricted recursively.', 'warning');
    });

    el.closeCaseArchiveBtn.addEventListener('click', () => {
        showToast('Case closed and pushed to regulatory archive.');
    });

    // Ambient Hover micro-interactions
    document.querySelectorAll('.glass-panel').forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            card.style.setProperty('--mouse-x', `${x}px`);
            card.style.setProperty('--mouse-y', `${y}px`);
        });
    });
});
