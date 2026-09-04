"""
@relation(SDOC-SRS-157, scope=file)
"""

from markupsafe import Markup

PLOTLY_JS_EXTENSION = Markup("""
    window.addEventListener("load", () => {
        var tooltip = document.createElement('div');
        tooltip.id = 'tooltip';
        tooltip.style.position = 'absolute';
        tooltip.style.background = '#ddd';
        tooltip.style.border = '1px solid black';
        tooltip.style.padding = '5px';
        tooltip.style.fontFamily = '"Open Sans", verdana, arial, sans-serif';
        tooltip.style.fontSize = "12px";
        tooltip.style.display = 'none';
        tooltip.style.pointerEvents = 'none';
        tooltip.style.zIndex = 1000;
        document.body.appendChild(tooltip);

        document.querySelectorAll('div.js-plotly-plot').forEach(plot => {
            let prevDepth = 0;
            let currentId = null;

            plot.on('plotly_treemapclick', function(event) {
                const domEvent = event.event;
                const link = domEvent?.target?.closest?.('a');

                // This branch handles the "Open in document" link click.
                if (link) {
                    // Stop the original DOM click from reaching Plotly/container
                    // handlers.
                    domEvent.stopPropagation();
                    domEvent.stopImmediatePropagation?.();

                    return false;
                }

                const point = event.points[0];
                const clickedNodeId = point.id;

                // Controls toggling of leaf nodes between summary and detailed views.
                //
                // `currentId` tracks whether a leaf node is currently in its "zoomed-in"
                // (detailed) state. This is necessary because depth alone is insufficient:
                // when a user zooms out and then back into the same node, the depth may
                // remain unchanged.
                //
                // The condition: clickedDepth > prevDepth handles normal
                // zoom-in transitions.
                //
                // The additional condition: clickedDepth === prevDepth && !currentId
                // handles the case where the same node is re-entered without a depth change,
                // ensuring it switches back to the detailed view.
                if (event.points[0].customdata) {
                    let clickedDepth = event.points[0].customdata[4];
                    var isLeaf = event.points[0].customdata[3];

                    if (isLeaf) {
                        if (
                            clickedDepth > prevDepth ||
                            (clickedDepth === prevDepth && !currentId)
                        ) {
                            Plotly.restyle(plot, {'texttemplate': '%{customdata[2]}'});
                            currentId = clickedNodeId;
                        }
                        else {
                            Plotly.restyle(plot, {'texttemplate': '%{customdata[1]}'});
                            currentId = null;
                        }
                    } else {
                        Plotly.restyle(plot, {'texttemplate': '%{customdata[1]}'});
                        currentId = null;
                    }
                    prevDepth = clickedDepth;
                } else {
                    Plotly.restyle(plot, {'texttemplate': '%{customdata[1]}'});
                    prevDepth = 0;
                    currentId = null;
                }
            });

            plot.on('plotly_hover', function(event) {
                var point = event.points[0];
                if (!point.customdata) return;

                var text = point.customdata[0];

                tooltip.innerHTML = text;
                tooltip.style.left = event.event.clientX + 10 + "px";
                tooltip.style.top = event.event.clientY + 10 + "px";
                tooltip.style.display = "block";
            });

            // Hide tooltip on unhover.
            plot.on('plotly_unhover', function(event) {
                tooltip.style.display = "none";
            });
        });
    });
""")
