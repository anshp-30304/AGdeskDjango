// Some commonly used keycodes
const [VK_0, VK_1, VK_2, VK_3, VK_4, VK_5, VK_6, VK_7, VK_8, VK_9] = [
    48, 49, 50, 51, 52, 53, 54, 55, 56, 57,
];
const [
    VK_NUMPAD0,
    VK_NUMPAD1,
    VK_NUMPAD2,
    VK_NUMPAD3,
    VK_NUMPAD4,
    VK_NUMPAD5,
    VK_NUMPAD6,
    VK_NUMPAD7,
    VK_NUMPAD8,
    VK_NUMPAD9,
] = [96, 97, 98, 99, 100, 101, 102, 103, 104, 105];
const [VK_W, VK_A, VK_S, VK_D] = [87, 65, 83, 68, 38];
const [VK_UP, VK_LEFT, VK_DOWN, VK_RIGHT] = [38, 37, 40, 39];
const [VK_ENTER, VK_ESCAPE, VK_DEL, VK_TAB] = [13, 27, 46, 9];
const [VK_CTRL, VK_SHIFT, VK_ALT, VK_WINDOWS] = [17, 16, 18, 91];

/**
 * InteractiveMap constructor function.
 * Creates an instance of an interactive map.
 *
 * @param {jQuery} selector - The jQuery selector attached to the map container.
 * @param {InteractiveMap.defaultConfig | object} settings - Configuration options for the map (optional).
 * @returns {InteractiveMap, boolean} - An instance of the InteractiveMap.
 */
