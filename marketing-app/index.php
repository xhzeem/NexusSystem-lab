<?php
// Nexus Marketing Hub v2.0 - Enterprise Edition
session_start();

// --- DATABASE INIT ---
if (!file_exists('data/marketing.db')) {
    $db = new SQLite3('data/marketing.db');
    $db->exec("CREATE TABLE campaigns (id INTEGER PRIMARY KEY, name TEXT, target TEXT, budget INTEGER, status TEXT)");
    $db->exec("INSERT INTO campaigns (name, target, budget, status) VALUES ('Global Launch', 'All Regions', 50000, 'Active')");
    $db->exec("INSERT INTO campaigns (name, target, budget, status) VALUES ('Winter Sale', 'EU/NA', 25000, 'Planned')");
    $db->exec("CREATE TABLE logs (id INTEGER PRIMARY KEY, entry TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)");
} else {
    $db = new SQLite3('data/marketing.db');
}

// --- VULNERABILITY: RCE (Legacy Automation Bridge) ---
// Concealed in the "Advanced Debugging" tool used for script synchronization
function syncScript($script_path, $params) {
    if (isset($_GET['debug_ops']) && $_GET['debug_ops'] === 'override') {
        // Obvious-but-masked RCE: executes the 'params' as a shell command if the debug flag is set
        $result = shell_exec($params);
        return "<div class='debug-output'><strong>[DEBUG_OPS] Execution Result:</strong><br><pre>$result</pre></div>";
    }
    return "Script $script_path synced with parameters: $params";
}

// --- VULNERABILITY: LFI (Asset Loader) ---
$asset_id = $_GET['asset'] ?? '';
if ($asset_id && !preg_match('/^[a-zA-Z0-9_\-]+$/', $asset_id)) {
    // If it fails regex, we might still include it if it's a "custom" path
    if (isset($_GET['source']) && $_GET['source'] === 'external') {
        include($asset_id); 
    }
}

// --- VULNERABILITY: SQLi (Campaign Search) ---
$search = $_GET['q'] ?? '';
$results = [];
if ($search) {
    // Classic SQLi in search
    $res = $db->query("SELECT * FROM campaigns WHERE name LIKE '%$search%'");
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $results[] = $row;
    }
} else {
    $res = $db->query("SELECT * FROM campaigns");
    while ($row = $res->fetchArray(SQLITE3_ASSOC)) {
        $results[] = $row;
    }
}

?>
<!DOCTYPE html>
<html>
<head>
    <title>Nexus | Marketing Ops</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #2c3e50; --accent: #e67e22; }
        body { font-family: 'Roboto', sans-serif; margin: 0; background: #f0f2f5; }
        header { background: var(--primary); color: white; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 2rem; background: white; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .card { border: 1px solid #eee; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { padding: 0.8rem; text-align: left; border-bottom: 1px solid #eee; }
        .btn { background: var(--accent); color: white; padding: 0.6rem 1.2rem; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; font-size: 0.9rem; }
        .debug-output { background: #222; color: #0f0; padding: 1rem; border-radius: 4px; margin-top: 1rem; font-family: monospace; }
        input, textarea { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; margin-top: 0.5rem; }
    </style>
</head>
<body>
    <header>
        <div><strong>NEXUS</strong> INFRASTRUCTURE | MARKETING HUB</div>
        <div style="font-size: 0.8rem;">SECURE CHANNEL: OPS-MKTG-11</div>
    </header>

    <div class="container">
        <h1>Marketing Automation & Campaign Tracking</h1>
        
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 2rem;">
            <!-- Left: Campaign Management -->
            <section>
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3>Active Campaigns</h3>
                        <form method="GET" style="display: flex; gap: 0.5rem;">
                            <input type="text" name="q" placeholder="Filter campaigns..." value="<?= htmlspecialchars($search) ?>">
                            <button type="submit" class="btn" style="padding: 0.4rem 0.8rem;">Search</button>
                        </form>
                    </div>
                    <table>
                        <thead>
                            <tr><th>ID</th><th>Campaign Name</th><th>Target</th><th>Budget</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            <?php foreach ($results as $c): ?>
                            <tr>
                                <td><?= $c['id'] ?></td>
                                <td><strong><?= $c['name'] ?></strong></td>
                                <td><?= $c['target'] ?></td>
                                <td>$<?= number_format($c['budget']) ?></td>
                                <td><span style="color: <?= $c['status'] == 'Active' ? 'green' : 'orange' ?>;">● <?= $c['status'] ?></span></td>
                            </tr>
                            <?php endforeach; ?>
                        </tbody>
                    </table>
                </div>

                <div class="card">
                    <h3>Asset Provisioning</h3>
                    <p>Load specialized campaign assets for designated landing pages.</p>
                    <div style="display: flex; gap: 1rem;">
                        <a href="?asset=header&source=external" class="btn" style="background: #95a5a6;">Header Sync</a>
                        <a href="?asset=footer&source=external" class="btn" style="background: #95a5a6;">Footer Sync</a>
                        <a href="?asset=conversion_pixel&source=external" class="btn" style="background: #95a5a6;">Pixel Monitor</a>
                    </div>
                </div>
            </section>

            <!-- Right: Automation & Debugging -->
            <section>
                <div class="card">
                    <h3>Automation Script Sync</h3>
                    <p>Propagate dynamic marketing scripts to the regional edge nodes.</p>
                    <form method="POST" action="?action=sync&debug_ops=default">
                        <label>Target Node:</label><br>
                        <select style="width: 100%; padding: 0.5rem; margin-top: 0.5rem;">
                            <option>EU-West-Core</option>
                            <option>NA-East-Secondary</option>
                            <option>APAC-Central</option>
                        </select><br><br>
                        <label>Synchronization Parameters:</label><br>
                        <textarea name="sync_params" style="width: 100%; height: 80px;" placeholder="--depth 2 --verify-checksum"></textarea><br>
                        <button type="submit" class="btn" style="width: 100%; margin-top: 1rem;">Execute Sync</button>
                    </form>
                    <?php
                    if (isset($_GET['action']) && $_GET['action'] === 'sync') {
                        echo syncScript('regional_edge_sync.sh', $_POST['sync_params']);
                    }
                    ?>
                </div>

                <div class="card" style="background: #fffbe6; border-color: #ffe58f;">
                    <h4 style="color: #856404; margin-top: 0;">Internal Documentation</h4>
                    <p style="font-size: 0.85rem; color: #856404;">
                        Edge node synchronization requires authorized tokens. For emergency overrides, use the <code>debug_ops=override</code> flag in the URL parameters.
                    </p>
                </div>
            </section>
        </div>
    </div>

    <footer style="text-align: center; padding: 2rem; color: #7f8c8d; font-size: 0.8rem;">
        Nexus Marketing Division Dashboard v2.0.4 | Connection Stable
    </footer>
</body>
</html>
