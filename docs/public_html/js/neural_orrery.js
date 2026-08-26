/**
 * ImpressionCore — Interactive 3D Canvas Neural Memory Orrery
 * Visualizes the 5-layer cognitive architecture & Brain-Triad memory systems
 */

class NeuralOrrery {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.width = this.canvas.clientWidth;
    this.height = this.canvas.clientHeight;
    this.nodes = [];
    this.particles = [];
    this.rotationX = 0.35;
    this.rotationY = 0;
    this.mouseX = 0;
    this.mouseY = 0;
    this.targetRotX = 0.35;
    this.targetRotY = 0;
    this.isHovered = false;

    this.init();
  }

  init() {
    this.resize();
    window.addEventListener('resize', () => this.resize());

    // Mouse tilt interaction
    this.canvas.addEventListener('mousemove', (e) => {
      const rect = this.canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) / this.width - 0.5;
      const y = (e.clientY - rect.top) / this.height - 0.5;
      this.targetRotY = x * 0.8;
      this.targetRotX = 0.35 + y * 0.5;
    });

    this.canvas.addEventListener('mouseenter', () => { this.isHovered = true; });
    this.canvas.addEventListener('mouseleave', () => {
      this.isHovered = false;
      this.targetRotX = 0.35;
      this.targetRotY = 0;
    });

    // Create Planetary Knowledge Nodes
    this.nodes = [
      { name: "Left Brain (T=0.1)", radius: 110, angle: 0, speed: 0.008, size: 9, color: "#38bdf8", glow: "#0284c7" },
      { name: "Right Brain (T=0.8)", radius: 110, angle: Math.PI, speed: 0.008, size: 9, color: "#fbbf24", glow: "#f59e0b" },
      { name: "Sensory Cortex (Vision/Audio)", radius: 170, angle: 0.8, speed: 0.005, size: 8, color: "#00f0ff", glow: "#0891b2" },
      { name: "Assembly of Experts (AoE)", radius: 170, angle: 3.8, speed: 0.005, size: 8, color: "#a855f7", glow: "#7c3aed" },
      { name: "Universal Knowledge Store (UKS)", radius: 230, angle: 1.5, speed: 0.003, size: 10, color: "#10b981", glow: "#059669" },
      { name: "Guardian 10-Law Cortex", radius: 230, angle: 4.5, speed: 0.003, size: 8, color: "#ffd700", glow: "#d97706" },
      { name: "Motor Cortex / Twin Avatar", radius: 280, angle: 2.8, speed: 0.002, size: 7, color: "#f43f5e", glow: "#e11d48" }
    ];

    // Background Neural Dust Particles
    for (let i = 0; i < 70; i++) {
      this.particles.push({
        x: (Math.random() - 0.5) * 600,
        y: (Math.random() - 0.5) * 400,
        z: (Math.random() - 0.5) * 600,
        size: Math.random() * 1.8 + 0.5,
        alpha: Math.random() * 0.6 + 0.2
      });
    }

    this.animate();
  }

  resize() {
    this.width = this.canvas.clientWidth;
    this.height = this.canvas.clientHeight;
    this.canvas.width = this.width * window.devicePixelRatio;
    this.canvas.height = this.height * window.devicePixelRatio;
    this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  animate() {
    this.rotationX += (this.targetRotX - this.rotationX) * 0.05;
    this.rotationY += (this.targetRotY - this.rotationY) * 0.05;

    this.ctx.clearRect(0, 0, this.width, this.height);

    const centerX = this.width / 2;
    const centerY = this.height / 2;

    // 1. Draw Background Particles
    this.ctx.fillStyle = "#ffffff";
    this.particles.forEach(p => {
      // 3D rotation projection
      const cosY = Math.cos(this.rotationY);
      const sinY = Math.sin(this.rotationY);
      const cosX = Math.cos(this.rotationX);
      const sinX = Math.sin(this.rotationX);

      let x1 = p.x * cosY - p.z * sinY;
      let z1 = p.z * cosY + p.x * sinY;
      let y1 = p.y * cosX - z1 * sinX;
      let z2 = z1 * cosX + p.y * sinX;

      const scale = 400 / (400 + z2);
      const projX = centerX + x1 * scale;
      const projY = centerY + y1 * scale;

      if (scale > 0) {
        this.ctx.globalAlpha = p.alpha * scale;
        this.ctx.beginPath();
        this.ctx.arc(projX, projY, p.size * scale, 0, Math.PI * 2);
        this.ctx.fill();
      }
    });

    // 2. Draw Orbital Rings
    const orbitRadii = [110, 170, 230, 280];
    orbitRadii.forEach(r => {
      this.ctx.strokeStyle = "rgba(0, 240, 255, 0.12)";
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      for (let a = 0; a <= Math.PI * 2; a += 0.1) {
        const x = r * Math.cos(a);
        const z = r * Math.sin(a);
        const cosY = Math.cos(this.rotationY);
        const sinY = Math.sin(this.rotationY);
        const cosX = Math.cos(this.rotationX);
        const sinX = Math.sin(this.rotationX);

        let x1 = x * cosY - z * sinY;
        let z1 = z * cosY + x * sinY;
        let y1 = -z1 * sinX;
        let z2 = z1 * cosX;

        const scale = 400 / (400 + z2);
        const projX = centerX + x1 * scale;
        const projY = centerY + y1 * scale;

        if (a === 0) this.ctx.moveTo(projX, projY);
        else this.ctx.lineTo(projX, projY);
      }
      this.ctx.closePath();
      this.ctx.stroke();
    });

    // 3. Draw Central Cognitive Sun (Colossus Integrator)
    const sunPulse = 18 + Math.sin(Date.now() * 0.003) * 2.5;
    const gradient = this.ctx.createRadialGradient(centerX, centerY, 2, centerX, centerY, sunPulse * 2.5);
    gradient.addColorStop(0, "#ffffff");
    gradient.addColorStop(0.3, "rgba(0, 240, 255, 0.9)");
    gradient.addColorStop(0.7, "rgba(30, 58, 138, 0.4)");
    gradient.addColorStop(1, "transparent");

    this.ctx.globalAlpha = 1;
    this.ctx.fillStyle = gradient;
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, sunPulse * 2.5, 0, Math.PI * 2);
    this.ctx.fill();

    this.ctx.fillStyle = "#ffffff";
    this.ctx.beginPath();
    this.ctx.arc(centerX, centerY, sunPulse * 0.7, 0, Math.PI * 2);
    this.ctx.fill();

    // Central Sun Label
    this.ctx.fillStyle = "#38bdf8";
    this.ctx.font = "600 11px 'JetBrains Mono', monospace";
    this.ctx.textAlign = "center";
    this.ctx.fillText("COLOSSUS ARBITER", centerX, centerY - 28);

    // 4. Update & Draw Planetary Nodes
    this.nodes.forEach(node => {
      node.angle += node.speed;

      const x = node.radius * Math.cos(node.angle);
      const z = node.radius * Math.sin(node.angle);

      const cosY = Math.cos(this.rotationY);
      const sinY = Math.sin(this.rotationY);
      const cosX = Math.cos(this.rotationX);
      const sinX = Math.sin(this.rotationX);

      let x1 = x * cosY - z * sinY;
      let z1 = z * cosY + x * sinY;
      let y1 = -z1 * sinX;
      let z2 = z1 * cosX;

      const scale = 400 / (400 + z2);
      const projX = centerX + x1 * scale;
      const projY = centerY + y1 * scale;

      // Draw Constellation Ray to Center
      this.ctx.strokeStyle = "rgba(0, 240, 255, 0.15)";
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      this.ctx.moveTo(centerX, centerY);
      this.ctx.lineTo(projX, projY);
      this.ctx.stroke();

      // Node Halo Glow
      const nodeGlow = this.ctx.createRadialGradient(projX, projY, 0, projX, projY, node.size * scale * 2.8);
      nodeGlow.addColorStop(0, node.color);
      nodeGlow.addColorStop(0.5, node.glow);
      nodeGlow.addColorStop(1, "transparent");

      this.ctx.fillStyle = nodeGlow;
      this.ctx.beginPath();
      this.ctx.arc(projX, projY, node.size * scale * 2.8, 0, Math.PI * 2);
      this.ctx.fill();

      // Node Solid Core
      this.ctx.fillStyle = "#ffffff";
      this.ctx.beginPath();
      this.ctx.arc(projX, projY, node.size * scale * 0.6, 0, Math.PI * 2);
      this.ctx.fill();

      // Node Label
      this.ctx.fillStyle = node.color;
      this.ctx.font = "500 10px 'JetBrains Mono', monospace";
      this.ctx.fillText(node.name, projX, projY + node.size * scale + 14);
    });

    requestAnimationFrame(() => this.animate());
  }
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('orreryCanvas')) {
    new NeuralOrrery('orreryCanvas');
  }
});
