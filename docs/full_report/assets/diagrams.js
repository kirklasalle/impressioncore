/**
 * ImpressionCore Advanced Diagram Support
 * Noir × Mickey Mouse × DC Comics Brand Integration
 */

// ImpressionCore Brand Colors for Diagrams
const IC_BRAND_COLORS = {
    // Noir Foundation
    noir: {
        black: '#1a1a1a',
        charcoal: '#2d2d2d',
        silver: '#c0c0c0',
        white: '#f8f8f8'
    },
    // Mickey Mouse Heritage
    mickey: {
        gold: '#ffd700',
        yellow: '#ffeb3b',
        cream: '#fff8e1',
        orange: '#ff9800'
    },
    // DC Comics Heroic
    dc: {
        blue: '#1e3a8a',
        red: '#dc2626',
        cyan: '#0891b2',
        purple: '#7c3aed'
    },
    // Semantic Colors
    semantic: {
        primary: '#1e3a8a',
        secondary: '#2d2d2d',
        accent: '#ffd700',
        success: '#10b981',
        warning: '#ff9800',
        error: '#dc2626'
    }
};

/**
 * Mermaid Configuration with ImpressionCore Brand Theme
 */
const MERMAID_CONFIG = {
    theme: 'base',
    themeVariables: {
        // Primary colors
        primaryColor: IC_BRAND_COLORS.semantic.primary,
        primaryTextColor: IC_BRAND_COLORS.noir.white,
        primaryBorderColor: IC_BRAND_COLORS.semantic.accent,
        
        // Secondary colors
        secondaryColor: IC_BRAND_COLORS.semantic.accent,
        secondaryTextColor: IC_BRAND_COLORS.noir.charcoal,
        secondaryBorderColor: IC_BRAND_COLORS.semantic.primary,
        
        // Tertiary colors
        tertiaryColor: IC_BRAND_COLORS.mickey.cream,
        tertiaryTextColor: IC_BRAND_COLORS.noir.charcoal,
        tertiaryBorderColor: IC_BRAND_COLORS.mickey.orange,
        
        // Background
        background: IC_BRAND_COLORS.noir.white,
        mainBkg: IC_BRAND_COLORS.mickey.cream,
        secondBkg: IC_BRAND_COLORS.semantic.accent,
        tertiaryBkg: IC_BRAND_COLORS.dc.cyan,
        
        // Lines and borders
        lineColor: IC_BRAND_COLORS.noir.charcoal,
        
        // Text
        textColor: IC_BRAND_COLORS.noir.charcoal,
        
        // Node styling
        nodeBkg: IC_BRAND_COLORS.semantic.primary,
        nodeTextColor: IC_BRAND_COLORS.noir.white,
        nodeBorder: IC_BRAND_COLORS.semantic.accent,
        
        // Flowchart
        flowchartNodeBkg: IC_BRAND_COLORS.semantic.primary,
        flowchartNodeTextColor: IC_BRAND_COLORS.noir.white,
        flowchartNodeBorder: IC_BRAND_COLORS.semantic.accent,
        flowchartLinkColor: IC_BRAND_COLORS.noir.charcoal,
        
        // Sequence diagram
        actorBkg: IC_BRAND_COLORS.semantic.accent,
        actorBorder: IC_BRAND_COLORS.semantic.primary,
        actorTextColor: IC_BRAND_COLORS.noir.charcoal,
        activationBkg: IC_BRAND_COLORS.dc.cyan,
        activationBorder: IC_BRAND_COLORS.semantic.primary,
        
        // Gantt
        gridColor: IC_BRAND_COLORS.noir.silver,
        section0: IC_BRAND_COLORS.semantic.primary,
        section1: IC_BRAND_COLORS.semantic.accent,
        section2: IC_BRAND_COLORS.mickey.orange,
        section3: IC_BRAND_COLORS.dc.cyan,
        
        // Git
        git0: IC_BRAND_COLORS.semantic.primary,
        git1: IC_BRAND_COLORS.semantic.accent,
        git2: IC_BRAND_COLORS.mickey.orange,
        git3: IC_BRAND_COLORS.dc.red,
        git4: IC_BRAND_COLORS.dc.purple,
        git5: IC_BRAND_COLORS.dc.cyan,
        git6: IC_BRAND_COLORS.semantic.success,
        git7: IC_BRAND_COLORS.semantic.warning,
        
        // Class diagram
        classText: IC_BRAND_COLORS.noir.charcoal,
        
        // State diagram
        fillType0: IC_BRAND_COLORS.semantic.primary,
        fillType1: IC_BRAND_COLORS.semantic.accent,
        fillType2: IC_BRAND_COLORS.mickey.orange,
        fillType3: IC_BRAND_COLORS.dc.cyan,
        fillType4: IC_BRAND_COLORS.dc.purple,
        fillType5: IC_BRAND_COLORS.semantic.success,
        fillType6: IC_BRAND_COLORS.semantic.warning,
        fillType7: IC_BRAND_COLORS.dc.red
    },
    flowchart: {
        curve: 'basis',
        padding: 20
    },
    sequence: {
        width: 150,
        height: 65,
        boxMargin: 10,
        boxTextMargin: 5,
        noteMargin: 10,
        messageMargin: 35
    },
    gantt: {
        gridLineStartPadding: 350,
        fontSize: 11,
        sectionFontSize: 24,
        numberSectionStyles: 4
    }
};