let InteractiveMap = function (selector, settings = {}) {
    // Try to find the map instance and return it
    if (Object.keys(selector).length === 0) {
        return false;
    }

    for (let i = 0; i < InteractiveMap.instances.length; i++) {
        let obj = InteractiveMap.instances[i];

        if (obj.selector.id === selector[0].id) {
            return obj;
        }
    }

    this.settings = Object.assign({}, {
        // Default view port for the map.
        viewPort: [-20.917574, 142.702789],
        zoomLevel: 6,
        height: "100vh",
        width: "100vw",
        paddingBottom: 0,
        minZoom: 2,
        maxZoom: 19,
        // Base map
        tileUrl: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
        // Enabled widgets for the map.
        widgets: [],
        // Whether to reload map when panned. Will perform any associated layer url requests.
        reloadOnPan: false,
        // Zooms to a feature when it is clicked. Requires the interactive flag set to true.
        zoomToClickedFeature: true,
        layers: [],
    }, settings);

    // Set up some instance settings
    let _this = this;
    this.layers = {};

    // Save the instance
    this.id = InteractiveMap.instances.length;
    this.selector = selector;
    this.selector.css({
        width: _this.settings.width,
        height: _this.settings.height,
        "padding-bottom": _this.settings.paddingBottom,
    });
    // Push this to the singleton
    InteractiveMap.instances.push(this);

    /**
     * Create Leaflet instance
     */
    // Put the instance functions here
    this.map = L.map(this.selector[0].id).setView(
        _this.settings.viewPort,
        _this.settings.zoomLevel
    );

    // Add world map container
    L.tileLayer(_this.settings.tileUrl, {
        maxZoom: _this.settings.maxZoom,
        minZoom: _this.settings.minZoom,
        attribution: _this.settings.attribution
    }).addTo(_this.map);

    /**
     * Creates a feature layer with some JSON and settings. Applies various events for mouse interaction.
     * @param geoJson
     * @param settings
     * @returns {*}
     */
    function createFeatureLayer(geoJson, settings) {
        // Create an icon if passed in
        if (settings.icon) {
            settings.icon = L.icon(settings.icon);
        }

        const {id, feature_name, feature_table} = settings;

        // Create the layer but include the settings supplied from earlier
        const layer = L.geoJSON(geoJson, Object.assign({}, settings, {
            onEachFeature: function (feature, layer){

                // When a feature is clicked, open a table of pre-assigned properties
                let tableHTML = `<table>`;
                feature_table.forEach(property => {
                    tableHTML += `
                        <tr><th>${property}</th><td>${feature.properties[property]}</td></tr>
                    `;
                })
                tableHTML += `</table>`
                layer.bindPopup(tableHTML);

                // TODO: Add a hover tooltip to show the 'feature_name' property
                // Create a tooltip for when mouse is over a feature
                // const hoverMarker = L.marker(layer.getBounds().getCenter(), {
                //     icon: L.divIcon({
                //         html: `<div class="hover-text">${feature.properties[feature_name]}</div>`,
                //         className: 'leaflet-hover-label d-none',
                //         iconSize: null,
                //     }),
                //     interactive: false
                // }).addTo(_this.map);

                // Setup event handlers for each feature
                layer.on({
                    mouseover: function (event) {
                        // _this.dispatchEvent(new CustomEvent("mouseOverFeature", {
                        //     detail: {
                        //         containerPoint: event.containerPoint,
                        //         latlng: event.latlng,
                        //         layerPoint: event.layerPoint,
                        //         event: event.originalEvent,
                        //         target: layer,
                        //     }
                        // }))
                        hoverMarker.getElement().classList.remove('d-none');
                    },
                    mouseout: function (event) {
                        // _this.dispatchEvent(new CustomEvent("mouseOutFeature", {
                        //     detail: {
                        //         containerPoint: event.containerPoint,
                        //         latlng: event.latlng,
                        //         layerPoint: event.layerPoint,
                        //         event: event.originalEvent,
                        //         target: layer,
                        //     }
                        // }))
                        hoverMarker.getElement().classList.add('d-none');
                    },
                    click: function (event) {
                        // _this.dispatchEvent(new CustomEvent("mouseClickFeature", {
                        //     detail: {
                        //         containerPoint: event.containerPoint,
                        //         latlng: event.latlng,
                        //         layerPoint: event.layerPoint,
                        //         event: event.originalEvent,
                        //         target: layer,
                        //     }
                        // }))
                    }
                })
            },
            pointToLayer: function(feature, latlng) {
                return L.marker(latlng, { icon: settings.icon });
            }
        }));

        // Store the layer for re-use
        _this.layers[id] = layer;

        return layer;
    }

    /**
     * Returns standard object used for posting map data
     * @returns {{headers: {"X-CSRFToken": (*|string|jQuery), "Content-Type": string}, method: string, body: string}}
     */
    function getPostInit() {
        // The bounds determine how we show data
        const bounds = _this.map.getBounds();
        const ne = bounds.getNorthEast();
        const sw = bounds.getSouthWest();

        return {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": $("[name=csrfmiddlewaretoken]").val(),
            },
            body: JSON.stringify({
                northEast: {lat: ne.lat, lng: ne.lng},
                southWest: {lat: sw.lat, lng: sw.lng},
            }),
        }
    }

    /**
     * Downloads some GeoJSON from an url.
     * @param config
     * @returns {Promise<*>}
     */
    function getGeoJson(config) {
        const {url} = config;

        return fetch(url, getPostInit())
            .then(response => response.json())
            .then(data => createFeatureLayer(data).addTo(_this.map))
            .catch(error => {
                console.error("Error fetching GeoJSON data:", error);
            });
    }

    /**
     * Loads a layer tree from some config. Requires either an url or treeUrl property
     * @param config
     * @returns {Promise<boolean>}
     */
    function getLayerTree(config) {
        const {treeUrl} = config;

        // Convert incoming json into structure appropriate for the tree widget
        // also add appropriate actions for loading/unloading data from URL
        function convertJsonTree(branch) {
            const {label, children, url} = branch;

            if (children) {
                // Category branch
                return {
                    label: label,
                    children: children.map(child => {
                        return convertJsonTree(child);
                    }),
                    collapsed: true,
                    selectAllCheckbox: true,
                }
            } else {
                // Leaf node reached, add load/unload logic from URL if specified
                const geoJsonLayer = createFeatureLayer(null, branch);

                // Add icons/colour boxes to feature layer

                // If the checkbox is selected (layer is shown) fetch the data for the layer
                geoJsonLayer.on('add', function () {
                    return fetch(url, getPostInit())
                        .then(response => response.json())
                        .then(data => geoJsonLayer.addData(JSON.parse(data)))
                        .catch(error => console.error("Failed to load tree layer:", error));
                });
                geoJsonLayer.on('remove', function () {
                    geoJsonLayer.clearLayers();
                })

                return {
                    label: label,
                    layer: geoJsonLayer,
                }
            }
        }

        // Convert branches and apply additional logic before widget initialized
        function createTreeControl(json) {
            const tree = []
            json.forEach(branch => {
                tree.push(convertJsonTree(branch, undefined))
            });

            // Load tree widget
            if (_this.layerTreeControl) {
                _this.map.removeControl(_this.layerTreeControl);
            }

            // Create the layer tree control
            _this.layerTreeControl = L.control.layers
                .tree(null, tree, {
                    spaceSymbol: " ",
                    closedSymbol: "+",
                    openedSymbol: "-",
                    // collapseAll: 'Collapse all',
                    // expandAll: 'Expand all',
                    collapsed: false,
                    position: "bottomright",
                    labelIsSelector: "both",
                })

            _this.layerTreeControl.addTo(_this.map);

            return true;
        }

        // Loads the actual tree structure
        return fetch(treeUrl, getPostInit())
            .then(response => response.json())
            .then(data => createTreeControl(data))
            .catch(error => {
                console.error("Error fetching Layer Tree:", error);
            });
    }

    /**
     * Loads the layers from the class constructor
     * @returns {Promise<unknown>}
     */
    function loadLayers() {
        // Iterate each layer
        _this.settings.layers.map((layer) => {
            const {url, treeUrl} = layer;

            if (url) {
                getGeoJson(url).then(r => console.log(r));
            } else if (treeUrl) {
                getLayerTree(layer).then(r => console.log(r));
            }
        });
    }

    // Perform initial loading
    loadLayers();
}

/**
 * List of Interactive Maps on the current page.
 * @type {*[]}
 */
InteractiveMap.instances = [];

(function ($) {
    $.fn._interactiveMap = function (selector, config) {
        return new InteractiveMap(selector, config);
    };

    /**
     * Creates/retrieves existing `InteractiveMap` from a jQuery selector.
     * @param {object} settings - Configuration options for the map. See Also: `InteractiveMap.defaultConfig`
     * @returns {InteractiveMap}
     * @constructor
     */
    $.fn.InteractiveMap = function (settings) {
        return $(this)._interactiveMap(this, settings);
    };
})(jQuery);


function generateColourValues(colour, style) {
  if (!colour) {
    return { rgba: "", bgColour: "", bdColour: "", colorBox: "" };
  }

  const rgba = `rgba(${colour[0] * 255}, ${colour[1] * 255}, ${
    colour[2] * 255
  }, ${colour[3]})`;
  const bgColour = `rgba(${colour[0] * 255}, ${colour[1] * 255}, ${
    colour[2] * 255
  }, ${style.fillOpacity})`;
  const bdColour = `rgba(${colour[0] * 255}, ${colour[1] * 255}, ${
    colour[2] * 255
  }, ${style.opacity})`;
  const colorBox = `<span class="leaflet-layertree-color-box" style="background-color: ${bgColour}; border-color: ${bdColour}"></span>`;

  return { rgba, bgColour, bdColour, colorBox };
}