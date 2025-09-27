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
            plot.on('plotly_treemapclick', function(event) {
                if (event.points[0].customdata) {
                    let clickedDepth = event.points[0].customdata[4];
                    var isLeaf = event.points[0].customdata[3];
                    if (isLeaf) {
                        if (clickedDepth > prevDepth) {
                            Plotly.restyle(plot, {'texttemplate': '%{customdata[2]}'});
                        } else {
                            Plotly.restyle(plot, {'texttemplate': '%{customdata[1]}'});
                        }
                    } else {
                        Plotly.restyle(plot, {'texttemplate': '%{customdata[1]}'});
                    }
                    prevDepth = clickedDepth;
                } else {
                    Plotly.restyle(plot, {'texttemplate': '%{customdata[1]}'});
                    prevDepth = 0;
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
