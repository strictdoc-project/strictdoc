// stable_uri_forwarder.js
//
// This script is included from the project's index.html page (in static HTML export)
// It checks for a known MID or UID in the #anchor, and then
// redirects to the referenced section or node within the project.
// 
// Example: 
//   http://strictdoc.company.com/#SDOC_UG will redirect to
//   http://strictdoc.company.com/strictdoc/docs/strictdoc_01_user_guide.html#SDOC_UG
//
// Thanks to this mechanism, it becomes possible to export stable links to
// nodes/requirements/sections for integration with external tools.
// The external links remain stable, even if the node/requirement/section is moved
// within the project.


// Resolve the MID / UID to the correct page / anchor using the projectMap.
function resolveStableUriRedirectUsingProjectMap(anchor) {
    const anchorIsMID = /^[a-fA-F0-9]{32}$/.test(anchor);
    for (const [page, nodes] of Object.entries(projectMap)) {
        for (const node of nodes) {
            const nodeHasMID = 'MID' in node && typeof node['MID'] === 'string';
            if ( (anchorIsMID && nodeHasMID && node['MID']?.toLowerCase() === anchor.toLowerCase()) 
                || (node['UID'] === anchor)
            )
            {
                window.location.replace(page + "#" + node['UID']);
                return;
            }
        }        
    }
}

// Dynamically load the projectMap an resolve MID / UID.
function loadProjectMapAndResolveStableUriRedirect(anchor) {
    
    // ProjectMap is loaded, no need to load it again.
    if (typeof projectMap !== 'undefined') {
        resolveStableUriRedirectUsingProjectMap(anchor);
        return;
    }

    // Get script URL and derive from it the url of project_map.js
    const scriptUrl = new URL(document.getElementById("stable_uri_forwarder").src, window.location.href)
    const projectMapUrl = new URL('project_map.js', scriptUrl).href;

    // Dynamically load project map and resolve
    const script = document.createElement("script");
    script.src = projectMapUrl;
    script.onload = () => resolveStableUriRedirectUsingProjectMap(anchor);
    script.onerror = () => {
        console.error(`Failed to load project map from ${projectMapUrl}`);
    };
    document.head.appendChild(script);
}

function processStableUriRedirect(anchor)
{
    const exportType = document.querySelector('meta[name="strictdoc-export-type"]')?.content;

    if (exportType === 'webserver') {
        // For the web server, we let the main_router.py dynamically forward UID to node.
        window.location.replace("/UID/" + anchor);
    } else if (exportType === 'static') {
        // For static exports, we use the project_map.js.
        loadProjectMapAndResolveStableUriRedirect(anchor)
    }
}


// In case an anchor is present at content load time.
document.addEventListener("DOMContentLoaded", () => {
    const anchor = window.location.hash.substring(1);
    if (anchor) {
        processStableUriRedirect(anchor)
    }
});

// In case an anchor is added manually afterwards (eases testing).
window.addEventListener("hashchange", () => {
    const anchor = window.location.hash.substring(1);
    if (anchor) {
        processStableUriRedirect(anchor)
    }
});