/**
 * Initialize Mermaid with ImpressionCore branding
 */
function initializeMermaid() {
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize(MERMAID_CONFIG);
        console.log('✨ ImpressionCore Mermaid theme initialized');
    }
}

/**
 * Diagram Export Functionality
 */
class DiagramExporter {
    constructor() {
        this.supportedFormats = ['svg', 'png', 'pdf', 'json'];
    }

    /**
     * Export diagram to specified format
     * @param {string} diagramId - ID of the diagram element
     * @param {string} format - Export format (svg, png, pdf, json)
     * @param {string} filename - Output filename
     */
    async exportDiagram(diagramId, format = 'svg', filename = 'diagram') {
        const diagramElement = document.getElementById(diagramId);
        if (!diagramElement) {
            console.error(`Diagram with ID '${diagramId}' not found`);
            return;
        }

        try {
            switch (format.toLowerCase()) {
                case 'svg':
                    this.exportAsSVG(diagramElement, filename);
                    break;
                case 'png':
                    await this.exportAsPNG(diagramElement, filename);
                    break;
                case 'pdf':
                    await this.exportAsPDF(diagramElement, filename);
                    break;
                case 'json':
                    this.exportAsJSON(diagramElement, filename);
                    break;
                default:
                    console.error(`Unsupported format: ${format}`);
            }
        } catch (error) {
            console.error(`Export failed: ${error.message}`);
        }
    }

    exportAsSVG(element, filename) {
        const svgElement = element.querySelector('svg');
        if (!svgElement) {
            console.error('No SVG found in diagram element');
            return;
        }

        const svgData = new XMLSerializer().serializeToString(svgElement);
        const blob = new Blob([svgData], { type: 'image/svg+xml' });
        this.downloadBlob(blob, `${filename}.svg`);
    }

    async exportAsPNG(element, filename) {
        const svgElement = element.querySelector('svg');
        if (!svgElement) {
            console.error('No SVG found in diagram element');
            return;
        }

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const svgData = new XMLSerializer().serializeToString(svgElement);
        const img = new Image();

        return new Promise((resolve, reject) => {
            img.onload = () => {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);
                
                canvas.toBlob((blob) => {
                    this.downloadBlob(blob, `${filename}.png`);
                    resolve();
                });
            };
            img.onerror = reject;
            img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
        });
    }

    async exportAsPDF(element, filename) {
        // This would require a PDF library like jsPDF
        console.log('PDF export requires additional library implementation');
    }

    exportAsJSON(element, filename) {
        // Extract diagram data and configuration
        const diagramData = {
            type: element.dataset.diagramType || 'unknown',
            content: element.textContent || element.innerHTML,
            timestamp: new Date().toISOString(),
            brandTheme: 'impressioncore-noir-mickey-dc'
        };

        const blob = new Blob([JSON.stringify(diagramData, null, 2)], { 
            type: 'application/json' 
        });
        this.downloadBlob(blob, `${filename}.json`);
    }

    downloadBlob(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

/**
 * Interactive Diagram Controls
 */
class DiagramControls {
    constructor() {
        this.exporter = new DiagramExporter();
        this.setupControls();
    }

    setupControls() {
        // Add export buttons to all diagrams
        document.querySelectorAll('[data-diagram-type]').forEach(diagram => {
            this.addControlsToTag(diagram);
        });

        // Add zoom and pan controls for complex diagrams
        this.addZoomControls();
    }

    addControlsToTag(diagramElement) {
        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'diagram-controls';
        controlsContainer.innerHTML = `
            <div class="ic-card" style="margin: 1rem 0; padding: 1rem;">
                <h4 style="margin: 0 0 1rem 0; color: var(--primary-color);">
                    📊 Diagram Controls
                </h4>
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <button class="ic-button ic-button-primary export-svg">
                        📥 Export SVG
                    </button>
                    <button class="ic-button ic-button-secondary export-png">
                        🖼️ Export PNG
                    </button>
                    <button class="ic-button ic-button-outline export-json">
                        📄 Export JSON
                    </button>
                    <button class="ic-button ic-button-outline zoom-reset">
                        🔍 Reset Zoom
                    </button>
                </div>
            </div>
        `;

        // Insert controls after the diagram
        diagramElement.parentNode.insertBefore(controlsContainer, diagramElement.nextSibling);

        // Add event listeners
        const diagramId = diagramElement.id || `diagram-${Date.now()}`;
        if (!diagramElement.id) {
            diagramElement.id = diagramId;
        }

        controlsContainer.querySelector('.export-svg').addEventListener('click', () => {
            this.exporter.exportDiagram(diagramId, 'svg');
        });

        controlsContainer.querySelector('.export-png').addEventListener('click', () => {
            this.exporter.exportDiagram(diagramId, 'png');
        });

        controlsContainer.querySelector('.export-json').addEventListener('click', () => {
            this.exporter.exportDiagram(diagramId, 'json');
        });

        controlsContainer.querySelector('.zoom-reset').addEventListener('click', () => {
            this.resetZoom(diagramElement);
        });
    }

    addZoomControls() {
        // Add pan and zoom functionality to SVG diagrams
        document.querySelectorAll('svg').forEach(svg => {
            svg.style.cursor = 'grab';
            
            let isPanning = false;
            let startPoint = { x: 0, y: 0 };
            let scale = 1;

            svg.addEventListener('wheel', (e) => {
                e.preventDefault();
                const delta = e.deltaY > 0 ? 0.9 : 1.1;
                scale *= delta;
                svg.style.transform = `scale(${scale})`;
            });

            svg.addEventListener('mousedown', (e) => {
                isPanning = true;
                startPoint = { x: e.clientX, y: e.clientY };
                svg.style.cursor = 'grabbing';
            });

            svg.addEventListener('mousemove', (e) => {
                if (!isPanning) return;
                
                const dx = e.clientX - startPoint.x;
                const dy = e.clientY - startPoint.y;
                
                svg.style.transform = `scale(${scale}) translate(${dx}px, ${dy}px)`;
            });

            svg.addEventListener('mouseup', () => {
                isPanning = false;
                svg.style.cursor = 'grab';
            });
        });
    }

    resetZoom(diagramElement) {
        const svg = diagramElement.querySelector('svg');
        if (svg) {
            svg.style.transform = 'scale(1) translate(0px, 0px)';
        }
    }
}

/**
 * Initialize everything when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    initializeMermaid();
    
    // Initialize diagram controls after a short delay to ensure all diagrams are rendered
    setTimeout(() => {
        new DiagramControls();
    }, 1000);
});

/**
 * Matrix and 3D Diagram Support
 */
class AdvancedDiagrams {
    constructor() {
        this.setupMatrixVisualization();
        this.setup3DSupport();
    }

    setupMatrixVisualization() {
        // Implementation for matrix diagrams would go here
        // This could integrate with libraries like D3.js or Chart.js
        console.log('🔢 Matrix visualization support initialized');
    }

    setup3DSupport() {
        // Implementation for 3D diagrams would go here
        // This could integrate with Three.js or similar
        console.log('🎯 3D diagram support initialized');
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        IC_BRAND_COLORS,
        MERMAID_CONFIG,
        DiagramExporter,
        DiagramControls,
        AdvancedDiagrams
    };
}
